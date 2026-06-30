"""
Módulo independiente para perfilado de hardware.
Puede ser usado por cualquier otro proyecto.
"""

import psutil
import platform
import subprocess
import re
from typing import Dict, Any, Optional
import json
from pathlib import Path

class HardwareProfiler:
    """Perfila las capacidades de hardware del sistema actual."""
    
    def __init__(self):
        self.profile = self._get_profile()
        self._cache_file = Path(__file__).parent.parent / "data" / "hardware_cache.json"
    
    def _get_profile(self) -> Dict[str, Any]:
        """Obtiene todas las especificaciones relevantes del hardware."""
        profile = {
            'cpu': self._get_cpu_info(),
            'ram': self._get_ram_info(),
            'gpu': self._get_gpu_info(),
            'disk': self._get_disk_info(),
            'os': platform.system(),
            'os_version': platform.version(),
            'python_version': platform.python_version()
        }
        return profile
    
    def _get_cpu_info(self) -> Dict[str, Any]:
        try:
            freq = psutil.cpu_freq()
            return {
                'cores': psutil.cpu_count(logical=True),
                'physical_cores': psutil.cpu_count(logical=False),
                'speed_mhz': freq.max if freq else None,
                'percent': psutil.cpu_percent(interval=0.1)
            }
        except Exception:
            return {'cores': 0, 'physical_cores': 0, 'speed_mhz': None, 'percent': 0}
    
    def _get_ram_info(self) -> Dict[str, float]:
        try:
            ram = psutil.virtual_memory()
            return {
                'total_gb': round(ram.total / (1024**3), 2),
                'available_gb': round(ram.available / (1024**3), 2),
                'used_gb': round(ram.used / (1024**3), 2),
                'percent': ram.percent
            }
        except Exception:
            return {'total_gb': 0, 'available_gb': 0, 'used_gb': 0, 'percent': 0}
    
    def _get_gpu_info(self) -> Dict[str, Any]:
        """Detección de GPU con múltiples métodos."""
        
        # Método 1: nvidia-ml-py (proporciona el módulo pynvml)
        try:
            import pynvml as nvml
            nvml.nvmlInit()
            device_count = nvml.nvmlDeviceGetCount()
            if device_count > 0:
                handle = nvml.nvmlDeviceGetHandleByIndex(0)
                name = nvml.nvmlDeviceGetName(handle)
                memory_info = nvml.nvmlDeviceGetMemoryInfo(handle)
                return {
                    'available': True,
                    'count': device_count,
                    'model': name.decode('utf-8') if isinstance(name, bytes) else str(name),
                    'vram_total_gb': round(memory_info.total / (1024**3), 2),
                    'vram_available_gb': round(memory_info.free / (1024**3), 2),
                    'vram_used_gb': round(memory_info.used / (1024**3), 2),
                    'driver': 'NVIDIA',
                    'method': 'nvml'
                }
        except ImportError:
            # No hay NVIDIA ML, intentar con métodos alternativos
            pass
        except Exception:
            pass
        
        # Método 2: Windows WMI
        if platform.system() == 'Windows':
            try:
                result = subprocess.run(
                    ['wmic', 'path', 'win32_VideoController', 'get', 
                     'name,AdapterRAM,DriverVersion'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')[1:]
                    for line in lines:
                        if line.strip() and not 'Intel' in line and not 'Microsoft' in line:
                            parts = line.split()
                            if len(parts) >= 2:
                                name_parts = []
                                ram_mb = 0
                                for part in parts:
                                    if part.isdigit():
                                        ram_mb = int(part) / (1024**2)
                                    else:
                                        name_parts.append(part)
                                name = ' '.join(name_parts)
                                if name and len(name) > 3:
                                    return {
                                        'available': True,
                                        'count': 1,
                                        'model': name,
                                        'vram_total_gb': round(ram_mb / 1024, 2),
                                        'vram_available_gb': round(ram_mb / 1024, 2),
                                        'vram_used_gb': 0,
                                        'driver': 'Windows WMI',
                                        'method': 'wmi'
                                    }
            except:
                pass
        
        # Sin GPU detectada
        return {
            'available': False,
            'count': 0,
            'model': 'No GPU detectada',
            'vram_total_gb': 0,
            'vram_available_gb': 0,
            'vram_used_gb': 0,
            'driver': 'N/A',
            'method': 'none'
        }
    
    def _get_disk_info(self) -> Dict[str, float]:
        try:
            disk = psutil.disk_usage('/')
            return {
                'total_gb': round(disk.total / (1024**3), 2),
                'free_gb': round(disk.free / (1024**3), 2),
                'used_gb': round(disk.used / (1024**3), 2),
                'percent': disk.percent
            }
        except:
            return {'total_gb': 0, 'free_gb': 0, 'used_gb': 0, 'percent': 0}
    
    def get_available_vram(self) -> float:
        return self.profile['gpu'].get('vram_available_gb', 0.0)
    
    def get_available_ram(self) -> float:
        return self.profile['ram']['available_gb']
    
    def get_summary(self) -> Dict[str, Any]:
        """Retorna un resumen del hardware para comparación rápida."""
        return {
            'ram_gb': self.profile['ram']['available_gb'],
            'vram_gb': self.get_available_vram(),
            'disk_gb': self.profile['disk']['free_gb'],
            'gpu_model': self.profile['gpu'].get('model', 'None'),
            'has_gpu': self.profile['gpu'].get('available', False)
        }
    
    def save_cache(self):
        """Guarda el perfil en caché para uso rápido."""
        self._cache_file.parent.mkdir(exist_ok=True)
        with open(self._cache_file, 'w') as f:
            json.dump(self.profile, f, indent=2)
    
    @classmethod
    def load_cache(cls) -> Dict[str, Any]:
        """Carga el perfil desde caché."""
        cache_file = Path(__file__).parent.parent / "data" / "hardware_cache.json"
        if cache_file.exists():
            with open(cache_file) as f:
                return json.load(f)
        return None
    
    def get_profile_report(self) -> str:
        gpu = self.profile['gpu']
        report = f"""
╔════════════════════════════════════════════════════════╗
║              PERFIL DE HARDWARE DETECTADO              ║
╚════════════════════════════════════════════════════════╝

📌 SISTEMA:
   • OS: {self.profile['os']}
   • Versión: {self.profile['os_version']}
   • Python: {self.profile['python_version']}

💻 CPU:
   • Núcleos: {self.profile['cpu']['cores']} (lógicos) | {self.profile['cpu']['physical_cores']} (físicos)
   • Velocidad: {self.profile['cpu']['speed_mhz']} MHz
   • Uso: {self.profile['cpu']['percent']}%

🧠 RAM:
   • Total: {self.profile['ram']['total_gb']} GB
   • Disponible: {self.profile['ram']['available_gb']} GB
   • Uso: {self.profile['ram']['percent']}%

💾 DISCO:
   • Total: {self.profile['disk']['total_gb']} GB
   • Libre: {self.profile['disk']['free_gb']} GB
   • Uso: {self.profile['disk']['percent']}%

🎮 GPU:"""
        if gpu.get('available', False):
            report += f"""
   • Modelo: {gpu.get('model', 'Desconocida')}
   • VRAM Total: {gpu.get('vram_total_gb', 0)} GB
   • VRAM Disponible: {gpu.get('vram_available_gb', 0)} GB
   • Driver: {gpu.get('driver', 'N/A')}
   • Detección: {gpu.get('method', 'desconocido')}"""
        else:
            report += f"""
   • {gpu.get('model', 'No detectada')}"""
        
        return report

    def __str__(self):
        return self.get_profile_report()