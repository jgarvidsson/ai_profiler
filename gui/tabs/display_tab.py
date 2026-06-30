import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import json
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from gui.styles import Colors, Fonts
from src.hardware_profiler import HardwareProfiler
from src.model_database import ModelDatabase
from src.recommendation_engine import RecommendationEngine
from src.language_manager import LanguageManager
from src.model_fetcher import ModelFetcher

class DisplayTab(ttk.Frame):
    def __init__(self, parent, db: ModelDatabase, lang: LanguageManager, on_db_updated=None):
        super().__init__(parent, style='Terminal.TFrame')
        self.db = db
        self.lang = lang
        self.profiler = HardwareProfiler()
        self.engine = RecommendationEngine()
        self.models = []
        self.current_results = []
        self.on_db_updated = on_db_updated
        self._setup_ui()

    def _setup_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        title = ttk.Label(self, text=self.lang.get("analysis.title"),
                         style='Terminal.Title.TLabel')
        title.grid(row=0, column=0, pady=(15, 5), sticky='w', padx=20)

        self.db_info = ttk.Label(self, text="",
                                style='Terminal.Subtitle.TLabel')
        self.db_info.grid(row=1, column=0, sticky='w', padx=20, pady=(0, 5))
        self._refresh_db_info()

        self._create_hardware_panel()
        self._create_results_panel()
        self._create_button_bar()
        self._update_hardware_info()

    def _create_hardware_panel(self):
        hw_frame = ttk.LabelFrame(self, text=self.lang.get("analysis.hw_title"),
                                  style='Terminal.TFrame', padding=10)
        hw_frame.grid(row=2, column=0, padx=20, pady=5, sticky='ew')
        hw_frame.columnconfigure((0, 1, 2, 3, 4), weight=1)

        card_style = {'bg': Colors.BG_ALT, 'fg': Colors.TEXT,
                      'font': Fonts.NORMAL, 'relief': 'flat',
                      'bd': 1, 'width': 16, 'height': 4}

        placeholders = f"{self.lang.get('analysis.hw.ram')}: -- GB"
        self.ram_card = tk.Label(hw_frame, text=placeholders, **card_style)
        self.ram_card.grid(row=0, column=0, padx=5, pady=5, sticky='ew')

        self.vram_card = tk.Label(hw_frame, text=f"{self.lang.get('analysis.hw.vram')}: -- GB", **card_style)
        self.vram_card.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        self.cpu_card = tk.Label(hw_frame, text=f"{self.lang.get('analysis.hw.cpu')}: --", **card_style)
        self.cpu_card.grid(row=0, column=2, padx=5, pady=5, sticky='ew')

        self.gpu_card = tk.Label(hw_frame, text=f"{self.lang.get('analysis.hw.gpu')}: --", **card_style)
        self.gpu_card.grid(row=0, column=3, padx=5, pady=5, sticky='ew')

        self.disk_card = tk.Label(hw_frame, text=f"{self.lang.get('analysis.hw.disk')}: -- GB", **card_style)
        self.disk_card.grid(row=0, column=4, padx=5, pady=5, sticky='ew')

    def _create_button_bar(self):
        btn_frame = ttk.Frame(self, style='Terminal.TFrame')
        btn_frame.grid(row=4, column=0, padx=20, pady=10, sticky='ew')

        self.scan_btn = ttk.Button(btn_frame,
                                   text=self.lang.get("analysis.btn.scan"),
                                   style='Terminal.TButton',
                                   command=self.scan_compatible)
        self.scan_btn.pack(side='left', padx=5)

        self.export_btn = ttk.Button(btn_frame,
                                     text=self.lang.get("analysis.btn.export"),
                                     style='Terminal.TButton',
                                     command=self.export_results,
                                     state='disabled')
        self.export_btn.pack(side='left', padx=5)

        self.clear_btn = ttk.Button(btn_frame,
                                    text=self.lang.get("analysis.btn.clear"),
                                    style='Terminal.TButton',
                                    command=self.clear_results)
        self.clear_btn.pack(side='left', padx=5)

        self.refresh_btn = ttk.Button(btn_frame,
                                      text=self.lang.get("analysis.btn.refresh"),
                                      style='Terminal.TButton',
                                      command=self.refresh_hardware)
        self.refresh_btn.pack(side='left', padx=5)

        self.progress = ttk.Progressbar(btn_frame,
                                       mode='indeterminate',
                                       style='Terminal.Horizontal.TProgressbar')
        self.progress.pack(side='right', padx=5, fill='x', expand=True)

    def _create_results_panel(self):
        results_frame = ttk.LabelFrame(self, text=self.lang.get("analysis.results_title"),
                                       style='Terminal.TFrame', padding=5)
        results_frame.grid(row=3, column=0, padx=20, pady=5, sticky='nsew')
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(1, weight=1)

        self.status_label = ttk.Label(results_frame,
                                      text=self.lang.get("analysis.status.ready"),
                                      style='Terminal.Subtitle.TLabel')
        self.status_label.grid(row=0, column=0, pady=(0, 5), sticky='w')

        columns = (
            self.lang.get("analysis.col.modelo"),
            self.lang.get("analysis.col.params"),
            self.lang.get("analysis.col.precision"),
            self.lang.get("analysis.col.ram"),
            self.lang.get("analysis.col.vram"),
            self.lang.get("analysis.col.technical"),
            self.lang.get("analysis.col.vision"),
            self.lang.get("analysis.col.audio"),
            self.lang.get("analysis.col.quality"),
        )
        self.tree = ttk.Treeview(results_frame, columns=columns,
                                show='headings', height=12,
                                style='Terminal.Treeview')

        col_widths = {
            columns[0]: 200, columns[1]: 80, columns[2]: 70,
            columns[3]: 70, columns[4]: 70, columns[5]: 60,
            columns[6]: 60, columns[7]: 60, columns[8]: 100
        }
        self.sort_col = None
        self.sort_reverse = False
        for col in columns:
            self.tree.heading(col, text=col,
                             command=lambda c=col: self._sort_by(c))
            width = col_widths.get(col, 100)
            anchor = 'w' if col == columns[0] else 'center'
            self.tree.column(col, width=width, anchor=anchor)

        scrollbar = ttk.Scrollbar(results_frame, orient='vertical',
                                 command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.bind('<Double-1>', self.on_double_click)

        self.tree.grid(row=1, column=0, sticky='nsew')
        scrollbar.grid(row=1, column=1, sticky='ns')

    def _update_hardware_info(self):
        profile = self.profiler.profile
        hw = self.profiler.get_summary()
        L = self.lang

        self.ram_card.config(
            text=f"{L.get('analysis.hw.ram')}\n{hw['ram_gb']:.1f} GB {L.get('analysis.hw.available')}\n{profile['ram']['total_gb']:.1f} GB {L.get('analysis.hw.total')}\n{L.get('analysis.hw.usage')}: {profile['ram']['percent']}%"
        )

        vram_text = f"{L.get('analysis.hw.vram')}\n{hw['vram_gb']:.1f} GB {L.get('analysis.hw.available')}"
        if profile['gpu']['available']:
            vram_text += f"\n{profile['gpu']['vram_total_gb']:.1f} GB {L.get('analysis.hw.total')}"
            vram_text += f"\n{L.get('analysis.hw.driver')}: {profile['gpu']['driver']}"
        else:
            vram_text += f"\n{L.get('analysis.hw.no_gpu')}"
        self.vram_card.config(text=vram_text)

        self.cpu_card.config(
            text=f"{L.get('analysis.hw.cpu')}\n{profile['cpu']['cores']} {L.get('analysis.hw.cores')}\n{profile['cpu']['physical_cores']} {L.get('analysis.hw.physical')}\n{profile['cpu']['speed_mhz']} MHz"
        )

        self.gpu_card.config(
            text=f"{L.get('analysis.hw.gpu')}\n{profile['gpu']['model'][:20]}"
        )

        self.disk_card.config(
            text=f"{L.get('analysis.hw.disk')}\n{hw['disk_gb']:.1f} GB {L.get('analysis.hw.free')}\n{profile['disk']['total_gb']:.1f} GB {L.get('analysis.hw.total')}\n{L.get('analysis.hw.usage')}: {profile['disk']['percent']}%"
        )

    def _sort_by(self, col):
        if self.sort_col == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_col = col
            self.sort_reverse = False

        items = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]

        def try_float(v):
            try:
                return float(v)
            except:
                return v

        items.sort(key=lambda x: try_float(x[0]), reverse=self.sort_reverse)
        for idx, (_, k) in enumerate(items):
            self.tree.move(k, '', idx)

        for c in self.tree['columns']:
            arrow = ' ▼' if (c == col and not self.sort_reverse) else ' ▲' if (c == col and self.sort_reverse) else ''
            base = self.tree.heading(c)['text'].rstrip(' ▲▼')
            self.tree.heading(c, text=base + arrow)

    def _refresh_db_info(self):
        count = self.db.get_model_count()
        last_update = self.db.get_last_update()
        updated_str = ""
        if last_update:
            updated_str = self.lang.get("app.footer.updated").replace('{date}', last_update[:10])
        else:
            updated_str = self.lang.get("search.db_never")
        self.db_info.config(
            text=self.lang.get("analysis.db_info").replace('{count}', str(count)).replace('{updated}', updated_str))

    def scan_compatible(self):
        self.status_label.config(text=self.lang.get("analysis.status.scanning"))
        self.progress.start()
        self.scan_btn.config(state='disabled')
        self.export_btn.config(state='disabled')

        for item in self.tree.get_children():
            self.tree.delete(item)

        threading.Thread(target=self._do_scan_compatible, daemon=True).start()

    def _do_scan_compatible(self):
        try:
            self.engine = RecommendationEngine()
            compatibles = self.engine.get_compatible_models()
            self.current_results = compatibles

            self.after(0, lambda: self._display_results(compatibles))
        except Exception as e:
            msg = self.lang.get("analysis.status.error").replace('{msg}', str(e))
            self.after(0, lambda: self._show_error(msg))
        finally:
            self.after(0, lambda: self._finish_scan())

    def _display_results(self, compatibles: list):
        for item in self.tree.get_children():
            self.tree.delete(item)

        L = self.lang
        si = L.get("analysis.yes")
        no = L.get("analysis.no")

        quality_map = {
            'low': 'analysis.quality.low',
            'medium': 'analysis.quality.medium',
            'medium_high': 'analysis.quality.medium_high',
            'high': 'analysis.quality.high',
            'very_high': 'analysis.quality.very_high',
            'maximum': 'analysis.quality.maximum',
            'Baja': 'analysis.quality.low',
            'Media': 'analysis.quality.medium',
            'Media-Alta': 'analysis.quality.medium_high',
            'Alta': 'analysis.quality.high',
            'Muy Alta': 'analysis.quality.very_high',
            'Máxima': 'analysis.quality.maximum',
        }

        if not compatibles:
            self.status_label.config(text=self.lang.get("analysis.status.none"))
            return

        for result in compatibles:
            model = result['model']
            comp = result['compatibility']
            uc = result['use_cases']

            if comp['compatible_precisions']:
                best = comp['compatible_precisions'][0]
                quality_key = quality_map.get(best['quality'], 'analysis.quality.medium_high')
                row = (
                    model.get('name', '?'),
                    model.get('params', '?'),
                    best['precision'],
                    f"{best['ram_needed']:.1f}",
                    f"{best['vram_needed']:.1f}",
                    si if uc['technical']['suitable'] else no,
                    si if uc['vision']['suitable'] else no,
                    si if uc['audio']['suitable'] else no,
                    L.get(quality_key)
                )
            else:
                row = (
                    model.get('name', '?'),
                    model.get('params', '?'),
                    '-', '-', '-',
                    si if uc['technical']['suitable'] else no,
                    si if uc['vision']['suitable'] else no,
                    si if uc['audio']['suitable'] else no,
                    '-'
                )

            self.tree.insert('', 'end', values=row)

        msg = self.lang.get("analysis.status.found").replace('{count}', str(len(compatibles)))
        self.status_label.config(text=msg)
        self.export_btn.config(state='normal')

    def _finish_scan(self):
        self.progress.stop()
        self.scan_btn.config(state='normal')
        self._refresh_db_info()
        if self.on_db_updated:
            self.on_db_updated()

    def clear_results(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.status_label.config(text=self.lang.get("analysis.status.cleared"))
        self.export_btn.config(state='disabled')
        self.current_results = []

    def refresh_hardware(self):
        self.profiler = HardwareProfiler()
        self._update_hardware_info()
        self.status_label.config(text=self.lang.get("analysis.status.refreshed"))

    def export_results(self):
        if not self.current_results:
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=f"compatibles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        if filename:
            try:
                export_data = {
                    'hardware': self.profiler.get_summary(),
                    'scanned_at': datetime.now().isoformat(),
                    'compatible_models': []
                }
                for r in self.current_results:
                    model = r['model']
                    comp = r['compatibility']
                    uc = r['use_cases']
                    entry = {
                        'name': model.get('name'),
                        'params': model.get('params'),
                        'compatibility': comp,
                        'use_cases': uc,
                        'capabilities': {
                            'technical': uc['technical']['suitable'],
                            'vision': uc['vision']['suitable'],
                            'audio': uc['audio']['suitable']
                        }
                    }
                    export_data['compatible_models'].append(entry)

                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                msg = self.lang.get("analysis.export.success").replace('{filename}', filename)
                messagebox.showinfo("Exito", msg)
            except Exception as e:
                msg = self.lang.get("analysis.export.error").replace('{msg}', str(e))
                messagebox.showerror("Error", msg)

    def on_double_click(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        item = self.tree.item(selection[0])
        values = item['values']
        if not values:
            return

        model_name = values[0]
        params = values[1] if len(values) > 1 else ''

        fetcher = ModelFetcher()
        ollama_name = fetcher.ollama_model_name(model_name)

        self._show_ollama_dialog(model_name, ollama_name)

    def _show_ollama_dialog(self, model_name: str, ollama_name: str):
        dialog = tk.Toplevel(self)
        dialog.title(f"Ollama - {model_name}")
        dialog.geometry("500x250")
        dialog.configure(bg=Colors.BG)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        ttk.Label(dialog, text="Comando para descargar con Ollama",
                 style='Terminal.Header.TLabel').pack(pady=(20, 10))

        cmd = f"ollama run {ollama_name}"
        text_frame = ttk.Frame(dialog, style='Terminal.TFrame')
        text_frame.pack(fill='x', padx=20, pady=10)

        cmd_text = tk.Text(text_frame, height=3,
                          bg=Colors.BG_ALT, fg=Colors.TEXT_BRIGHT,
                          font=('Courier', 12, 'bold'),
                          relief='flat', borderwidth=0)
        cmd_text.insert('1.0', f"$ {cmd}")
        cmd_text.config(state='disabled')
        cmd_text.pack(fill='x')

        btn_frame = ttk.Frame(dialog, style='Terminal.TFrame')
        btn_frame.pack(pady=10)

        def copy_cmd():
            dialog.clipboard_clear()
            dialog.clipboard_append(cmd)
            status_label.config(text="Comando copiado al portapapeles!")

        ttk.Button(btn_frame, text="Copiar comando",
                  style='Terminal.TButton',
                  command=copy_cmd).pack(side='left', padx=5)

        ttk.Button(btn_frame, text="Cerrar",
                  style='Terminal.TButton',
                  command=dialog.destroy).pack(side='left', padx=5)

        status_label = ttk.Label(dialog, text="",
                                style='Terminal.Subtitle.TLabel')
        status_label.pack(pady=5)

    def _show_error(self, message: str):
        self.progress.stop()
        self.scan_btn.config(state='normal')
        self.status_label.config(text=f"Error: {message}")
