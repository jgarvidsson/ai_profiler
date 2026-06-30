#!/usr/bin/env python3
"""
Punto de entrada CLI (consola).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from hardware_profiler import HardwareProfiler
from model_database import ModelDatabase
from recommendation_engine import RecommendationEngine

def main():
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    print("[AI] Perfilador de IA - Modo CLI")
    print("="*50)

    profiler = HardwareProfiler()
    print(profiler)

    db = ModelDatabase()
    models = db.get_all_models()
    print(f"\n[DB] Modelos en DB: {len(models)}")

    engine = RecommendationEngine()
    print(engine.generate_report())

if __name__ == "__main__":
    main()