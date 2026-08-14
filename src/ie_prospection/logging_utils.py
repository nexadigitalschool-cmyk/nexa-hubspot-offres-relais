"""Configuration du journal d'exécution.

Écrit à la fois sur la console et dans un fichier horodaté sous ``reports/``.
"""
from __future__ import annotations

import logging
from pathlib import Path


def setup_logging(reports_dir: str | Path, run_id: str, level: int = logging.INFO) -> Path:
    reports_dir = Path(reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)
    log_path = reports_dir / f"run_{run_id}.log"

    logger = logging.getLogger("ie_prospection")
    logger.setLevel(level)
    logger.handlers.clear()

    fmt = logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s")

    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    logger.propagate = False
    return log_path


def get_logger() -> logging.Logger:
    return logging.getLogger("ie_prospection")
