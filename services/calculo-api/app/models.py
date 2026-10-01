"""Modelos de entrada/salida del servicio de cálculo (C8) con validación de negocio."""
from pydantic import BaseModel, Field, field_validator

from app.catalog import FACTORES, TIPOS_VALIDOS


class Actividad(BaseModel):
    """Actividad estructurada que llega desde el servicio de extracción (C4)."""
    tipo: str = Field(description="Uno de los 13 tipos del catálogo de factores (C7)")
    cantidad: float = Field(gt=0, le=1_000_000, description="Cantidad en la unidad del factor")
    supuesto: bool = Field(default=False, description="True si la cantidad fue asumida por defecto")

    @field_validator("tipo")
    @classmethod
    def tipo_en_catalogo(cls, v: str) -> str:
        v = v.strip().lower()
        if v not in FACTORES:
            raise ValueError(f"tipo '{v}' no existe. Tipos válidos: {', '.join(TIPOS_VALIDOS)}")
        return v


class SolicitudCalculo(BaseModel):
    actividades: list[Actividad] = Field(min_length=1, max_length=50)


class Linea(BaseModel):
    tipo: str
    actividad: str
    categoria: str
    cantidad: float
    unidad: str
    factor: float
    kg_co2e: float
    supuesto: bool


class ResultadoCalculo(BaseModel):
    lineas: list[Linea]
    total_kg: float
    por_categoria: dict[str, float]
    proyeccion_mensual_kg: float
    proyeccion_mensual_t: float
    arboles_equivalentes: int
    advertencias: list[str]
    fuentes: str
