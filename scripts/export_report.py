#!/usr/bin/env python3
"""
Script para exportar reportes en diferentes formatos.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.recommendation_engine import RecommendationEngine

def export_json(engine):
    """Exporta a JSON."""
    results = engine.evaluate_models()
    filename = f"reporte_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Reporte JSON exportado: {filename}")

def export_text(engine):
    """Exporta a texto."""
    report = engine.generate_report()
    filename = f"reporte_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"✅ Reporte texto exportado: {filename}")

def main():
    """Punto de entrada principal."""
    print("="*50)
    print("  EXPORTADOR DE REPORTES")
    print("="*50)
    
    engine = RecommendationEngine()
    
    print("\nFormatos disponibles:")
    print("1. JSON")
    print("2. Texto")
    print("3. Ambos")
    
    choice = input("\nSelecciona formato (1-3): ").strip()
    
    if choice == "1":
        export_json(engine)
    elif choice == "2":
        export_text(engine)
    elif choice == "3":
        export_json(engine)
        export_text(engine)
    else:
        print("❌ Opción inválida")

if __name__ == "__main__":
    main()