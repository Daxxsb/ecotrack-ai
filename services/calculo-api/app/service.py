"""Lógica de negocio del motor de cálculo y validación (C8)."""
import json
from pathlib import Path

from app.models import Actividad, Linea, ResultadoCalculo

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "emission_factors.json"

DIAS_LABORALES_MES = 26
KG_CO2_POR_ARBOL_ANIO = 22
VEHICULOS = {"camioneta", "camion", "carro", "moto"}
COMBUSTIBLES = {"diesel", "gasolina"}


def cargar_factores(path: Path = DATA_PATH) -> dict:
    """Carga el catálogo de factores de emisión (C7)."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


CATALOGO = cargar_factores()


def calcular(actividades: list[Actividad]) -> ResultadoCalculo:
    """Calcula emisiones, métricas agregadas y advertencias."""
    factores = CATALOGO["factores"]
    lineas: list[Linea] = []
    por_categoria: dict[str, float] = {}

    # 1-3) Buscar el factor de cada tipo y calcular línea por línea
    for act in actividades:
        info = factores[act.tipo]
        kg = round(act.cantidad * info["factor"], 2)
        lineas.append(Linea(actividad=info["etiqueta"], categoria=info["categoria"],
                            cantidad=act.cantidad, unidad=info["unidad"], kg_co2e=kg))
        por_categoria[info["categoria"]] = round(por_categoria.get(info["categoria"], 0) + kg, 2)

    # 4) Agregar y proyectar
    total = round(sum(l.kg_co2e for l in lineas), 2)
    proyeccion = round(total * DIAS_LABORALES_MES, 2)
    arboles = round(proyeccion * 12 / KG_CO2_POR_ARBOL_ANIO)

    # 5) Advertencias
    tipos = {a.tipo for a in actividades}
    advertencias = []
    if tipos & VEHICULOS and tipos & COMBUSTIBLES:
        advertencias.append("Posible doble conteo: reportaste km de vehículos y litros de combustible.")
    if any(a.supuesto for a in actividades):
        advertencias.append("Algunos datos fueron asumidos. Ingresa los valores reales para mayor precisión.")

    return ResultadoCalculo(lineas=lineas, total_kg=total, por_categoria=por_categoria,
                            proyeccion_mensual_kg=proyeccion, arboles_equivalentes=arboles,
                            advertencias=advertencias, fuentes=CATALOGO["_fuentes"])
