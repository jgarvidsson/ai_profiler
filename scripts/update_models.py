#!/usr/bin/env python3
"""
Script para actualizar la base de datos de modelos desde repositorio remoto.
"""

import json
import requests
import sys
from pathlib import Path
from datetime import datetime

# Añadir src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.model_database import ModelDatabase

def update_database():
    """Actualiza la base de datos de modelos."""
    print("🔄 Actualizando base de datos de modelos...")
    
    # Intentar obtener desde URL remota
    remote_url = "https://raw.githubusercontent.com/tu-usuario/llm-requirements/main/models_db.json"
    
    try:
        response = requests.get(remote_url, timeout=10)
        if response.status_code == 200:
            remote_data = response.json()
            
            # Guardar en data/
            data_dir = Path(__file__).parent.parent / "data"
            data_dir.mkdir(exist_ok=True)
            
            with open(data_dir / "models_db.json", "w", encoding="utf-8") as f:
                json.dump(remote_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Base de datos actualizada: {len(remote_data)} modelos")
            return True
        else:
            print(f"⚠️ No se pudo obtener: Status {response.status_code}")
    except Exception as e:
        print(f"⚠️ Error: {e}")
    
    print("ℹ️ Usando base de datos local")
    return False

def main():
    """Punto de entrada principal."""
    print("="*50)
    print("  ACTUALIZADOR DE BASE DE MODELOS")
    print("="*50)
    
    success = update_database()
    
    if success:
        print("\n✅ Actualización completada")
    else:
        print("\n⚠️ Actualización fallida, usando datos locales")
    
    print(f"\n📅 Última comprobación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()