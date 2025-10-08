import httpx
import os
from typing import Optional, Dict, Any
from fastapi import UploadFile
from app.core.config import settings
from app.core.config_store import config_store


class AlistService:
    def __init__(self):
        # Load initial values from config store, falling back to env-based settings
        stored = config_store.get_section("alist")
        env_url = settings.ALIST_URL
        env_username = settings.ALIST_USERNAME
        env_password = settings.ALIST_PASSWORD
        env_token = settings.ALIST_TOKEN
        env_upload_path = settings.ALIST_UPLOAD_PATH

        self.base_url = (stored.get("url") or env_url or "").rstrip('/') or None
        self.username = stored.get("username") or env_username
        self.password = stored.get("password") or env_password
        self.token = stored.get("token") or env_token
        self.upload_path = stored.get("upload_path") or env_upload_path
        self._is_configured = bool(self.base_url)
        # Debug configuration summary (mask token)
        try:
            masked_token = (self.token[:8] + "...") if self.token else None
            print(
                f"[AList] init url={self.base_url} username={'yes' if self.username else 'no'} token={'yes' if self.token else 'no'} token_preview={masked_token} upload_path={self.upload_path}"
            )
        except Exception:
            pass

    def refresh_from_store(self) -> None:
        """Refresh runtime settings from config_store, always merging non-empty values.
        Also checks for on-disk changes beforehand.
        """
        try:
            config_store.reload_if_changed()
        except Exception:
            pass
        stored = config_store.get_section("alist")
        # Merge non-empty values from store
        url_val = (stored.get("url") or "").strip()
        if url_val:
            self.base_url = url_val.rstrip('/')
        username_val = (stored.get("username") or "").strip()
        if username_val:
            self.username = username_val
        password_val = stored.get("password")
        if isinstance(password_val, str) and password_val != "":
            self.password = password_val
        token_val = (stored.get("token") or "").strip()
        if token_val:
            self.token = token_val
        upload_path_val = (stored.get("upload_path") or "").strip()
        if upload_path_val:
            # Normalize leading slash
            self.upload_path = "/" + upload_path_val.strip("/")
        self._is_configured = bool(self.base_url)
        print(f"[AList] reloaded from config store: url={self.base_url} upload_path={self.upload_path}")
        
    async def _get_token(self) -> Optional[str]:
        """Get authentication token from Alist"""
        # Refresh in case config.toml changed
        self.refresh_from_store()
        if not self._is_configured:
            raise ValueError("Alist is not configured. Please set ALIST_URL in environment variables.")
            
        if self.token:
            print("[AList] using configured token")
            return self.token
            
        if not self.username or not self.password:
            raise ValueError("Alist credentials not configured")
            
        async with httpx.AsyncClient() as client:
            print(f"[AList] login POST {self.base_url}/api/auth/login")
            response = await client.post(
                f"{self.base_url}/api/auth/login",
                json={
                    "username": self.username,
                    "password": self.password,
                    "opt_code": ""
                }
            )
            
            if response.status_code == 200:
                print(f"[AList] login -> {response.text[:200]}")
                data = response.json()
                return data.get("data", {}).get("token")
            else:
                raise Exception(f"Failed to authenticate with Alist: {response.text}")
    
    async def test_connection(self) -> bool:
        """Test connection to Alist"""
        try:
            self.refresh_from_store()
            token = await self._get_token()
            if not token:
                return False
                
            async with httpx.AsyncClient() as client:
                print("[AList] GET /api/me for health check")
                response = await client.get(
                    f"{self.base_url}/api/me",
                    headers={"Authorization": token}
                )
                print(f"[AList] /api/me -> {response.status_code} {response.text[:200]}")
                return response.status_code == 200
        except Exception:
            return False
    
    async def upload_file(self, file: UploadFile, filename: str, subfolder: str = "") -> Dict[str, Any]:
        """Upload file to Alist using PUT API with raw token and File-Path header."""
        # Refresh in case config.toml changed
        self.refresh_from_store()
        token = await self._get_token()
        if not token:
            raise Exception("Failed to get Alist token")

        # Prepare file path
        file_path = os.path.join(self.upload_path, subfolder, filename).replace("\\", "/")

        # Read file content
        file_content = await file.read()

        async with httpx.AsyncClient(timeout=60.0) as client:
            # Ensure directory exists (best-effort)
            dir_path = os.path.dirname(file_path)
            if dir_path and dir_path != self.upload_path:
                try:
                    print(f"[AList] mkdir {dir_path}")
                    await self._ensure_directory(client, token, dir_path)
                except Exception as e:
                    # Non-fatal; continue upload attempt
                    print(f"[AList] mkdir warning: {e}")

            # Use PUT /api/fs/put with raw token and File-Path headers
            headers = {
                "Authorization": token,
                "File-Path": file_path,
                "Content-Type": "application/octet-stream",
                "Accept": "application/json",
            }

            print(f"[AList] PUT /api/fs/put File-Path={file_path} size={len(file_content)}")
            response = await client.put(
                f"{self.base_url}/api/fs/put",
                headers=headers,
                content=file_content,
            )

            # Try to parse JSON response
            try:
                result = response.json()
            except ValueError:
                result = None

            print(f"[AList] PUT result {response.status_code} {response.text[:400]}")
            if response.status_code == 200 and (not result or result.get("code") == 200):
                public_url = await self.get_file_url(file_path)
                return {
                    "success": True,
                    "file_path": file_path,
                    "url": public_url,
                    "size": len(file_content)
                }

            # Handle API error with message
            error_msg = response.text
            if result and "message" in result:
                error_msg = result.get("message")

            # Fallback: some backends can't create directories; try uploading without subfolder
            if isinstance(error_msg, str) and "not support" in error_msg and "make dir" in error_msg:
                print(
                    f"[AList] fallback: retrying upload without subfolder because mkdir is not supported"
                )
                # Optionally prefix filename with subfolder to avoid collisions
                fallback_filename = filename
                if subfolder:
                    fallback_filename = f"{subfolder}_{filename}"
                fallback_file_path = os.path.join(self.upload_path, fallback_filename).replace("\\", "/")
                fallback_headers = {
                    "Authorization": token,
                    "File-Path": fallback_file_path,
                    "Content-Type": "application/octet-stream",
                    "Accept": "application/json",
                }
                print(f"[AList] PUT (fallback) File-Path={fallback_file_path} size={len(file_content)}")
                fallback_resp = await client.put(
                    f"{self.base_url}/api/fs/put",
                    headers=fallback_headers,
                    content=file_content,
                )
                print(f"[AList] PUT (fallback) result {fallback_resp.status_code} {fallback_resp.text[:400]}")
                try:
                    fallback_body = fallback_resp.json()
                except ValueError:
                    fallback_body = None

                if fallback_resp.status_code == 200 and (not fallback_body or fallback_body.get("code") == 200):
                    public_url = await self.get_file_url(fallback_file_path)
                    return {
                        "success": True,
                        "file_path": fallback_file_path,
                        "url": public_url,
                        "size": len(file_content)
                    }

                # If fallback also failed, bubble up the original message
                fb_msg = fallback_resp.text
                if fallback_body and "message" in fallback_body:
                    fb_msg = fallback_body.get("message")
                raise Exception(f"Upload failed (fallback): {fb_msg}")

            raise Exception(f"Upload failed: {error_msg}")
    
    async def _ensure_directory(self, client: httpx.AsyncClient, token: str, dir_path: str):
        """Ensure directory exists in Alist"""
        response = await client.post(
            f"{self.base_url}/api/fs/mkdir",
            json={
                "path": dir_path,
                "password": ""
            },
            headers={"Authorization": token}
        )
        # Ignore if directory already exists
        if response.status_code not in [200, 409]:
            try:
                body = response.json()
                if body.get("code") != 200:
                    raise Exception(f"Failed to create directory: {body.get('message')}")
            except ValueError:
                raise Exception(f"Failed to create directory: {response.text}")
    
    async def get_file_url(self, file_path: str) -> str:
        """Get public URL for a file"""
        # Alist typically serves files at /d/ path
        return f"{self.base_url}/d{file_path}"
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from Alist"""
        token = await self._get_token()
        if not token:
            return False
        
        async with httpx.AsyncClient() as client:
            print(f"[AList] remove {file_path}")
            response = await client.post(
                f"{self.base_url}/api/fs/remove",
                json={
                    "path": file_path,
                    "password": ""
                },
                headers={"Authorization": token}
            )
            print(f"[AList] remove -> {response.status_code} {response.text[:200]}")
            return response.status_code == 200 and response.json().get("code") == 200


# Global instance
alist_service = AlistService()