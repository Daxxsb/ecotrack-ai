"""Modelos de entrada y salida del servicio de cálculo (C8)."""
from pydantic import BaseModel


class Actividad(BaseModel):
    """Actividad estructurada que llega desde el servicio de extracción (C4)."""
    tipo: str
    cantidad: float
    supuesto: bool = False


class SolicitudCalculo(BaseModel):
    actividades: list[Actividad]


class Linea(BaseModel):
    actividad: str
    categoria: str
    cantidad: float
    unidad: str
    kg_co2e: float


class ResultadoCalculo(BaseModel):
    lineas: list[Linea]
    total_kg: float
    por_categoria: dict[str, float]
    proyeccion_mensual_kg: float
    arboles_equivalentes: int
    advertencias: list[str]
    fuentes: str
