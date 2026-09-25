"""Pruebas de regresión del motor de extracción y cálculo (modo simulado)."""
from core.ai import extract_simulated
from core.calculator import analyze


def total(text: str) -> float:
    return analyze(extract_simulated(text)).total_kg


def test_caso_enunciado():
    # 5 camionetas × 80 km × 0.25 + 200 kWh × 0.13 = 100 + 26
    assert total("Hoy usamos 5 camionetas de reparto y gastamos 200kWh de luz") == 126.0


def test_camionetas_no_se_cuentan_como_camion():
    # Regresión del bug: "camion" era prefijo de "camioneta" y duplicaba emisiones (486 kg)
    tipos = [a.tipo for a in extract_simulated("Usamos 5 camionetas")]
    assert tipos == ["camioneta"]


def test_km_cada_uno():
    assert total("Tenemos 2 camiones que hicieron 300 km cada uno") == 540.0


def test_galones_a_litros():
    acts = extract_simulated("compramos 10 galones de gasolina")
    assert acts[0].tipo == "gasolina" and acts[0].cantidad == 37.85


def test_advertencia_doble_conteo():
    a = analyze(extract_simulated("3 camionetas recorrieron 120 km cada una y cargamos 40 litros de diésel"))
    assert any("dos veces" in w for w in a.advertencias)


def test_texto_sin_actividades():
    assert analyze(extract_simulated("Hoy fue un buen día")).lines == []
