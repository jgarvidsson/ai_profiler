#!/usr/bin/env python3
"""
Punto de entrada para la aplicación GUI.
"""

import sys
from pathlib import Path

root = Path(__file__).parent
sys.path.insert(0, str(root))
sys.path.insert(0, str(root / "src"))

from gui.app import main

if __name__ == "__main__":
    main()