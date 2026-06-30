"""
Módulo para búsqueda de modelos desde fuentes externas.
SOLO OBTIENE METADATOS, no descarga modelos.
"""

import httpx
import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

class ModelFetcher:
    """Buscador de modelos desde APIs externas (solo metadatos)."""
    
    def __init__(self):
        self.vramio_url = "https://vramio.ksingh.in/model"
        self.timeout = 15.0  # Aumentado para evitar timeouts
        self.session = httpx.Client(timeout=self.timeout)
    
    def fetch_from_vramio(self, model_id: str, retries: int = 2, quiet: bool = False) -> Optional[Dict[str, Any]]:
        """
        Obtiene información de un modelo desde VRAM.io.
        Solo metadatos, no descarga el modelo.
        """
        for attempt in range(retries + 1):
            try:
                response = self.session.get(
                    f"{self.vramio_url}?hf_id={model_id}"
                )
                response.raise_for_status()
                data = response.json()
                
                if not data or 'model' not in data:
                    if not quiet:
                        print(f"⚠️ Datos incompletos para {model_id}")
                    return None
                
                # Transformar al formato de nuestra DB
                return {
                    'name': data.get('model', model_id).split('/')[-1],
                    'full_name': data.get('model', model_id),
                    'params': data.get('total_parameters', 'Desconocido'),
                    'model_type': data.get('model_type', 'Densa'),
                    'context': data.get('context_length', 'Desconocido'),
                    'license': data.get('license', 'Desconocida'),
                    'description': data.get('description', ''),
                    'tags': data.get('tags', []),
                    'requirements': self._parse_vramio_requirements(data),
                    'source_url': f"https://huggingface.co/{data.get('model', model_id)}",
                    'last_updated': datetime.now().isoformat()
                }
            except httpx.TimeoutException:
                if not quiet:
                    print(f"⏱️ Timeout en intento {attempt + 1} para {model_id}")
                if attempt < retries:
                    time.sleep(1)
                    continue
                else:
                    if not quiet:
                        print(f"❌ Timeout después de {retries + 1} intentos para {model_id}")
                    return None
            except Exception as e:
                if not quiet:
                    print(f"❌ Error fetching {model_id}: {e}")
                if attempt < retries:
                    time.sleep(1)
                    continue
                return None
        
        return None

    def fetch_with_fallback(self, model_id: str, quiet: bool = True) -> Optional[Dict[str, Any]]:
        """Try VRAM.io first; if it fails, estimate requirements locally."""
        result = self.fetch_from_vramio(model_id, quiet=quiet)
        if result:
            return result
        return self._estimate_full_model(model_id)

    def _estimate_full_model(self, model_id: str) -> Dict[str, Any]:
        """Generate full model metadata with estimated requirements."""
        name = model_id.split('/')[-1]
        params = self._estimate_params(model_id)
        return {
            'name': name,
            'full_name': model_id,
            'params': params,
            'model_type': 'Densa',
            'context': '128K',
            'license': 'Desconocida',
            'description': f'Estimado localmente - {params}',
            'tags': ['text-generation', 'estimated'],
            'requirements': self._estimate_requirements(model_id),
            'source_url': f"https://huggingface.co/{model_id}",
            'last_updated': datetime.now().isoformat()
        }

    def _parse_vramio_requirements(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parsea los requisitos de VRAM.io."""
        requirements = {}
        
        # Mapeo de precisiones con valores por defecto
        precision_map = {
            'int4': {'ram_gb': None, 'vram_gb': None, 'quality': 'medium_high', 'speed': 5, 'recommended': True},
            'int8': {'ram_gb': None, 'vram_gb': None, 'quality': 'high', 'speed': 4, 'recommended': False},
            'fp16': {'ram_gb': None, 'vram_gb': None, 'quality': 'very_high', 'speed': 3, 'recommended': False},
            'fp32': {'ram_gb': None, 'vram_gb': None, 'quality': 'maximum', 'speed': 2, 'recommended': False}
        }
        
        # Obtener memoria requerida en diferentes precisiones
        other_precisions = data.get('other_precisions', {})
        
        for precision, values in precision_map.items():
            if precision in other_precisions:
                mem_str = other_precisions[precision]
                try:
                    # Convertir "13.49 GB" a float
                    mem_gb = float(mem_str.replace(' GB', '').replace(' MB', '')) / 1024 if 'MB' in mem_str else float(mem_str.replace(' GB', ''))
                    values['vram_gb'] = round(mem_gb, 2)
                    values['ram_gb'] = round(mem_gb * 1.5, 2)  # Estimación para RAM
                    requirements[precision] = values
                except (ValueError, AttributeError):
                    continue
        
        # Si no hay precisiones específicas, usar el requerimiento base
        if not requirements and 'memory_required' in data:
            try:
                mem_str = data['memory_required']
                mem_gb = float(mem_str.replace(' GB', '').replace(' MB', '')) / 1024 if 'MB' in mem_str else float(mem_str.replace(' GB', ''))
                requirements['fp16'] = {
                    'ram_gb': round(mem_gb * 1.5, 2),
                    'vram_gb': round(mem_gb, 2),
                    'quality': 'high',
                    'speed': 3,
                    'recommended': True
                }
            except (ValueError, AttributeError):
                pass
        
        return requirements
    
    def search_huggingface(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Busca modelos en Hugging Face (solo metadatos).
        """
        try:
            import requests
            
            # API REST de Hugging Face
            url = "https://huggingface.co/api/models"
            params = {
                'search': query,
                'limit': limit,
                'filter': 'text-generation',
                'sort': 'downloads'
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                models = []
                for model in data:
                    # Verificar que sea un modelo de texto
                    tags = model.get('tags', [])
                    if 'text-generation' in tags or 'conversational' in tags:
                        models.append({
                            'name': model.get('modelId', '').split('/')[-1],
                            'full_name': model.get('modelId', ''),
                            'description': model.get('description', ''),
                            'tags': tags,
                            'downloads': model.get('downloads', 0),
                            'likes': model.get('likes', 0),
                            'private': model.get('private', False),
                            'source_url': f"https://huggingface.co/{model.get('modelId', '')}"
                        })
                return models
            
            return []
            
        except Exception as e:
            print(f"Error en búsqueda: {e}")
            return []

    def fetch_popular_text_models(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Obtiene modelos populares de texto desde Hugging Face (lista dinámica)."""
        try:
            import requests
            url = "https://huggingface.co/api/models"
            params = {
                'filter': 'text-generation',
                'sort': 'downloads',
                'direction': -1,
                'limit': limit
            }
            response = requests.get(url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                models = []
                for model in data:
                    model_id = model.get('modelId', '')
                    tags = model.get('tags', [])
                    if 'text-generation' in tags or 'conversational' in tags:
                        models.append({
                            'full_name': model_id,
                            'name': model_id.split('/')[-1],
                            'downloads': model.get('downloads', 0),
                            'likes': model.get('likes', 0),
                            'pipeline_tag': 'text-generation'
                        })
                return models
            return []
        except Exception as e:
            print(f"Error obteniendo modelos populares: {e}")
            return []

    def fetch_model_details(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene detalles completos de un modelo desde Hugging Face + VRAM.io.
        """
        try:
            # Primero obtener detalles básicos de HF
            import requests
            hf_response = requests.get(
                f"https://huggingface.co/api/models/{model_id}",
                timeout=10
            )
            hf_data = hf_response.json() if hf_response.status_code == 200 else {}
            
            # Luego obtener requisitos de VRAM.io
            vram_data = self.fetch_from_vramio(model_id)
            
            # Combinar datos
            result = {
                'name': model_id.split('/')[-1],
                'full_name': model_id,
                'description': hf_data.get('description', ''),
                'tags': hf_data.get('tags', []),
                'downloads': hf_data.get('downloads', 0),
                'likes': hf_data.get('likes', 0),
                'source_url': f"https://huggingface.co/{model_id}",
                'last_updated': datetime.now().isoformat()
            }
            
            # Agregar requisitos si están disponibles
            if vram_data:
                result.update({
                    'params': vram_data.get('params', 'Desconocido'),
                    'context': vram_data.get('context', 'Desconocido'),
                    'license': vram_data.get('license', 'Desconocida'),
                    'requirements': vram_data.get('requirements', {})
                })
            else:
                # Estimar requisitos basados en parámetros
                result.update({
                    'params': self._estimate_params(model_id),
                    'context': '128K',
                    'license': 'Desconocida',
                    'requirements': self._estimate_requirements(model_id)
                })
            
            return result
            
        except Exception as e:
            print(f"Error obteniendo detalles de {model_id}: {e}")
            return None
    
    def _estimate_params(self, model_id: str) -> str:
        """Estima los parámetros del modelo basado en el nombre."""
        model_id_lower = model_id.lower()
        # Ordenar de más específico a menos específico
        patterns = [
            ('70b', '70B'), ('34b', '34B'), ('32b', '32B'),
            ('30b', '30B'), ('27b', '27B'), ('22b', '22B'),
            ('20b', '20B'), ('14b', '14B'), ('13b', '13B'),
            ('12b', '12B'), ('9b', '9B'), ('8b', '8B'),
            ('7b', '7B'), ('3b', '3B'), ('2b', '2B'),
            ('1b', '1B'), ('0.5b', '0.5B'),
        ]
        for pattern, result in patterns:
            if pattern in model_id_lower:
                return result
        return 'Desconocido'
    
    def _estimate_requirements(self, model_id: str) -> Dict[str, Any]:
        """Estima requisitos basados en el nombre del modelo."""
        params_str = self._estimate_params(model_id)
        try:
            # Extraer número de parámetros
            if 'B' in params_str:
                params = float(params_str.replace('B', ''))
            else:
                params = 7  # Valor por defecto
        except:
            params = 7
        
        # Estimación: ~1.2 GB por cada B de parámetros en FP16
        vram_fp16 = params * 1.2
        vram_int8 = vram_fp16 / 2
        vram_int4 = vram_fp16 / 4
        
        return {
            'int4': {
                'vram_gb': round(vram_int4, 2),
                'ram_gb': round(vram_int4 * 1.5, 2),
                'quality': 'medium_high',
                'speed': 5,
                'recommended': True
            },
            'int8': {
                'vram_gb': round(vram_int8, 2),
                'ram_gb': round(vram_int8 * 1.5, 2),
                'quality': 'high',
                'speed': 4,
                'recommended': False
            },
            'fp16': {
                'vram_gb': round(vram_fp16, 2),
                'ram_gb': round(vram_fp16 * 1.5, 2),
                'quality': 'very_high',
                'speed': 3,
                'recommended': False
            }
        }
    
    def fetch_multiple(self, model_ids: List[str], progress_callback=None) -> List[Dict[str, Any]]:
        """
        Obtiene múltiples modelos con progreso.
        """
        results = []
        total = len(model_ids)
        
        for i, model_id in enumerate(model_ids):
            if progress_callback:
                progress_callback(i + 1, total, model_id)
            
            # Esperar entre peticiones para no sobrecargar la API
            if i > 0:
                time.sleep(0.5)
            
            model_data = self.fetch_model_details(model_id)
            if model_data:
                results.append(model_data)
                print(f"✅ {model_id}")
            else:
                print(f"❌ {model_id} - No se pudo obtener")
        
        return results
    
    def get_popular_models(self) -> List[str]:
        """Lista de modelos populares para descargar metadatos."""
        return [
            'meta-llama/Llama-3-8B',
            'meta-llama/Llama-3-70B',
            'mistralai/Mistral-7B-v0.1',
            'microsoft/Phi-3-mini-4k-instruct',
            'microsoft/Phi-3-medium-4k-instruct',
            'deepseek-ai/deepseek-coder-6.7b-instruct',
            'deepseek-ai/deepseek-coder-33b-instruct',
            'google/gemma-2b',
            'google/gemma-7b',
            'tiiuae/falcon-7b',
            'tiiuae/falcon-40b',
            'Qwen/Qwen2.5-7B-Instruct',
            'Qwen/Qwen2.5-14B-Instruct',
            'Qwen/Qwen2.5-32B-Instruct',
            'databricks/dbrx-instruct'
        ]

    def fetch_ollama_models(self) -> List[Dict[str, Any]]:
        """Detecta modelos disponibles localmente via Ollama CLI."""
        try:
            import subprocess
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                return []

            models = []
            lines = result.stdout.strip().split('\n')[1:]
            for line in lines:
                if not line.strip():
                    continue
                parts = line.split()
                if parts:
                    name = parts[0]
                    models.append({
                        'full_name': name,
                        'name': name,
                        'source': 'ollama',
                        'local': True
                    })
            return models
        except FileNotFoundError:
            return []
        except Exception:
            return []

    def ollama_model_name(self, model_name: str) -> str:
        """Convierte nombre de modelo HF a nombre de modelo Ollama."""
        mapping = {
            'Llama-3-8B': 'llama3',
            'Llama-3-70B': 'llama3:70b',
            'Mistral-7B': 'mistral',
            'Phi-3-Mini': 'phi3:mini',
            'Phi-3-Medium': 'phi3:medium',
            'DeepSeek-Coder-6.7B': 'deepseek-coder:6.7b',
            'Qwen2.5-7B': 'qwen2.5:7b',
            'Qwen2.5-14B': 'qwen2.5:14b',
            'Qwen2.5-32B': 'qwen2.5:32b',
            'Gemma-2B': 'gemma2:2b',
            'Gemma-7B': 'gemma2:7b',
            'Falcon-7B': 'falcon2:7b',
            'Falcon-40B': 'falcon2:40b',
        }
        for key, val in mapping.items():
            if key.lower() in model_name.lower():
                return val
        return model_name.lower().replace('/', ':').replace('-', ':').split(':')[-1] if ':' in model_name.lower().replace('/', ':') else model_name.lower()

    def close(self):
        """Cierra la sesión HTTP."""
        self.session.close()