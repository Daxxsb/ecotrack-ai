"""API FastAPI del motor de cálculo (C8) con errores en español."""
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.catalog import TIPOS_VALIDOS
from app.models import ResultadoCalculo, SolicitudCalculo
from app.service import calcular

app = FastAPI(title="EcoTrack AI – Motor de cálculo (C8)", version="2.0.0")

MENSAJES = {
    "greater_than": "debe ser mayor que 0",
    "less_than_equal": "debe ser menor o igual a 1.000.000",
    "float_parsing": "debe ser un número",
    "too_short": "debe tener al menos 1 actividad",
    "too_long": "admite máximo 50 actividades",
    "missing": "es obligatorio",
}


@app.exception_handler(RequestValidationError)
async def errores_en_espanol(_: Request, exc: RequestValidationError) -> JSONResponse:
    """Traduce los errores de Pydantic al formato {"errores": [{"campo", "mensaje"}]}."""
    errores = []
    for e in exc.errors():
        campo = ".".join(str(p) for p in e["loc"] if p != "body")
        if e["type"] == "value_error":
            mensaje = str(e["ctx"]["error"])
        else:
            mensaje = MENSAJES.get(e["type"], e["msg"])
        errores.append({"campo": campo, "mensaje": mensaje})
    return JSONResponse(status_code=422, content={"errores": errores})


@app.post("/calcular", response_model=ResultadoCalculo)
def calcular_huella(solicitud: SolicitudCalculo) -> ResultadoCalculo:
    """Recibe actividades estructuradas (de C4) y devuelve el análisis de emisiones."""
    return calcular(solicitud.actividades)


@app.get("/tipos")
def tipos() -> dict:
    return {"tipos_validos": TIPOS_VALIDOS}


@app.get("/salud")
def salud() -> dict:
    return {"estado": "ok"}
