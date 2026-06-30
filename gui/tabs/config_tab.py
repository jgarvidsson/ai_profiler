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
        frame = ttk.Frame(notebook, style='Terminal.TFrame')
        notebook.add(frame, text=self.lang.get("config.language.title"))

        ttk.Label(frame, text=self.lang.get("config.language.label"),
                 style='Terminal.Header.TLabel').pack(pady=(20, 10))

        langs = self.lang.get_available_languages()
        self.lang_var = tk.StringVar(value=self.lang.lang)

        for code, name in langs:
            rb = ttk.Radiobutton(frame, text=f"{name} ({code})",
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
                 text="github.com/jgarvidsson/lenguages/ia_profiler/1.0/",
                 style='Terminal.Subtitle.TLabel',
                 foreground='#4A9EFF').pack()

        ttk.Label(frame,
                 text=self.lang.get("config.about.collab_desc"),
                 style='Terminal.Subtitle.TLabel',
                 wraplength=500).pack(pady=5)

        def open_github():
            import webbrowser
            webbrowser.open("https://github.com/jgarvidsson/lenguages/ia_profiler/1.0/")

        ttk.Button(frame,
                  text=self.lang.get("config.about.collab_btn"),
                  style='Terminal.TButton',
                  command=open_github).pack(pady=5)

        def check_lang_updates():
            count = len(self.lang.get_available_languages())
            msg = self.lang.get("config.about.check_done").replace('{count}', str(count))
            messagebox.showinfo(self.lang.get("config.about.collab"), msg)

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
