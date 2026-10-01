# C8 – Motor de cálculo (EcoTrack AI)

Microservicio FastAPI que calcula emisiones de CO2e a partir de actividades estructuradas.

```bash
pip install fastapi uvicorn pytest httpx
uvicorn app.main:app --reload
pytest -q
```

Endpoint: `POST /calcular` con `{"actividades": [{"tipo": "electricidad", "cantidad": 200}]}`.
