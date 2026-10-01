"""Acceso al catálogo de factores de emisión (componente C7)."""
import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "emission_factors.json"


def cargar_catalogo(path: Path = DATA_PATH) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


CATALOGO = cargar_catalogo()
FACTORES: dict = CATALOGO["factores"]
SUPUESTOS: dict = CATALOGO["supuestos"]
FUENTES: str = CATALOGO["_fuentes"]
TIPOS_VALIDOS: list[str] = sorted(FACTORES)
