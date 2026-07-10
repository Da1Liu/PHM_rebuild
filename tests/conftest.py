from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "domain" / "src"))
sys.path.insert(0, str(ROOT / "packages" / "health-core" / "src"))
sys.path.insert(0, str(ROOT / "packages" / "application" / "src"))
sys.path.insert(0, str(ROOT / "packages" / "persistence" / "src"))
