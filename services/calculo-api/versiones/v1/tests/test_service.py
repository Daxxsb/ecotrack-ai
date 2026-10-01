"""Pruebas unitarias del motor de cálculo (criterios de aceptación de la spec)."""
from fastapi.testclient import TestClient

from app.main import app
from app.models import Actividad
from app.service import calcular

client = TestClient(app)


def test_caso_base_126_kg():
    r = calcular([Actividad(tipo="camioneta", cantidad=400, supuesto=True),
                  Actividad(tipo="electricidad", cantidad=200)])
    assert r.total_kg == 126.0
    assert r.proyeccion_mensual_kg == 3276.0
    assert r.arboles_equivalentes == 1787


def test_advertencia_doble_conteo():
    r = calcular([Actividad(tipo="camioneta", cantidad=360), Actividad(tipo="diesel", cantidad=40)])
    assert any("doble conteo" in a for a in r.advertencias)


def test_endpoint_calcular():
    resp = client.post("/calcular", json={"actividades": [{"tipo": "electricidad", "cantidad": 100}]})
    assert resp.status_code == 200
    assert resp.json()["total_kg"] == 13.0
