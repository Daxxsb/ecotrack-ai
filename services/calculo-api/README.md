# C8 – Motor de cálculo y validación (EcoTrack AI)

Microservicio **FastAPI** que recibe actividades estructuradas (salida del componente C4) y devuelve las emisiones en kg CO₂e con desglose, proyección, árboles equivalentes y advertencias. La lógica es determinística: `kg CO₂e = cantidad × factor` (factores con fuente en `data/emission_factors.json`).

## Ejecutar
```bash
cd services/calculo-api
pip install -r requirements.txt
uvicorn app.main:app --reload      # documentación interactiva en http://localhost:8000/docs
pytest -q                          # 10 pruebas
```

## Ejemplo
`POST /calcular`
```json
{"actividades": [{"tipo": "camioneta", "cantidad": 400, "supuesto": true},
                 {"tipo": "electricidad", "cantidad": 200}]}
```
Respuesta (resumen; completa en `versiones/ejemplo_respuesta.json`):
`total_kg: 126.0 · proyeccion_mensual_t: 3.28 · arboles_equivalentes: 1787` + líneas con `factor` y advertencia de supuestos.

## Errores (HTTP 422, en español)
| Caso | Mensaje |
|---|---|
| Tipo fuera del catálogo | `tipo 'x' no existe. Tipos válidos: ...` |
| Cantidad ≤ 0 | `debe ser mayor que 0` |
| Cantidad > 1.000.000 | `debe ser menor o igual a 1.000.000` |
| Lista vacía / > 50 | `debe tener al menos 1 actividad` / `admite máximo 50 actividades` |
| Cantidad no numérica | `debe ser un número` |

## Estructura
- `app/catalog.py` – catálogo de factores (C7) · `app/models.py` – validación · `app/service.py` – lógica pura · `app/main.py` – API y errores
- `prompts/` – prompt inicial y refinado · `versiones/` – código v1, revisión de casos límite v1 vs v2
