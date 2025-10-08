import os
from pathlib import Path
import time
from typing import Any, Dict, Optional

import toml


class ConfigStore:
    """Simple TOML-backed configuration store for runtime settings."""

    def __init__(self, config_path: Optional[Path] = None):
        # Default to backend/config.toml
        if config_path is None:
            # This file is located at backend/app/core/config_store.py
            # Go up two levels to reach backend/
            backend_dir = Path(__file__).resolve().parents[2]
            config_path = backend_dir / "config.toml"

        self.config_path: Path = config_path
        self._config: Dict[str, Any] = {}
        self._mtime: float = 0.0
        self._load()

    def _default_config(self) -> Dict[str, Any]:
        return {
            "alist": {
                "url": "",
                "token": "",
                "username": "",
                "password": "",
                "upload_path": "/gallery",
            }
        }

    def _load(self) -> None:
        if self.config_path.exists():
            try:
                with self.config_path.open("r", encoding="utf-8") as f:
                    self._config = toml.load(f)
                try:
                    self._mtime = self.config_path.stat().st_mtime
                except Exception:
                    self._mtime = time.time()
            except Exception:
                # Fall back to defaults if file is corrupted
                self._config = self._default_config()
        else:
            # Initialize with defaults and write file
            self._config = self._default_config()
            self._save()

    def _save(self) -> None:
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with self.config_path.open("w", encoding="utf-8") as f:
            toml.dump(self._config, f)
        try:
            self._mtime = self.config_path.stat().st_mtime
        except Exception:
            self._mtime = time.time()

    def reload_if_changed(self) -> bool:
        """Reload the TOML if the file has changed on disk. Returns True if reloaded."""
        try:
            current_mtime = self.config_path.stat().st_mtime
        except Exception:
            return False
        if current_mtime != self._mtime:
            self._load()
            return True
        return False

    def get(self, key: str, default: Any = None) -> Any:
        parts = key.split(".")
        cur: Any = self._config
        for part in parts:
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                return default
        return cur

    def set(self, key: str, value: Any) -> None:
        parts = key.split(".")
        cur = self._config
        for part in parts[:-1]:
            if part not in cur or not isinstance(cur[part], dict):
                cur[part] = {}
            cur = cur[part]
        cur[parts[-1]] = value
        self._save()

    def update_section(self, section: str, values: Dict[str, Any]) -> None:
        if section not in self._config or not isinstance(self._config[section], dict):
            self._config[section] = {}
        self._config[section].update(values)
        self._save()

    def get_section(self, section: str) -> Dict[str, Any]:
        val = self._config.get(section) or {}
        return dict(val)

    def get_all(self) -> Dict[str, Any]:
        return dict(self._config)


# Global singleton instance
config_store = ConfigStore()


