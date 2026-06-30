import json
import locale
import os
from pathlib import Path
from typing import Optional

class LanguageManager:
    def __init__(self, lang: str = 'auto'):
        if lang == 'auto':
            lang = self.detect_system_language()
        self.lang = lang
        self.strings = {}
        self._load()

    @staticmethod
    def detect_system_language() -> str:
        try:
            sys_locale, _ = locale.getdefaultlocale()
            if sys_locale:
                code = sys_locale[:2]
                lang_dir = Path(__file__).parent.parent / "languages"
                if (lang_dir / f"{code}.json").exists():
                    return code
        except:
            pass
        try:
            env_lang = os.environ.get('LANG', '')
            if env_lang:
                code = env_lang[:2]
                lang_dir = Path(__file__).parent.parent / "languages"
                if (lang_dir / f"{code}.json").exists():
                    return code
        except:
            pass
        return 'es'

    def _load(self):
        lang_dir = Path(__file__).parent.parent / "languages"
        filepath = lang_dir / f"{self.lang}.json"
        if not filepath.exists():
            filepath = lang_dir / "es.json"
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.strings = json.load(f)
        except:
            self.strings = {}

    def get(self, key: str, default: Optional[str] = None) -> str:
        return self.strings.get(key, default or key)

    def set_language(self, lang: str):
        self.lang = lang
        self._load()

    def get_available_languages(self) -> list:
        lang_dir = Path(__file__).parent.parent / "languages"
        if not lang_dir.exists():
            return [('es', 'Espanol')]
        langs = []
        for f in sorted(lang_dir.glob("*.json")):
            code = f.stem
            try:
                with open(f, 'r', encoding='utf-8') as fh:
                    data = json.load(fh)
                name = data.get('_language_name', code)
            except:
                name = code
            langs.append((code, name))
        return langs
