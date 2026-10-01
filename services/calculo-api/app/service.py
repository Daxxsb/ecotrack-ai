"""Lógica pura del motor de cálculo y validación (C8). No depende de FastAPI."""
from app.catalog import FACTORES, FUENTES, SUPUESTOS
from app.models import Actividad, Linea, ResultadoCalculo

VEHICULOS = {"camioneta", "camion", "carro", "moto"}
COMBUSTIBLES = {"diesel", "gasolina"}


def calcular_linea(act: Actividad) -> Linea:
    """Regla: kg CO2e = cantidad × factor, redondeado a 2 decimales."""
    info = FACTORES[act.tipo]
    return Linea(tipo=act.tipo, actividad=info["etiqueta"], categoria=info["categoria"],
                 cantidad=act.cantidad, unidad=info["unidad"], factor=info["factor"],
                 kg_co2e=round(act.cantidad * info["factor"], 2), supuesto=act.supuesto)


def generar_advertencias(actividades: list[Actividad]) -> list[str]:
    """Reglas de validación: doble conteo y datos asumidos."""
    tipos = {a.tipo for a in actividades}
    advertencias = []
    if tipos & VEHICULOS and tipos & COMBUSTIBLES:
        advertencias.append(
            "Posible doble conteo: reportaste km de vehículos y también litros de combustible. "
            "Si el combustible es de esos mismos vehículos, reporta solo uno de los dos "
            "(el combustible es más preciso).")
    if any(a.supuesto for a in actividades):
        advertencias.append(
            f"Algunas cantidades fueron asumidas (p. ej. {SUPUESTOS['km_por_vehiculo_dia']} km por "
            "vehículo). Ingresa los valores reales para afinar el cálculo.")
    return advertencias


def calcular(actividades: list[Actividad]) -> ResultadoCalculo:
    """Flujo: factores → líneas → agregados y proyección → advertencias."""
    lineas = [calcular_linea(a) for a in actividades]

    por_categoria: dict[str, float] = {}
    for l in lineas:
        por_categoria[l.categoria] = round(por_categoria.get(l.categoria, 0.0) + l.kg_co2e, 2)

    total = round(sum(l.kg_co2e for l in lineas), 2)
    proyeccion_kg = round(total * SUPUESTOS["dias_laborales_mes"], 2)
    arboles = round(proyeccion_kg * 12 / SUPUESTOS["kg_co2_absorbidos_por_arbol_anio"])

    return ResultadoCalculo(
        lineas=lineas, total_kg=total, por_categoria=por_categoria,
        proyeccion_mensual_kg=proyeccion_kg, proyeccion_mensual_t=round(proyeccion_kg / 1000, 2),
        arboles_equivalentes=arboles, advertencias=generar_advertencias(actividades),
        fuentes=FUENTES)
