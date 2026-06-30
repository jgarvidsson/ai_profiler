import tkinter as tk
from tkinter import ttk, messagebox
import threading
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from gui.styles import Colors, Fonts
from src.model_database import ModelDatabase
from src.model_fetcher import ModelFetcher
from src.language_manager import LanguageManager
from src.settings_manager import SettingsManager

class SearchTab(ttk.Frame):
    def __init__(self, parent, db: ModelDatabase, lang: LanguageManager,
                 settings: SettingsManager, on_db_updated=None):
        super().__init__(parent, style='Terminal.TFrame')
        self.db = db
        self.lang = lang
        self.settings = settings
        self.fetcher = ModelFetcher()
        self.current_model = None
        self.search_results = []
        self.on_db_updated = on_db_updated
        self.scan_stop = False
        self._setup_ui()
        self._show_db_info()

    def _setup_ui(self):
        title = ttk.Label(self, text=self.lang.get("search.title"),
                         style='Terminal.Title.TLabel')
        title.pack(pady=(15, 5))

        subtitle = ttk.Label(self, text=self.lang.get("search.subtitle"),
                            style='Terminal.Subtitle.TLabel')
        subtitle.pack(pady=(0, 10))

        self._build_db_info_bar()

        search_frame = ttk.Frame(self, style='Terminal.TFrame')
        search_frame.pack(fill='x', padx=20, pady=5)

        ttk.Label(search_frame, text=self.lang.get("search.label.query"),
                 style='Terminal.TLabel').pack(side='left', padx=(0, 10))

        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame,
                                     textvariable=self.search_var,
                                     style='Terminal.TEntry',
                                     width=50)
        self.search_entry.pack(side='left', padx=(0, 10))
        self.search_entry.bind('<Return>', lambda e: self.search_models())

        self.search_btn = ttk.Button(search_frame,
                                     text=self.lang.get("search.btn.search"),
                                     style='Terminal.TButton',
                                     command=self.search_models)
        self.search_btn.pack(side='left')

        specific_frame = ttk.Frame(self, style='Terminal.TFrame')
        specific_frame.pack(fill='x', padx=20, pady=5)

        ttk.Label(specific_frame, text=self.lang.get("search.label.specific"),
                 style='Terminal.TLabel').pack(side='left', padx=(0, 10))

        self.specific_var = tk.StringVar()
        self.specific_entry = ttk.Entry(specific_frame,
                                       textvariable=self.specific_var,
                                       style='Terminal.TEntry',
                                       width=40)
        self.specific_entry.pack(side='left', padx=(0, 10))

        self.fetch_btn = ttk.Button(specific_frame,
                                    text=self.lang.get("search.btn.fetch"),
                                    style='Terminal.TButton',
                                    command=self.fetch_specific)
        self.fetch_btn.pack(side='left')

        ttk.Separator(self, orient='horizontal').pack(fill='x', padx=20, pady=5)

        results_frame = ttk.Frame(self, style='Terminal.TFrame')
        results_frame.pack(fill='both', expand=True, padx=20, pady=5)

        columns = ('#', 'Modelo', 'Parametros', 'Descargas', 'Likes')
        self.tree = ttk.Treeview(results_frame, columns=columns,
                                show='headings',
                                style='Terminal.Treeview')

        for col in columns:
            self.tree.heading(col, text=col)
        self.tree.column('#', width=40, anchor='center')
        self.tree.column('Modelo', width=280, anchor='w')
        self.tree.column('Parametros', width=80, anchor='center')
        self.tree.column('Descargas', width=80, anchor='center')
        self.tree.column('Likes', width=60, anchor='center')

        scrollbar = ttk.Scrollbar(results_frame, orient='vertical',
                                 command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        self.tree.bind('<<TreeviewSelect>>', self.on_select)

        self.details_frame = ttk.LabelFrame(self,
                                           text=self.lang.get("search.details.title"),
                                           style='Terminal.TFrame', padding=8)
        self.details_frame.pack(fill='x', padx=20, pady=5)

        self.details_text = tk.Text(self.details_frame,
                                    height=4,
                                    bg=Colors.BG_ALT,
                                    fg=Colors.TEXT,
                                    font=Fonts.SMALL,
                                    wrap='word',
                                    relief='flat',
                                    borderwidth=0)
        self.details_text.pack(fill='x')

        action_frame = ttk.Frame(self, style='Terminal.TFrame')
        action_frame.pack(fill='x', padx=20, pady=5)

        self.add_btn = ttk.Button(action_frame,
                                 text=self.lang.get("search.btn.add_db"),
                                 style='Terminal.TButton',
                                 command=self.add_to_db,
                                 state='disabled')
        self.add_btn.pack(side='left', padx=5)

        self.scan_btn = ttk.Button(action_frame,
                                  text=self.lang.get("search.btn.scan"),
                                  style='Terminal.TButton',
                                  command=self.scan_external)
        self.scan_btn.pack(side='left', padx=5)

        self.stop_btn = ttk.Button(action_frame,
                                  text=self.lang.get("search.btn.stop"),
                                  style='Terminal.TButton',
                                  command=self.stop_scan,
                                  state='disabled')
        self.stop_btn.pack(side='left', padx=5)

        self.fetch_all_btn = ttk.Button(action_frame,
                                       text=self.lang.get("search.btn.import_all"),
                                       style='Terminal.TButton',
                                       command=self.fetch_all)
        self.fetch_all_btn.pack(side='left', padx=5)

        self.progress = ttk.Progressbar(self,
                                       mode='indeterminate',
                                       style='Terminal.Horizontal.TProgressbar')
        self.progress.pack(fill='x', padx=20, pady=(5, 10))

        self.status_label = ttk.Label(self, text=self.lang.get("search.status.ready"),
                                     style='Terminal.Subtitle.TLabel')
        self.status_label.pack(pady=(0, 15))

    def _build_db_info_bar(self):
        info_frame = ttk.Frame(self, style='Terminal.TFrame')
        info_frame.pack(fill='x', padx=20, pady=(0, 10))

        self.db_info_label = ttk.Label(info_frame, text="",
                                      style='Terminal.Subtitle.TLabel')
        self.db_info_label.pack(side='left')

    def _show_db_info(self):
        count = self.db.get_model_count()
        last_update = self.db.get_last_update()
        updated_str = ""
        if last_update:
            updated_str = self.lang.get("search.db_never")
        else:
            updated_str = self.lang.get("app.footer.updated").replace('{date}', last_update[:10])
        self.db_info_label.config(
            text=self.lang.get("search.db_info").replace('{count}', str(count)).replace('{updated}', updated_str))

    def search_models(self):
        query = self.search_var.get().strip()
        if not query:
            msg = self.lang.get("search.error.empty_query")
            messagebox.showwarning(self.lang.get("search.btn.search"), msg)
            return

        msg = self.lang.get("search.status.searching").replace('{query}', query)
        self.status_label.config(text=msg)
        self.progress.start()
        self.search_btn.config(state='disabled')

        threading.Thread(target=self._do_search, args=(query,), daemon=True).start()

    def _do_search(self, query: str):
        try:
            results = self.fetcher.search_huggingface(query, limit=20)
            self.search_results = results
            self.after(0, lambda: self._update_search_results(results))
        except Exception as e:
            msg = self.lang.get("search.error.search").replace('{msg}', str(e))
            self.after(0, lambda: self._show_error(msg))

    def _update_search_results(self, results: list):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for i, model in enumerate(results, 1):
            self.tree.insert('', 'end', values=(
                i,
                model.get('name', 'Desconocido'),
                'N/A',
                model.get('downloads', 0),
                model.get('likes', 0)
            ), tags=(model.get('full_name', ''),))

        msg = self.lang.get("search.status.found").replace('{count}', str(len(results)))
        self.status_label.config(text=msg)
        self.progress.stop()
        self.search_btn.config(state='normal')

    def fetch_specific(self):
        model_id = self.specific_var.get().strip()
        if not model_id:
            msg = self.lang.get("search.error.empty_id")
            messagebox.showwarning(self.lang.get("search.btn.fetch"), msg)
            return

        msg = self.lang.get("search.status.fetching").replace('{model_id}', model_id)
        self.status_label.config(text=msg)
        self.progress.start()
        self.fetch_btn.config(state='disabled')

        threading.Thread(target=self._do_fetch_specific, args=(model_id,), daemon=True).start()

    def _do_fetch_specific(self, model_id: str):
        try:
            model_data = self.fetcher.fetch_with_fallback(model_id)
            if model_data:
                self.current_model = model_data
                self.after(0, lambda: self._show_model_details(model_data))
                self.after(0, lambda: self.add_btn.config(state='normal'))
                source = "API" if 'estimated' not in model_data.get('tags', []) else "estimación"
                msg = self.lang.get("search.status.fetched").replace('{name}', model_data['name']) + f" ({source})"
                self.status_label.config(text=msg)
            else:
                msg = self.lang.get("search.error.fetch").replace('{model_id}', model_id)
                self.after(0, lambda: self._show_error(msg))
        except Exception as e:
            msg = self.lang.get("search.error.fetch_generic").replace('{msg}', str(e))
            self.after(0, lambda: self._show_error(msg))
        finally:
            self.progress.stop()
            self.fetch_btn.config(state='normal')

    def _show_model_details(self, model_data: dict):
        details = f"""
Nombre: {model_data.get('name', 'N/A')}
ID completo: {model_data.get('full_name', 'N/A')}
Parametros: {model_data.get('params', 'N/A')}
Contexto: {model_data.get('context', 'N/A')}
Tipo: {model_data.get('model_type', 'N/A')}
Licencia: {model_data.get('license', 'N/A')}

Requisitos (VRAM):
"""
        for precision, reqs in model_data.get('requirements', {}).items():
            details += f"  - {precision}: {reqs.get('vram_gb', 'N/A')} GB VRAM\n"

        self.details_text.delete('1.0', tk.END)
        self.details_text.insert('1.0', details)

    def on_select(self, event):
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            full_name = item['tags'][0] if item['tags'] else None
            if full_name:
                self.specific_var.set(full_name)
                self.fetch_specific()

    def add_to_db(self):
        if not self.current_model:
            return

        try:
            model_data = self.current_model
            self.db.add_model(model_data)
            self.db.add_requirements(model_data['name'], model_data['requirements'])

            msg = self.lang.get("search.status.added").replace('{name}', model_data['name'])
            self.status_label.config(text=msg)
            messagebox.showinfo(
                self.lang.get("search.btn.add_db"),
                f"Modelo '{model_data['name']}' agregado a la base de datos.")

            self.add_btn.config(state='disabled')
            self.current_model = None
            self._show_db_info()
            if self.on_db_updated:
                self.on_db_updated()
        except Exception as e:
            msg = self.lang.get("search.error.add").replace('{msg}', str(e))
            self._show_error(msg)

    def stop_scan(self):
        self.scan_stop = True
        self.status_label.config(text=self.lang.get("search.status.scan_stop"))

    def scan_external(self):
        def do_scan():
            self.scan_stop = False
            self.scan_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            self.fetch_all_btn.config(state='disabled')
            self.progress.start()

            msg = self.lang.get("search.status.scanning").replace('{current}', '0').replace('{total}', str(total)).replace('{model_id}', '...')
            self.status_label.config(text=msg)

            threading.Thread(target=self._do_scan_external,
                           args=(model_list, total), daemon=True).start()

        self.status_label.config(text="Obteniendo lista de modelos populares...")
        self.progress.start()
        self.scan_btn.config(state='disabled')

        threading.Thread(target=self._fetch_popular_list, daemon=True).start()

    def _fetch_popular_list(self):
        try:
            scan_limit = self.settings.get('scan_limit', 100)
            enabled_sources = self.settings.get_enabled_sources()
            all_models = []

            if 'huggingface' in enabled_sources:
                hf_models = self.fetcher.fetch_popular_text_models(limit=scan_limit)
                all_models.extend(hf_models)

            if 'vramio' in enabled_sources:
                if not all_models:
                    fallback = self.fetcher.get_popular_models()
                    for m in fallback:
                        all_models.append({'full_name': m})

            if 'ollama' in enabled_sources:
                ollama_models = self.fetcher.fetch_ollama_models()
                for om in ollama_models:
                    if om['full_name'] not in [m.get('full_name') for m in all_models]:
                        all_models.append(om)

            total = len(all_models)
            if total == 0:
                self.after(0, lambda: self._show_error("No se pudieron obtener modelos para rastrear."))
                return

            self.after(0, lambda: self._confirm_and_scan(all_models, total))
        except Exception as e:
            self.after(0, lambda: self._show_error(f"Error obteniendo lista: {e}"))

    def _confirm_and_scan(self, model_list: list, total: int):
        self.progress.stop()
        self.scan_btn.config(state='normal')

        confirm_msg = f"Rastrear {total} modelos externos y agregar los nuevos a la DB local?\nEsto puede tomar varios minutos. Puedes detenerlo en cualquier momento."
        if messagebox.askyesno("Confirmar", confirm_msg):
            self.scan_stop = False
            msg = self.lang.get("search.status.scanning").replace('{current}', '0').replace('{total}', str(total)).replace('{model_id}', '...')
            self.status_label.config(text=msg)
            self.progress.start()
            self.scan_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            self.fetch_all_btn.config(state='disabled')

            threading.Thread(target=self._do_scan_external,
                           args=(model_list, total), daemon=True).start()

    def _do_scan_external(self, model_list: list, total: int):
        added = 0
        skipped = 0
        estimated = 0
        failed = 0
        stopped = False
        errors = []

        for i, model_entry in enumerate(model_list):
            if self.scan_stop:
                stopped = True
                break

            model_id = model_entry.get('full_name', model_entry if isinstance(model_entry, str) else '')
            if not model_id:
                continue

            current = i + 1
            scan_msg = self.lang.get("search.status.scanning").replace('{current}', str(current)).replace('{total}', str(total)).replace('{model_id}', model_id)
            self.after(0, lambda m=scan_msg: self.status_label.config(text=m))

            try:
                model_data = self.fetcher.fetch_with_fallback(model_id)
                if model_data:
                    existing = self.db.get_model(model_data['name'])
                    if not existing:
                        self.db.add_model(model_data)
                        self.db.add_requirements(model_data['name'], model_data['requirements'])
                        added += 1
                        if 'estimated' in model_data.get('tags', []):
                            estimated += 1
                    else:
                        skipped += 1
                else:
                    failed += 1
                    errors.append(f"{model_id}: No se pudieron obtener datos")
            except Exception as e:
                failed += 1
                errors.append(f"{model_id}: {e}")

        self._log_scan_errors(errors)
        self.after(0, lambda: self._finish_scan(added, skipped, failed, total, stopped, estimated))

    def _log_scan_errors(self, errors: list):
        if not errors:
            return
        try:
            log_path = Path(__file__).parent.parent.parent / "data" / "scan_errors.txt"
            log_path.parent.mkdir(exist_ok=True)
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(f"\n--- Escaneo {datetime.now().isoformat()} ---\n")
                for err in errors:
                    f.write(f"  {err}\n")
        except:
            pass

    def _finish_scan(self, added: int, skipped: int, failed: int, total: int, stopped: bool, estimated: int = 0):
        self.progress.stop()
        self.scan_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.fetch_all_btn.config(state='normal')

        processed = added + skipped + failed
        action_key = "search.scan.stopped" if stopped else "search.scan.completed"
        action = self.lang.get(action_key)

        summary = self.lang.get("search.scan.summary").replace('{action}', action).replace('{added}', str(added)).replace('{skipped}', str(skipped)).replace('{failed}', str(failed)).replace('{processed}', str(processed)).replace('{total}', str(total))
        self.status_label.config(text=summary)
        self._show_db_info()

        if self.on_db_updated:
            self.on_db_updated()

        result_msg = self.lang.get("search.scan.result_msg").replace('{action}', action).replace('{added}', str(added)).replace('{skipped}', str(skipped)).replace('{failed}', str(failed)).replace('{processed}', str(processed)).replace('{total}', str(total))
        if estimated:
            result_msg += f"\n({estimated} con requisitos estimados localmente)"
        result_title = self.lang.get("search.scan.result_title").replace('{action}', action)
        messagebox.showinfo(result_title, result_msg)

    def fetch_all(self):
        confirm_msg = self.lang.get("search.import.confirm_msg")
        if messagebox.askyesno(
            self.lang.get("search.import.confirm_title"), confirm_msg):

            msg = self.lang.get("search.import.downloading")
            self.status_label.config(text=msg)
            self.progress.start()
            self.fetch_all_btn.config(state='disabled')

            threading.Thread(target=self._do_fetch_all_popular, daemon=True).start()

    def _do_fetch_all_popular(self):
        popular_models = self.fetcher.get_popular_models()
        saved = 0
        total = len(popular_models)

        def update_progress(current, total, model_id):
            self.after(0, lambda: self.status_label.config(
                text=f"{current}/{total}: {model_id}"
            ))
            self.after(0, lambda: self.progress.step(100/total))

        results = self.fetcher.fetch_multiple(
            popular_models,
            progress_callback=update_progress
        )

        for model_data in results:
            try:
                db_model = {
                    'name': model_data.get('name'),
                    'full_name': model_data.get('full_name'),
                    'params': model_data.get('params', 'Desconocido'),
                    'model_type': model_data.get('model_type', 'Densa'),
                    'context': model_data.get('context', 'Desconocido'),
                    'license': model_data.get('license', 'Desconocida'),
                    'description': model_data.get('description', ''),
                    'tags': model_data.get('tags', []),
                    'source_url': model_data.get('source_url', ''),
                }
                self.db.add_model(db_model)

                if 'requirements' in model_data:
                    self.db.add_requirements(model_data['name'], model_data['requirements'])

                saved += 1
            except Exception as e:
                print(f"Error guardando {model_data.get('name')}: {e}")

        self.after(0, lambda: self._finish_fetch_all(saved, total))

    def _finish_fetch_all(self, saved: int, total: int):
        self.progress.stop()
        self.fetch_all_btn.config(state='normal')
        msg = self.lang.get("search.import.done").replace('{saved}', str(saved)).replace('{total}', str(total))
        self.status_label.config(text=msg)
        self._show_db_info()
        if self.on_db_updated:
            self.on_db_updated()

    def _show_error(self, message: str):
        self.progress.stop()
        self.search_btn.config(state='normal')
        self.fetch_btn.config(state='normal')
        self.scan_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.fetch_all_btn.config(state='normal')
        self.status_label.config(text=f"Error: {message}")
        messagebox.showerror("Error", message)
