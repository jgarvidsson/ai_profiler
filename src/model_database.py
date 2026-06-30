"""
Módulo independiente para gestión de base de datos local SQLite.
Almacena modelos, requisitos y compatibilidad.
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

class ModelDatabase:
    """Gestión de base de datos local para modelos de IA."""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = Path(__file__).parent.parent / "data" / "models.db"
        self.db_path = db_path
        self._init_database()
        
        # Verificar si hay modelos, si no, precargar
        if self.get_model_count() == 0:
            self._preload_models()
    
    def _init_database(self):
        """Inicializa la base de datos con las tablas necesarias."""
        Path(self.db_path).parent.mkdir(exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de modelos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                full_name TEXT,
                params TEXT,
                model_type TEXT,
                context TEXT,
                license TEXT,
                description TEXT,
                tags TEXT,
                source_url TEXT,
                last_updated TIMESTAMP,
                is_active INTEGER DEFAULT 1
            )
        ''')
        
        # Tabla de requisitos (con recommended añadido)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS requirements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_id INTEGER,
                precision_type TEXT NOT NULL,
                ram_gb REAL,
                vram_gb REAL,
                disk_gb REAL,
                quality TEXT,
                speed INTEGER,
                recommended INTEGER DEFAULT 0,
                FOREIGN KEY (model_id) REFERENCES models(id),
                UNIQUE(model_id, precision_type)
            )
        ''')
        
        # Verificar si la columna recommended existe, si no, añadirla
        try:
            cursor.execute('SELECT recommended FROM requirements LIMIT 1')
        except sqlite3.OperationalError:
            # La columna no existe, añadirla
            try:
                cursor.execute('ALTER TABLE requirements ADD COLUMN recommended INTEGER DEFAULT 0')
                print("✅ Columna 'recommended' añadida a requirements")
            except sqlite3.OperationalError:
                pass
        
        # Tabla de compatibilidad
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS compatibility (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_id INTEGER,
                hardware_hash TEXT,
                ram_available_gb REAL,
                vram_available_gb REAL,
                compatible INTEGER,
                recommended_precision TEXT,
                checked_at TIMESTAMP,
                FOREIGN KEY (model_id) REFERENCES models(id)
            )
        ''')
        
        # Índices
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_models_name ON models(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_models_tags ON models(tags)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_req_model ON requirements(model_id)')
        
        conn.commit()
        conn.close()
    
    def get_model_count(self) -> int:
        """Retorna el número de modelos en la base de datos."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT COUNT(*) FROM models WHERE is_active = 1')
            count = cursor.fetchone()[0]
        except:
            count = 0
        conn.close()
        return count
    
    def _preload_models(self):
        """Precarga modelos conocidos si la DB está vacía."""
        print("📦 Precargando modelos populares en la base de datos...")
        
        # Modelos predefinidos con requisitos estimados
        default_models = [
            {
                'name': 'Llama-3-8B',
                'full_name': 'meta-llama/Llama-3-8B',
                'params': '8B',
                'context': '128K',
                'license': 'Meta Llama 3',
                'description': 'Modelo de Meta con excelente rendimiento general',
                'tags': ['general', 'balanceado', 'popular'],
                'requirements': {
                    'int4': {'vram_gb': 4.5, 'ram_gb': 6.75, 'quality': 'Media-Alta', 'speed': 5, 'recommended': 1},
                    'int8': {'vram_gb': 9.0, 'ram_gb': 13.5, 'quality': 'Alta', 'speed': 4, 'recommended': 0},
                    'fp16': {'vram_gb': 16.0, 'ram_gb': 24.0, 'quality': 'Muy Alta', 'speed': 3, 'recommended': 0}
                }
            },
            {
                'name': 'Mistral-7B',
                'full_name': 'mistralai/Mistral-7B-v0.1',
                'params': '7B',
                'context': '32K',
                'license': 'Apache 2.0',
                'description': 'Excelente relación calidad/rendimiento',
                'tags': ['referencia', 'balanceado', 'popular'],
                'requirements': {
                    'int4': {'vram_gb': 4.0, 'ram_gb': 6.0, 'quality': 'Media-Alta', 'speed': 5, 'recommended': 1},
                    'int8': {'vram_gb': 8.0, 'ram_gb': 12.0, 'quality': 'Alta', 'speed': 4, 'recommended': 0},
                    'fp16': {'vram_gb': 14.0, 'ram_gb': 21.0, 'quality': 'Muy Alta', 'speed': 3, 'recommended': 0}
                }
            },
            {
                'name': 'Phi-3-Mini',
                'full_name': 'microsoft/Phi-3-mini-4k-instruct',
                'params': '3.8B',
                'context': '128K',
                'license': 'MIT',
                'description': 'Modelo ultra-ligero para hardware limitado',
                'tags': ['ultra-ligero', 'edge', 'popular'],
                'requirements': {
                    'int4': {'vram_gb': 2.5, 'ram_gb': 3.75, 'quality': 'Media', 'speed': 5, 'recommended': 1},
                    'int8': {'vram_gb': 5.0, 'ram_gb': 7.5, 'quality': 'Media-Alta', 'speed': 4, 'recommended': 0},
                    'fp16': {'vram_gb': 8.0, 'ram_gb': 12.0, 'quality': 'Alta', 'speed': 3, 'recommended': 0}
                }
            },
            {
                'name': 'Phi-3-Medium',
                'full_name': 'microsoft/Phi-3-medium-4k-instruct',
                'params': '14B',
                'context': '128K',
                'license': 'MIT',
                'description': 'Modelo ligero con buen razonamiento',
                'tags': ['ligero', 'razonamiento', 'popular'],
                'requirements': {
                    'int4': {'vram_gb': 8.0, 'ram_gb': 12.0, 'quality': 'Media-Alta', 'speed': 5, 'recommended': 1},
                    'int8': {'vram_gb': 16.0, 'ram_gb': 24.0, 'quality': 'Alta', 'speed': 4, 'recommended': 0},
                    'fp16': {'vram_gb': 28.0, 'ram_gb': 42.0, 'quality': 'Muy Alta', 'speed': 3, 'recommended': 0}
                }
            },
            {
                'name': 'DeepSeek-Coder-6.7B',
                'full_name': 'deepseek-ai/deepseek-coder-6.7b-instruct',
                'params': '6.7B',
                'context': '128K',
                'license': 'DeepSeek',
                'description': 'Especializado en programación',
                'tags': ['codificación', 'eficiente', 'popular'],
                'requirements': {
                    'int4': {'vram_gb': 4.0, 'ram_gb': 6.0, 'quality': 'Media-Alta', 'speed': 5, 'recommended': 1},
                    'int8': {'vram_gb': 8.0, 'ram_gb': 12.0, 'quality': 'Alta', 'speed': 4, 'recommended': 0},
                    'fp16': {'vram_gb': 13.4, 'ram_gb': 20.1, 'quality': 'Muy Alta', 'speed': 3, 'recommended': 0}
                }
            },
            {
                'name': 'Qwen2.5-7B',
                'full_name': 'Qwen/Qwen2.5-7B-Instruct',
                'params': '7B',
                'context': '128K',
                'license': 'Qwen',
                'description': 'Modelo chino con buen rendimiento multilingüe',
                'tags': ['multilingüe', 'balanceado'],
                'requirements': {
                    'int4': {'vram_gb': 4.5, 'ram_gb': 6.75, 'quality': 'Media-Alta', 'speed': 5, 'recommended': 1},
                    'int8': {'vram_gb': 9.0, 'ram_gb': 13.5, 'quality': 'Alta', 'speed': 4, 'recommended': 0},
                    'fp16': {'vram_gb': 14.0, 'ram_gb': 21.0, 'quality': 'Muy Alta', 'speed': 3, 'recommended': 0}
                }
            },
            {
                'name': 'Qwen2.5-14B',
                'full_name': 'Qwen/Qwen2.5-14B-Instruct',
                'params': '14B',
                'context': '128K',
                'license': 'Qwen',
                'description': 'Modelo grande con excelente razonamiento',
                'tags': ['razonamiento', 'grande'],
                'requirements': {
                    'int4': {'vram_gb': 9.0, 'ram_gb': 13.5, 'quality': 'Media-Alta', 'speed': 5, 'recommended': 1},
                    'int8': {'vram_gb': 18.0, 'ram_gb': 27.0, 'quality': 'Alta', 'speed': 4, 'recommended': 0},
                    'fp16': {'vram_gb': 28.0, 'ram_gb': 42.0, 'quality': 'Muy Alta', 'speed': 3, 'recommended': 0}
                }
            },
            {
                'name': 'Qwen2.5-32B',
                'full_name': 'Qwen/Qwen2.5-32B-Instruct',
                'params': '32B',
                'context': '128K',
                'license': 'Qwen',
                'description': 'Modelo muy grande para tareas complejas',
                'tags': ['razonamiento', 'muy-grande'],
                'requirements': {
                    'int4': {'vram_gb': 20.0, 'ram_gb': 30.0, 'quality': 'Media-Alta', 'speed': 5, 'recommended': 1},
                    'int8': {'vram_gb': 40.0, 'ram_gb': 60.0, 'quality': 'Alta', 'speed': 4, 'recommended': 0},
                    'fp16': {'vram_gb': 64.0, 'ram_gb': 96.0, 'quality': 'Muy Alta', 'speed': 3, 'recommended': 0}
                }
            },
            {
                'name': 'Gemma-2B',
                'full_name': 'google/gemma-2b',
                'params': '2B',
                'context': '8K',
                'license': 'Google',
                'description': 'Modelo ultra-ligero de Google',
                'tags': ['ultra-ligero', 'edge'],
                'requirements': {
                    'int4': {'vram_gb': 1.5, 'ram_gb': 2.25, 'quality': 'Media', 'speed': 5, 'recommended': 1},
                    'int8': {'vram_gb': 3.0, 'ram_gb': 4.5, 'quality': 'Media-Alta', 'speed': 4, 'recommended': 0},
                    'fp16': {'vram_gb': 4.0, 'ram_gb': 6.0, 'quality': 'Alta', 'speed': 3, 'recommended': 0}
                }
            },
            {
                'name': 'Gemma-7B',
                'full_name': 'google/gemma-7b',
                'params': '7B',
                'context': '8K',
                'license': 'Google',
                'description': 'Modelo ligero de Google',
                'tags': ['ligero', 'razonamiento'],
                'requirements': {
                    'int4': {'vram_gb': 4.5, 'ram_gb': 6.75, 'quality': 'Media-Alta', 'speed': 5, 'recommended': 1},
                    'int8': {'vram_gb': 9.0, 'ram_gb': 13.5, 'quality': 'Alta', 'speed': 4, 'recommended': 0},
                    'fp16': {'vram_gb': 14.0, 'ram_gb': 21.0, 'quality': 'Muy Alta', 'speed': 3, 'recommended': 0}
                }
            },
            {
                'name': 'Falcon-7B',
                'full_name': 'tiiuae/falcon-7b',
                'params': '7B',
                'context': '2K',
                'license': 'TII',
                'description': 'Modelo robusto de TII',
                'tags': ['robusto', 'balanceado'],
                'requirements': {
                    'int4': {'vram_gb': 4.5, 'ram_gb': 6.75, 'quality': 'Media-Alta', 'speed': 5, 'recommended': 1},
                    'int8': {'vram_gb': 9.0, 'ram_gb': 13.5, 'quality': 'Alta', 'speed': 4, 'recommended': 0},
                    'fp16': {'vram_gb': 14.0, 'ram_gb': 21.0, 'quality': 'Muy Alta', 'speed': 3, 'recommended': 0}
                }
            },
            {
                'name': 'Falcon-40B',
                'full_name': 'tiiuae/falcon-40b',
                'params': '40B',
                'context': '2K',
                'license': 'TII',
                'description': 'Modelo muy grande de TII',
                'tags': ['muy-grande', 'robusto'],
                'requirements': {
                    'int4': {'vram_gb': 25.0, 'ram_gb': 37.5, 'quality': 'Media-Alta', 'speed': 5, 'recommended': 1},
                    'int8': {'vram_gb': 50.0, 'ram_gb': 75.0, 'quality': 'Alta', 'speed': 4, 'recommended': 0},
                    'fp16': {'vram_gb': 80.0, 'ram_gb': 120.0, 'quality': 'Muy Alta', 'speed': 3, 'recommended': 0}
                }
            },
            {
                'name': 'Llama-3-70B',
                'full_name': 'meta-llama/Llama-3-70B',
                'params': '70B',
                'context': '128K',
                'license': 'Meta Llama 3',
                'description': 'Modelo enorme de Meta para tareas avanzadas',
                'tags': ['enorme', 'avanzado'],
                'requirements': {
                    'int4': {'vram_gb': 45.0, 'ram_gb': 67.5, 'quality': 'Media-Alta', 'speed': 5, 'recommended': 1},
                    'int8': {'vram_gb': 90.0, 'ram_gb': 135.0, 'quality': 'Alta', 'speed': 4, 'recommended': 0},
                    'fp16': {'vram_gb': 140.0, 'ram_gb': 210.0, 'quality': 'Muy Alta', 'speed': 3, 'recommended': 0}
                }
            }
        ]
        
        # Insertar modelos
        for model_data in default_models:
            try:
                # Verificar si ya existe
                if not self.get_model(model_data['name']):
                    self.add_model(model_data)
                    self.add_requirements(model_data['name'], model_data['requirements'])
            except Exception as e:
                print(f"Error precargando {model_data['name']}: {e}")
        
        print(f"✅ Precargados {len(default_models)} modelos")
    
    def add_model(self, model_data: Dict[str, Any]) -> int:
        """Añade un nuevo modelo a la base de datos."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO models 
            (name, full_name, params, model_type, context, license, description, tags, source_url, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            model_data.get('name'),
            model_data.get('full_name'),
            model_data.get('params'),
            model_data.get('model_type', 'Densa'),
            model_data.get('context'),
            model_data.get('license'),
            model_data.get('description'),
            json.dumps(model_data.get('tags', [])),
            model_data.get('source_url'),
            datetime.now().isoformat()
        ))
        
        model_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return model_id
    
    def add_requirements(self, model_name: str, requirements: Dict[str, Any]):
        """Añade requisitos para un modelo."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM models WHERE name = ?', (model_name,))
        result = cursor.fetchone()
        if not result:
            conn.close()
            return False
        
        model_id = result[0]
        
        for precision, reqs in requirements.items():
            cursor.execute('''
                INSERT OR REPLACE INTO requirements
                (model_id, precision_type, ram_gb, vram_gb, disk_gb, quality, speed, recommended)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                model_id,
                precision,
                reqs.get('ram_gb'),
                reqs.get('vram_gb'),
                reqs.get('disk_gb', reqs.get('vram_gb', 0) * 0.8),
                reqs.get('quality', 'Media'),
                reqs.get('speed', 3),
                reqs.get('recommended', 0)
            ))
        
        conn.commit()
        conn.close()
        return True
    
    def get_model(self, name: str) -> Optional[Dict[str, Any]]:
        """Obtiene un modelo específico por nombre."""
        models = self.get_all_models()
        for model in models:
            if model['name'].lower() == name.lower():
                return model
        return None
    
    def get_all_models(self) -> List[Dict[str, Any]]:
        """Obtiene todos los modelos con sus requisitos."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT m.*, 
                   GROUP_CONCAT(
                       r.precision_type || '|' || 
                       COALESCE(r.ram_gb, 'null') || '|' || 
                       COALESCE(r.vram_gb, 'null') || '|' || 
                       COALESCE(r.disk_gb, 'null') || '|' ||
                       COALESCE(r.quality, 'Media') || '|' ||
                       COALESCE(r.speed, '3') || '|' ||
                       COALESCE(r.recommended, '0'), 
                       '||'
                   ) as requirements_raw
            FROM models m
            LEFT JOIN requirements r ON m.id = r.model_id
            WHERE m.is_active = 1
            GROUP BY m.id
        ''')
        
        results = []
        for row in cursor.fetchall():
            model = dict(row)
            
            # Parsear tags
            if model.get('tags'):
                model['tags'] = json.loads(model['tags'])
            else:
                model['tags'] = []
            
            # Parsear requisitos
            requirements = {}
            if model.get('requirements_raw'):
                for req_str in model['requirements_raw'].split('||'):
                    if req_str:
                        parts = req_str.split('|')
                        if len(parts) >= 3:
                            precision = parts[0]
                            reqs = {
                                'ram_gb': float(parts[1]) if parts[1] != 'null' and parts[1] else None,
                                'vram_gb': float(parts[2]) if parts[2] != 'null' and parts[2] else None,
                                'disk_gb': float(parts[3]) if parts[3] != 'null' and parts[3] else None,
                                'quality': parts[4] if len(parts) > 4 and parts[4] else 'Media',
                                'speed': int(parts[5]) if len(parts) > 5 and parts[5] and parts[5] != 'null' else 3,
                                'recommended': int(parts[6]) if len(parts) > 6 and parts[6] and parts[6] != 'null' else 0
                            }
                            requirements[precision] = reqs
            
            model['requirements'] = requirements
            model.pop('requirements_raw', None)
            results.append(model)
        
        conn.close()
        return results
    
    def search_models(self, query: str, tag: Optional[str] = None) -> List[Dict[str, Any]]:
        """Busca modelos por nombre o etiqueta."""
        models = self.get_all_models()
        results = []
        query_lower = query.lower() if query else ''
        
        for model in models:
            match = False
            name = model.get('name', '').lower()
            full_name = model.get('full_name', '').lower()
            description = model.get('description', '').lower()
            tags = [t.lower() for t in model.get('tags', [])]
            
            if query:
                if query_lower in name or query_lower in full_name or query_lower in description:
                    match = True
            
            if tag and not match:
                if tag.lower() in tags:
                    match = True
            
            if query and tag:
                match = (query_lower in name or query_lower in full_name) and tag.lower() in tags
            
            if not query and not tag:
                match = True
            
            if match:
                results.append(model)
        
        return results
    
    def check_compatibility(self, model_name: str, hardware_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Verifica compatibilidad de un modelo con hardware específico."""
        model = self.get_model(model_name)
        if not model:
            return {'compatible': False, 'error': 'Modelo no encontrado'}
        
        requirements = model.get('requirements', {})
        ram_available = hardware_summary.get('ram_gb', 0)
        vram_available = hardware_summary.get('vram_gb', 0)
        
        compatible_precisions = []
        for precision, reqs in requirements.items():
            ram_needed = reqs.get('ram_gb', float('inf'))
            vram_needed = reqs.get('vram_gb', float('inf'))
            
            # Si hay VRAM disponible, usar VRAM, si no, RAM
            if vram_available > 0 and vram_needed:
                compatible = vram_available >= (vram_needed or float('inf')) * 1.1
                memory_type = 'VRAM'
                memory_available = vram_available
                memory_needed = vram_needed
            else:
                compatible = ram_available >= (ram_needed or float('inf')) * 1.1
                memory_type = 'RAM'
                memory_available = ram_available
                memory_needed = ram_needed
            
            if compatible:
                compatible_precisions.append({
                    'precision': precision,
                    'ram_needed': ram_needed,
                    'vram_needed': vram_needed,
                    'memory_needed': memory_needed,
                    'memory_available': memory_available,
                    'memory_type': memory_type,
                    'quality': reqs.get('quality', 'Media'),
                    'speed': reqs.get('speed', 3),
                    'recommended': reqs.get('recommended', 0)
                })
        
        # Ordenar por recommended primero, luego por memoria necesaria
        compatible_precisions.sort(key=lambda x: (-x.get('recommended', 0), x.get('memory_needed', float('inf'))))
        
        return {
            'model': model_name,
            'compatible': len(compatible_precisions) > 0,
            'compatible_precisions': compatible_precisions,
            'ram_available': ram_available,
            'vram_available': vram_available,
            'model_info': {
                'params': model.get('params'),
                'context': model.get('context'),
                'description': model.get('description')
            }
        }
    
    def export_to_json(self, filepath: str) -> bool:
        """Exporta toda la base de datos a JSON."""
        try:
            models = self.get_all_models()
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(models, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error exportando: {e}")
            return False
    
    def import_from_json(self, filepath: str) -> bool:
        """Importa modelos desde JSON."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                models = json.load(f)
            
            for model in models:
                model_data = {k: v for k, v in model.items() if k not in ['id', 'requirements', 'last_updated']}
                self.add_model(model_data)
                
                if 'requirements' in model:
                    self.add_requirements(model['name'], model['requirements'])
            
            return True
        except Exception as e:
            print(f"Error importando: {e}")
            return False
    
    def get_last_update(self) -> Optional[str]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT MAX(last_updated) FROM models WHERE is_active = 1')
            result = cursor.fetchone()
            if result and result[0]:
                return result[0][:19]
            return None
        except:
            return None
        finally:
            conn.close()

    def clear_all(self):
        """Limpia todos los datos (útil para pruebas)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM requirements')
        cursor.execute('DELETE FROM compatibility')
        cursor.execute('DELETE FROM models')
        conn.commit()
        conn.close()