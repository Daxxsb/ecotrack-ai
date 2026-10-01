"""Revisión de la v1 contra la especificación con casos límite."""
from fastapi.testclient import TestClient
from app.main import app
c = TestClient(app, raise_server_exceptions=False)
casos = {
 "tipo desconocido ('helicoptero')": {"actividades": [{"tipo": "helicoptero", "cantidad": 10}]},
 "cantidad negativa": {"actividades": [{"tipo": "electricidad", "cantidad": -50}]},
 "lista vacía": {"actividades": []},
 "cantidad como texto": {"actividades": [{"tipo": "electricidad", "cantidad": "mucho"}]},
}
for nombre, body in casos.items():
    r = c.post("/calcular", json=body)
    print(f"{nombre}: HTTP {r.status_code} -> {r.text[:150]}")
r = c.post("/calcular", json={"actividades":[{"tipo":"camioneta","cantidad":400,"supuesto":True},{"tipo":"electricidad","cantidad":200}]}).json()
print("criterio 3,28 t/mes:", r.get("proyeccion_mensual_t", f"{r['proyeccion_mensual_kg']} (solo kg; la spec pide t)"))
print("factor por línea (trazabilidad):", r["lineas"][0].get("factor", "NO INCLUIDO"), "| advertencias:", r["advertencias"])
