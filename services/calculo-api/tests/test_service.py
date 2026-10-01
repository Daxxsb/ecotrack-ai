"""Pruebas del motor de cálculo: criterios de aceptación, problemas de la v1 y RNF."""
import time

from fastapi.testclient import TestClient

from app.main import app
from app.models import Actividad
from app.service import calcular

client = TestClient(app)
CASO_BASE = [Actividad(tipo="camioneta", cantidad=400, supuesto=True),
             Actividad(tipo="electricidad", cantidad=200)]


# ---------- Criterios de aceptación (Laboratorio 2)
def test_ca1_total_proyeccion_y_arboles():
    r = calcular(CASO_BASE)
    assert r.total_kg == 126.0
    assert r.proyeccion_mensual_t == 3.28
    assert r.arboles_equivalentes == 1787


def test_ca2_advertencia_doble_conteo():
    r = calcular([Actividad(tipo="camioneta", cantidad=360), Actividad(tipo="diesel", cantidad=40)])
    assert any("doble conteo" in a and "combustible es más preciso" in a for a in r.advertencias)


# ---------- Problemas detectados en la v1
def test_p1_tipo_desconocido_da_422_en_espanol():
    resp = client.post("/calcular", json={"actividades": [{"tipo": "helicoptero", "cantidad": 10}]})
    assert resp.status_code == 422
    assert "no existe" in resp.json()["errores"][0]["mensaje"]


def test_p2_cantidad_negativa_rechazada():
    resp = client.post("/calcular", json={"actividades": [{"tipo": "electricidad", "cantidad": -50}]})
    assert resp.status_code == 422
    assert resp.json()["errores"][0]["mensaje"] == "debe ser mayor que 0"


def test_p3_proyeccion_en_toneladas():
    assert calcular(CASO_BASE).proyeccion_mensual_kg == 3276.0


def test_p4_trazabilidad_factor_por_linea():
    linea = calcular(CASO_BASE).lineas[0]
    assert linea.factor == 0.25 and linea.supuesto is True


def test_p5_lista_vacia_rechazada_en_espanol():
    resp = client.post("/calcular", json={"actividades": []})
    assert resp.status_code == 422
    assert resp.json()["errores"][0]["mensaje"] == "debe tener al menos 1 actividad"


# ---------- RNF
def test_rnf_exactitud_determinista():
    assert calcular(CASO_BASE) == calcular(CASO_BASE)


def test_rnf_rendimiento_50_actividades_menos_de_50ms():
    acts = [Actividad(tipo="electricidad", cantidad=i + 1) for i in range(50)]
    inicio = time.perf_counter()
    calcular(acts)
    assert (time.perf_counter() - inicio) * 1000 < 50


def test_endpoint_ok():
    resp = client.post("/calcular", json={"actividades": [{"tipo": "Electricidad", "cantidad": 100}]})
    assert resp.status_code == 200 and resp.json()["total_kg"] == 13.0
