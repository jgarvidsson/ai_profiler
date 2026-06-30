import pytest
from src.hardware_profiler import HardwareProfiler

def test_hardware_profiler_initialization():
    """Prueba que el perfilador se inicialice correctamente."""
    profiler = HardwareProfiler()
    assert profiler is not None
    assert 'cpu' in profiler.profile
    assert 'ram' in profiler.profile
    assert 'gpu' in profiler.profile

def test_ram_info():
    """Prueba que la información de RAM sea válida."""
    profiler = HardwareProfiler()
    ram = profiler.profile['ram']
    assert ram['total_gb'] > 0
    assert ram['available_gb'] >= 0
    assert ram['percent'] >= 0

def test_disk_info():
    """Prueba que la información de disco sea válida."""
    profiler = HardwareProfiler()
    disk = profiler.profile['disk']
    assert disk['total_gb'] > 0
    assert disk['free_gb'] >= 0
    assert disk['percent'] >= 0

def test_get_available_ram():
    """Prueba que retorne RAM disponible."""
    profiler = HardwareProfiler()
    ram = profiler.get_available_ram()
    assert ram >= 0
    assert isinstance(ram, float)