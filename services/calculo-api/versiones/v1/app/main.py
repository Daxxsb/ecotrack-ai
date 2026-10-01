"""API FastAPI del motor de cálculo (C8)."""
from fastapi import FastAPI

from app.models import ResultadoCalculo, SolicitudCalculo
from app.service import calcular

app = FastAPI(title="EcoTrack AI – Motor de cálculo (C8)", version="1.0.0")


@app.post("/calcular", response_model=ResultadoCalculo)
def calcular_huella(solicitud: SolicitudCalculo) -> ResultadoCalculo:
    """Recibe actividades estructuradas y devuelve el análisis de emisiones."""
    return calcular(solicitud.actividades)


@app.get("/salud")
def salud() -> dict:
    return {"estado": "ok"}
