import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from gui.styles import Colors, Fonts, configure_styles
from gui.tabs.search_tab import SearchTab
from gui.tabs.display_tab import DisplayTab
from gui.tabs.config_tab import ConfigTab
from src.model_database import ModelDatabase
from src.language_manager import LanguageManager
from src.settings_manager import SettingsManager

class AIProfilerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.settings = SettingsManager()
        saved_lang = self.settings.get('language', 'auto')
        self.lang = LanguageManager(saved_lang)
        if saved_lang == 'auto':
            self.settings.set('language', self.lang.lang)
        self.root.title(self.lang.get("app.title"))
        self.root.geometry("1200x960")
        self.root.minsize(1000, 700)
        self.root.configure(bg=Colors.BG)

        try:
            self.root.iconbitmap(default='icon.ico')
        except:
            pass

        configure_styles()
        self.db = ModelDatabase()
        self._setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _setup_ui(self):
        header = ttk.Frame(self.root, style='Terminal.TFrame')
        header.pack(fill='x', padx=20, pady=10)

        title = ttk.Label(header,
            text=self.lang.get("app.title"),
            style='Terminal.Title.TLabel')
        title.pack(side='left')

        version = ttk.Label(header,
            text=self.lang.get("app.version"),
            style='Terminal.Subtitle.TLabel')
        version.pack(side='right')

        ttk.Separator(self.root, orient='horizontal').pack(fill='x', padx=20)

        self.notebook = ttk.Notebook(self.root, style='Terminal.TNotebook')
        self.notebook.pack(fill='both', expand=True, padx=20, pady=10)

        self.search_tab = SearchTab(self.notebook, self.db, self.lang, self.settings, self.refresh_ui)
        self.notebook.add(self.search_tab, text=self.lang.get("app.tab.search"))

        self.display_tab = DisplayTab(self.notebook, self.db, self.lang, self.refresh_ui)
        self.notebook.add(self.display_tab, text=self.lang.get("app.tab.analysis"))

        self.config_tab = ConfigTab(self.notebook, self.db, self.lang, self.settings, self.on_language_changed)
        self.notebook.add(self.config_tab, text=self.lang.get("app.tab.config"))

        self._build_footer()
        self.refresh_ui()

    def _build_footer(self):
        self.footer = ttk.Frame(self.root, style='Terminal.TFrame')
        self.footer.pack(fill='x', padx=20, pady=5)

        self.footer_status = ttk.Label(self.footer,
            text=self.lang.get("app.footer.db"),
            style='Terminal.Subtitle.TLabel')
        self.footer_status.pack(side='left')

        self.footer_models = ttk.Label(self.footer,
            text="",
            style='Terminal.Subtitle.TLabel')
        self.footer_models.pack(side='right', padx=(15, 0))

        self.footer_updated = ttk.Label(self.footer,
            text="",
            style='Terminal.Subtitle.TLabel')
        self.footer_updated.pack(side='right')

    def refresh_ui(self):
        count = self.db.get_model_count()
        last_update = self.db.get_last_update()

        self.root.title(self.lang.get("app.title"))

        self.footer_models.config(
            text=self.lang.get("app.footer.models").replace('{count}', str(count)))

        if last_update:
            updated_str = self.lang.get("app.footer.updated").replace('{date}', last_update[:10])
        else:
            updated_str = ""
        self.footer_updated.config(text=updated_str)

        self.notebook.tab(0, text=self.lang.get("app.tab.search"))
        self.notebook.tab(1, text=self.lang.get("app.tab.analysis"))
        self.notebook.tab(2, text=self.lang.get("app.tab.config"))

    def on_language_changed(self, new_lang):
        self.lang.set_language(new_lang)
        self.refresh_ui()

    def run(self):
        self.root.mainloop()

    def on_close(self):
        if messagebox.askokcancel(
            self.lang.get("app.exit.title"),
            self.lang.get("app.exit.confirm")):
            self.root.destroy()

def main():
    app = AIProfilerApp()
    app.run()

if __name__ == "__main__":
    main()
