import httpx
import os
from typing import Optional, Dict, Any
from fastapi import UploadFile
from app.core.config import settings


class AlistService:
    def __init__(self):
        self.base_url = settings.ALIST_URL.rstrip('/') if settings.ALIST_URL else None
        self.username = settings.ALIST_USERNAME
        self.password = settings.ALIST_PASSWORD
        self.token = settings.ALIST_TOKEN
        self.upload_path = settings.ALIST_UPLOAD_PATH
        self._is_configured = bool(self.base_url)
        
    async def _get_token(self) -> Optional[str]:
        """Get authentication token from Alist"""
        if not self._is_configured:
            raise ValueError("Alist is not configured. Please set ALIST_URL in environment variables.")
            
        if self.token:
            return self.token
            
        if not self.username or not self.password:
            raise ValueError("Alist credentials not configured")
            
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/auth/login",
                json={
                    "username": self.username,
                    "password": self.password
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("data", {}).get("token")
            else:
                raise Exception(f"Failed to authenticate with Alist: {response.text}")
    
    async def test_connection(self) -> bool:
        """Test connection to Alist"""
        try:
            token = await self._get_token()
            if not token:
                return False
                
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/me",
                    headers={"Authorization": f"Bearer {token}"}
                )
                return response.status_code == 200
        except Exception:
            return False
    
    async def upload_file(self, file: UploadFile, filename: str, subfolder: str = "") -> Dict[str, Any]:
        """Upload file to Alist"""
        token = await self._get_token()
        if not token:
            raise Exception("Failed to get Alist token")
        
        # Prepare file path
        file_path = os.path.join(self.upload_path, subfolder, filename).replace("\\", "/")
        
        # Read file content
        file_content = await file.read()
        
        async with httpx.AsyncClient() as client:
            # First, ensure the directory exists
            dir_path = os.path.dirname(file_path)
            if dir_path != self.upload_path:
                await self._ensure_directory(client, token, dir_path)
            
            # Upload file
            files = {"file": (filename, file_content, file.content_type)}
            data = {
                "file_path": file_path,
                "password": ""
            }
            
            response = await client.post(
                f"{self.base_url}/api/fs/put",
                files=files,
                data=data,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 200:
                    # Get public URL
                    public_url = await self.get_file_url(file_path)
                    return {
                        "success": True,
                        "file_path": file_path,
                        "url": public_url,
                        "size": len(file_content)
                    }
                else:
                    raise Exception(f"Upload failed: {result.get('message', 'Unknown error')}")
            else:
                raise Exception(f"Upload failed: {response.text}")
    
    async def _ensure_directory(self, client: httpx.AsyncClient, token: str, dir_path: str):
        """Ensure directory exists in Alist"""
        response = await client.post(
            f"{self.base_url}/api/fs/mkdir",
            json={
                "path": dir_path,
                "password": ""
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        # Ignore if directory already exists
        if response.status_code not in [200, 409]:
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
            response = await client.post(
                f"{self.base_url}/api/fs/remove",
                json={
                    "path": file_path,
                    "password": ""
                },
                headers={"Authorization": f"Bearer {token}"}
            )
            
            return response.status_code == 200 and response.json().get("code") == 200


# Global instance
alist_service = AlistService()