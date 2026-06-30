import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import sys
import subprocess
import os

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from gui.styles import Colors, Fonts
from src.model_database import ModelDatabase
from src.language_manager import LanguageManager
from src.settings_manager import SettingsManager

class ConfigTab(ttk.Frame):
    def __init__(self, parent, db: ModelDatabase, lang: LanguageManager,
                 settings: SettingsManager, on_lang_change=None):
        super().__init__(parent, style='Terminal.TFrame')
        self.db = db
        self.lang = lang
        self.settings = settings
        self.on_lang_change = on_lang_change
        self._setup_ui()

    def _setup_ui(self):
        title = ttk.Label(self, text=self.lang.get("config.title"),
                         style='Terminal.Title.TLabel')
        title.pack(pady=(20, 20))

        notebook = ttk.Notebook(self, style='Terminal.TNotebook')
        notebook.pack(fill='both', expand=True, padx=20, pady=10)

        self._create_sources_tab(notebook)
        self._create_language_tab(notebook)
        self._create_database_tab(notebook)
        self._create_logs_tab(notebook)
        self._create_about_tab(notebook)

    def _create_sources_tab(self, notebook):
        frame = ttk.Frame(notebook, style='Terminal.TFrame')
        notebook.add(frame, text="Fuentes de datos")

        row = 0

        ttk.Label(frame, text="Limite de busqueda",
                 style='Terminal.Header.TLabel').grid(row=row, column=0, columnspan=2,
                                                      sticky='w', padx=20, pady=(20, 5))
        row += 1

        ttk.Label(frame, text="Modelos a escanear por fuente:",
                 style='Terminal.TLabel').grid(row=row, column=0, sticky='w', padx=20)
        self.limit_var = tk.IntVar(value=self.settings.get('scan_limit', 100))
        limit_spin = ttk.Spinbox(frame, from_=10, to=500, textvariable=self.limit_var,
                                 width=8, style='Terminal.TSpinbox')
        limit_spin.grid(row=row, column=1, sticky='w', padx=10)
        limit_spin.bind('<FocusOut>', lambda e: self._save_setting('scan_limit', self.limit_var.get()))
        row += 1

        ttk.Separator(frame, orient='horizontal').grid(row=row, column=0, columnspan=2,
                                                       sticky='ew', padx=20, pady=10)
        row += 1

        ttk.Label(frame, text="Fuentes activas",
                 style='Terminal.Header.TLabel').grid(row=row, column=0, columnspan=2,
                                                      sticky='w', padx=20, pady=(0, 10))
        row += 1

        self.source_vars = {}
        sources = self.settings.get('data_sources', {})

        for src_key, src_data in sources.items():
            enabled = src_data.get('enabled', False)
            label = src_data.get('label', src_key)

            var = tk.BooleanVar(value=enabled)
            self.source_vars[src_key] = var

            cb = ttk.Checkbutton(frame, text=label, variable=var,
                                 style='Terminal.TCheckbutton',
                                 command=lambda k=src_key: self._toggle_source(k))
            cb.grid(row=row, column=0, sticky='w', padx=20, pady=3)
            row += 1

            api_url = src_data.get('api_url', '')
            if api_url:
                ttk.Label(frame, text=f"  URL:", style='Terminal.Subtitle.TLabel'
                         ).grid(row=row, column=0, sticky='w', padx=40)
                url_var = tk.StringVar(value=api_url)
                url_entry = ttk.Entry(frame, textvariable=url_var,
                                     style='Terminal.TEntry', width=60)
                url_entry.grid(row=row, column=1, sticky='w', padx=10)
                url_entry.bind('<FocusOut>',
                    lambda e, k=src_key, v=url_var: self._save_source_url(k, v.get()))
                row += 1

    def _create_language_tab(self, notebook):
        self.lang_frame = ttk.Frame(notebook, style='Terminal.TFrame')
        notebook.add(self.lang_frame, text=self.lang.get("config.language.title"))

        self.lang_var = tk.StringVar(value=self.lang.lang)
        self._build_lang_radios()

    def _build_lang_radios(self):
        for w in self.lang_frame.winfo_children():
            w.destroy()

        ttk.Label(self.lang_frame, text=self.lang.get("config.language.label"),
                 style='Terminal.Header.TLabel').pack(pady=(20, 10))

        langs = self.lang.get_available_languages()
        for code, name in langs:
            rb = ttk.Radiobutton(self.lang_frame, text=f"{name} ({code})",
                                variable=self.lang_var, value=code,
                                style='Terminal.TRadiobutton',
                                command=self._on_lang_selected)
            rb.pack(anchor='w', padx=40, pady=5)

    def _create_database_tab(self, notebook):
        frame = ttk.Frame(notebook, style='Terminal.TFrame')
        notebook.add(frame, text=self.lang.get("config.db.title"))

        ttk.Label(frame, text=self.lang.get("config.db.title"),
                 style='Terminal.Header.TLabel').pack(pady=(20, 10))

        info_text = self.lang.get("config.db.stored").replace('{count}', str(self.db.get_model_count()))
        ttk.Label(frame, text=info_text,
                 style='Terminal.TLabel').pack(pady=(0, 20))

        reset_btn = ttk.Button(frame,
                              text=self.lang.get("config.db.reset"),
                              style='Terminal.TButton',
                              command=self._reset_db)
        reset_btn.pack(pady=10)

        ttk.Label(frame,
                 text=self.lang.get("config.db.reset_confirm"),
                 style='Terminal.Subtitle.TLabel',
                 wraplength=500).pack(pady=(20, 0))

    def _create_logs_tab(self, notebook):
        frame = ttk.Frame(notebook, style='Terminal.TFrame')
        notebook.add(frame, text=self.lang.get("config.logs.title"))

        ttk.Label(frame, text=self.lang.get("config.logs.title"),
                 style='Terminal.Header.TLabel').pack(pady=(20, 10))

        view_btn = ttk.Button(frame,
                             text=self.lang.get("config.logs.view"),
                             style='Terminal.TButton',
                             command=self._view_logs)
        view_btn.pack(pady=10)

        log_path = Path(__file__).parent.parent.parent / "data" / "scan_errors.txt"
        if log_path.exists():
            try:
                size = log_path.stat().st_size
                with open(log_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                info = self.lang.get("config.logs.file_info").replace('{size}', str(size)).replace('{lines}', str(len(lines)))
                ttk.Label(frame, text=info,
                         style='Terminal.Subtitle.TLabel').pack(pady=10)
            except:
                pass
        else:
            ttk.Label(frame, text=self.lang.get("config.logs.no_file"),
                     style='Terminal.Subtitle.TLabel').pack(pady=10)

    def _create_about_tab(self, notebook):
        frame = ttk.Frame(notebook, style='Terminal.TFrame')
        notebook.add(frame, text=self.lang.get("config.about.title"))

        info = [
            (self.lang.get("config.about.name"), 'Terminal.Title.TLabel'),
            ("", None),
            (self.lang.get("config.about.version"), 'Terminal.TLabel'),
            (self.lang.get("config.about.desc"), 'Terminal.Subtitle.TLabel'),
            ("", None),
            (self.lang.get("config.about.tech"), 'Terminal.TLabel'),
            (self.lang.get("config.about.license"), 'Terminal.TLabel'),
        ]

        for text, style in info:
            if not text:
                ttk.Label(frame, text="", style='Terminal.TLabel').pack()
            else:
                ttk.Label(frame, text=text,
                         style=style or 'Terminal.TLabel').pack(pady=3)

        ttk.Separator(frame, orient='horizontal').pack(fill='x', padx=40, pady=15)

        ttk.Label(frame,
                 text=self.lang.get("config.about.collab"),
                 style='Terminal.Header.TLabel').pack(pady=(0, 5))

        ttk.Label(frame,
                 text="github.com/jgarvidsson/lenguages/tree/main/ia_profiler/1.0",
                 style='Terminal.Subtitle.TLabel',
                 foreground='#4A9EFF').pack()

        ttk.Label(frame,
                 text=self.lang.get("config.about.collab_desc"),
                 style='Terminal.Subtitle.TLabel',
                 wraplength=500).pack(pady=5)

        def open_github():
            import webbrowser
            webbrowser.open("https://github.com/jgarvidsson/lenguages/tree/main/ia_profiler/1.0")

        ttk.Button(frame,
                  text=self.lang.get("config.about.collab_btn"),
                  style='Terminal.TButton',
                  command=open_github).pack(pady=5)

        def check_lang_updates():
            L = self.lang
            try:
                import requests
                api_url = "https://api.github.com/repos/jgarvidsson/lenguages/contents/ia_profiler/1.0"
                headers = {}
                token = self.settings.get('github_token', '')
                if token:
                    headers['Authorization'] = f'token {token}'
                resp = requests.get(api_url, headers=headers, timeout=10)

                if resp.status_code == 404:
                    msg = ("Repositorio no encontrado o privado.\n\n"
                           "Si el repo es privado, necesitas un token de GitHub:\n"
                           "1. Ve a GitHub -> Settings -> Developer settings -> Personal access tokens\n"
                           "2. Crea un token con permiso 'repo'\n"
                           "3. Agregalo en data/config.json:\n"
                           '   "github_token": "tu_token"\n\n'
                           "O haz el repo publico para actualizacion automatica.")
                    messagebox.showwarning(L.get("config.about.check_btn"), msg)
                    webbrowser.open("https://github.com/jgarvidsson/lenguages/tree/main/ia_profiler/1.0")
                    return
                if resp.status_code == 403:
                    msg = ("Límite de API de GitHub alcanzado.\n"
                           "Espera unos minutos o agrega un token en data/config.json:\n"
                           '   "github_token": "tu_token"')
                    messagebox.showwarning(L.get("config.about.check_btn"), msg)
                    return
                if resp.status_code != 200:
                    msg = f"Error HTTP {resp.status_code}. Abre el enlace manualmente."
                    messagebox.showwarning(L.get("config.about.check_btn"), msg)
                    webbrowser.open("https://github.com/jgarvidsson/lenguages/tree/main/ia_profiler/1.0")
                    return

                remote_files = resp.json()
                if not isinstance(remote_files, list):
                    msg = "Estructura del repositorio no reconocida."
                    messagebox.showwarning(L.get("config.about.check_btn"), msg)
                    return

                remote_langs = {}
                for f in remote_files:
                    if f['name'].endswith('.json') and f['type'] == 'file':
                        code = f['name'].replace('.json', '')
                        remote_langs[code] = f['download_url']

                lang_dir = Path(__file__).parent.parent.parent / "languages"
                local_langs = {f.stem for f in lang_dir.glob("*.json")}

                new_langs = {k: v for k, v in remote_langs.items() if k not in local_langs}

                if not new_langs:
                    msg = L.get("config.about.check_done").replace('{count}', str(len(remote_langs)))
                    messagebox.showinfo(L.get("config.about.collab"), msg)
                    return

                codes = ', '.join(sorted(new_langs.keys()))
                msg = (f"Idiomas remotos: {', '.join(sorted(remote_langs.keys()))}\n"
                       f"Nuevos (no en local): {codes}\n\n"
                       "Descargar idiomas nuevos?")
                if messagebox.askyesno(L.get("config.about.collab"), msg):
                    downloaded = 0
                    for code, url in new_langs.items():
                        try:
                            r = requests.get(url, timeout=10)
                            if r.status_code == 200:
                                filepath = lang_dir / f"{code}.json"
                                with open(filepath, 'w', encoding='utf-8') as f:
                                    f.write(r.text)
                                downloaded += 1
                        except:
                            pass
                    msg = f"Descargados {downloaded} de {len(new_langs)} nuevos idiomas."
                    if downloaded:
                        self._build_lang_radios()
                    messagebox.showinfo(L.get("config.about.collab"), msg)
            except ImportError:
                messagebox.showwarning(L.get("config.about.check_btn"),
                    "Se necesita la biblioteca 'requests'.\n"
                    "Instalala con: pip install requests")
            except Exception as e:
                messagebox.showerror(L.get("config.about.collab"),
                    f"Error: {e}")

        ttk.Button(frame,
                  text=self.lang.get("config.about.check_btn"),
                  style='Terminal.TButton',
                  command=check_lang_updates).pack(pady=5)

    def _toggle_source(self, key: str):
        enabled = self.source_vars[key].get()
        self.settings.set(f'data_sources.{key}.enabled', enabled)

    def _save_source_url(self, key: str, url: str):
        self.settings.set(f'data_sources.{key}.api_url', url)

    def _save_setting(self, key: str, value):
        self.settings.set(key, value)

    def _on_lang_selected(self):
        new_lang = self.lang_var.get()
        if new_lang != self.lang.lang:
            self.lang.set_language(new_lang)
            self.settings.set('language', new_lang)
            if self.on_lang_change:
                self.on_lang_change(new_lang)

    def _reset_db(self):
        if messagebox.askyesno(
            self.lang.get("config.db.reset"),
            self.lang.get("config.db.reset_confirm")):
            try:
                self.db.clear_all()
                self.db._preload_models()
                messagebox.showinfo(
                    self.lang.get("config.db.reset"),
                    self.lang.get("config.db.reset_done"))
                if self.on_lang_change:
                    self.on_lang_change(self.lang.lang)
            except Exception as e:
                messagebox.showerror("Error", f"Error al resetear DB: {e}")

    def _view_logs(self):
        log_path = Path(__file__).parent.parent.parent / "data" / "scan_errors.txt"
        if not log_path.exists():
            messagebox.showinfo(
                self.lang.get("config.logs.title"),
                self.lang.get("config.logs.no_file"))
            return
        try:
            if sys.platform == 'win32':
                os.startfile(log_path)
            elif sys.platform == 'darwin':
                subprocess.run(['open', str(log_path)])
            else:
                subprocess.run(['xdg-open', str(log_path)])
        except Exception as e:
            msg = self.lang.get("config.logs.error").replace('{msg}', str(e))
            messagebox.showerror("Error", msg)
