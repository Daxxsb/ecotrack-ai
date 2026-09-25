"""Cálculo determinístico de emisiones y métricas de análisis para el negocio."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "emission_factors.json"


@dataclass
class Activity:
    """Actividad estructurada extraída del texto del usuario."""
    tipo: str                 # clave en emission_factors.json (ej. "camioneta")
    cantidad: float           # en la unidad del factor (km, kWh, litro...)
    detalle: str = ""         # cómo se interpretó (ej. "5 vehículos × 80 km")
    supuesto: bool = False    # True si se usó un valor por defecto


@dataclass
class Line:
    etiqueta: str
    categoria: str
    cantidad: float
    unidad: str
    kg: float
    detalle: str
    supuesto: bool


@dataclass
class Analysis:
    lines: list[Line] = field(default_factory=list)
    total_kg: float = 0.0
    por_categoria: dict[str, float] = field(default_factory=dict)
    proyeccion_mensual_kg: float = 0.0
    arboles_equivalentes: int = 0
    advertencias: list[str] = field(default_factory=list)


def load_data(path: Path = DATA_PATH) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


DATA = load_data()
FACTORS: dict = DATA["factores"]
ASSUMPTIONS: dict = DATA["supuestos"]


def analyze(activities: list[Activity]) -> Analysis:
    """Multiplica cada actividad por su factor y calcula métricas agregadas."""
    result = Analysis()
    for act in activities:
        info = FACTORS.get(act.tipo)
        if info is None or act.cantidad <= 0:
            continue
        kg = round(act.cantidad * info["factor"], 2)
        result.lines.append(Line(info["etiqueta"], info["categoria"], act.cantidad,
                                 info["unidad"], kg, act.detalle, act.supuesto))
        result.por_categoria[info["categoria"]] = round(result.por_categoria.get(info["categoria"], 0) + kg, 2)

    tipos = {a.tipo for a in activities}
    if tipos & {"diesel", "gasolina"} and tipos & {"camioneta", "camion", "carro", "moto"}:
        result.advertencias.append(
            "Reportaste km de vehículos y también litros de combustible. Si el combustible es de "
            "esos mismos vehículos, la huella de transporte se estaría contando dos veces: "
            "reporta solo uno de los dos (el combustible es más preciso).")
    if any(a.supuesto for a in activities):
        result.advertencias.append(
            f"Algunas distancias no se mencionaron; se asumieron {ASSUMPTIONS['km_por_vehiculo_dia']} km "
            "por vehículo. Dime los km reales para afinar el cálculo.")

    result.total_kg = round(sum(l.kg for l in result.lines), 2)
    result.proyeccion_mensual_kg = round(result.total_kg * ASSUMPTIONS["dias_laborales_mes"], 1)
    anual = result.proyeccion_mensual_kg * 12
    result.arboles_equivalentes = round(anual / ASSUMPTIONS["kg_co2_absorbidos_por_arbol_anio"])
    return result
