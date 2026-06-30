#!/usr/bin/env python3
"""
Script de diagnóstico para verificar el hardware y dependencias.
"""

import sys
import platform

def check_python():
    """Verifica la versión de Python."""
    version = sys.version_info
    print(f"🐍 Python: {version.major}.{version.minor}.{version.micro}")
    if version.major == 3 and version.minor >= 12:
        print("   ⚠️ Python 3.12+ detectado (sin distutils)")
    return True

def check_dependencies():
    """Verifica dependencias críticas."""
    deps = {
        'psutil': 'psutil',
        'pynvml': 'pynvml',
        'requests': 'requests'
    }
    
    print("\n📦 Dependencias:")
    for name, module in deps.items():
        try:
            __import__(module)
            print(f"   ✅ {name}")
        except ImportError:
            print(f"   ❌ {name} (no instalado)")
    
    # Verificar GPUtil (opcional)
    try:
        __import__('GPUtil')
        print("   ⚠️ GPUtil instalado (puede causar problemas en Python 3.12+)")
    except ImportError:
        print("   ℹ️ GPUtil no instalado (recomendado para Python 3.12+)")

def check_hardware():
    """Verifica hardware básico."""
    print("\n🖥️ Hardware:")
    
    try:
        import psutil
        ram = psutil.virtual_memory()
        print(f"   RAM Total: {ram.total / (1024**3):.1f} GB")
        print(f"   RAM Disponible: {ram.available / (1024**3):.1f} GB")
    except:
        print("   ❌ No se pudo obtener información de RAM")
    
    try:
        import pynvml
        pynvml.nvmlInit()
        count = pynvml.nvmlDeviceGetCount()
        if count > 0:
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            name = pynvml.nvmlDeviceGetName(handle)
            print(f"   ✅ GPU Detectada: {name}")
        else:
            print("   ⚠️ No se detectaron GPUs NVIDIA")
    except:
        print("   ℹ️ pynvml no disponible o sin GPU NVIDIA")

def main():
    """Punto de entrada principal."""
    print("="*50)
    print("  🔍 DIAGNÓSTICO DEL SISTEMA")
    print("="*50)
    
    check_python()
    check_dependencies()
    check_hardware()
    
    print("\n" + "="*50)
    print("✅ Diagnóstico completado")

if __name__ == "__main__":
    main()