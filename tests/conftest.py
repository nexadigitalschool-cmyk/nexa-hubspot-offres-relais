import sys
from pathlib import Path

# Garantit l'import du paquet même sans installation editable.
SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
