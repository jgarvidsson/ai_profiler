import json
from pathlib import Path
from typing import Any, Optional

class SettingsManager:
    def __init__(self):
        self.config_path = Path(__file__).parent.parent / "data" / "config.json"
        self.settings = self._defaults()
        self._load()

    def _defaults(self) -> dict:
        return {
            "scan_limit": 100,
            "language": "auto",
            "data_sources": {
                "huggingface": {
                    "enabled": True,
                    "api_url": "https://huggingface.co/api/models",
                    "label": "HuggingFace"
                },
                "vramio": {
                    "enabled": True,
                    "api_url": "https://vramio.ksingh.in/model",
                    "label": "VRAM.io"
                },
                "ollama": {
                    "enabled": False,
                    "label": "Ollama (local)"
                }
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split('.')
        val = self.settings
        for k in keys:
            if isinstance(val, dict):
                val = val.get(k)
            else:
                return default
        return val if val is not None else default

    def set(self, key: str, value: Any):
        keys = key.split('.')
        target = self.settings
        for k in keys[:-1]:
            target = target.setdefault(k, {})
        target[keys[-1]] = value
        self._save()

    def get_enabled_sources(self) -> list:
        sources = self.get('data_sources', {})
        return [k for k, v in sources.items() if v.get('enabled', False)]

    def _load(self):
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                merged = self._defaults()
                self._deep_merge(merged, loaded)
                self.settings = merged
            except:
                pass

    def _save(self):
        self.config_path.parent.mkdir(exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, indent=2, ensure_ascii=False)

    def _deep_merge(self, base: dict, override: dict):
        for k, v in override.items():
            if k in base and isinstance(base[k], dict) and isinstance(v, dict):
                self._deep_merge(base[k], v)
            else:
                base[k] = v
