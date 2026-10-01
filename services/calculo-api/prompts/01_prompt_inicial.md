Quiero que generes el código de un componente llamado: C8 – Motor de cálculo y validación (EcoTrack AI)
Tipo: Servicio
Lenguaje/Framework preferido: Python 3.11 + FastAPI + Pydantic v2, pruebas con pytest

Especificación del componente:
- Propósito: calcular las emisiones de forma determinística y generar métricas y advertencias.
- Entradas: actividades extraídas por C4 (tipo, cantidad, supuesto); factores de emisión de C7 (data/emission_factors.json, 13 tipos con factor, unidad, etiqueta y categoría).
- Salidas: líneas (actividad, cantidad, kg CO2e), total diario, total por categoría, proyección mensual, árboles equivalentes y advertencias.
- Reglas de negocio:
  - kg CO2e = cantidad × factor; redondeo a 2 decimales.
  - Proyección mensual = total diario × 26 días laborales.
  - Árboles = (proyección × 12) ÷ 22 kg por árbol al año.
  - Si hay km de vehículos y litros de combustible a la vez, advertir posible doble conteo.
  - Si hay supuestos, advertir y pedir los datos reales.
- Flujo principal: 1) Recibe las actividades. 2) Busca el factor de cada tipo. 3) Calcula línea por línea. 4) Agrega por categoría y proyecta. 5) Genera advertencias.
- RNF clave: exactitud (mismo input → mismo resultado), trazabilidad (cada factor tiene fuente: EPA, DEFRA, UPME), calidad (pruebas automatizadas).
- Criterios de aceptación:
  - Dado camioneta = 400 km y electricidad = 200 kWh, cuando se calcula, entonces total = 126,0 kg, proyección = 3,28 t/mes y árboles = 1.787.
  - Dado km de camionetas y 40 litros de diésel, cuando se calcula, entonces aparece la advertencia de doble conteo.

Requerimientos adicionales para el código:
- Código modular y comentado.
- Buenas prácticas de FastAPI.
- Pruebas unitarias básicas incluidas.
- Documentación mínima (README corto con instrucciones de ejecución).
