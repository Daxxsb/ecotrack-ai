Revisé la v1 del componente C8 contra la especificación y con casos límite (versiones/revision_v1_salida.txt). Cumple los 2 criterios de aceptación básicos, pero falla en esto:
1. Un tipo desconocido (ej. "helicoptero") provoca HTTP 500.
2. Acepta cantidades negativas y devuelve emisiones negativas.
3. La proyección solo sale en kg; el criterio de aceptación la expresa en t/mes.
4. Las líneas no incluyen el factor usado ni su fuente (incumple el RNF de trazabilidad).
5. Los errores de validación salen en inglés.

Ajusta el componente manteniendo Python 3.11 + FastAPI + Pydantic v2 y estas reglas adicionales:
- Validación de entrada con Pydantic:
  - "tipo" debe ser uno de los 13 tipos del catálogo; si no, HTTP 422 con un mensaje en español que liste los tipos válidos.
  - "cantidad" debe ser > 0 y ≤ 1.000.000.
  - "actividades" debe tener entre 1 y 50 elementos.
- Todos los errores de validación deben salir en español con el formato {"errores": [{"campo": "...", "mensaje": "..."}]}.
- Cada línea de salida debe incluir: tipo, actividad, categoría, cantidad, unidad, factor, kg_co2e y supuesto.
- La respuesta debe incluir proyeccion_mensual_kg y proyeccion_mensual_t (2 decimales).
- Los parámetros (26 días laborales, 22 kg por árbol, km por defecto) se leen del bloque "supuestos" del JSON, sin valores mágicos en el código.
- Advertencia de doble conteo con guía de acción: "reporta solo uno de los dos (el combustible es más preciso)".
- Separar capas: models.py (validación), service.py (lógica pura, sin FastAPI), main.py (API y manejo de errores).
- RNF de rendimiento: el cálculo de 50 actividades debe tardar < 50 ms; inclúyelo como prueba.
- RNF de exactitud: prueba que el mismo input produce el mismo resultado.
- Pruebas con pytest para los 2 criterios de aceptación y para cada uno de los 5 problemas anteriores.
- README con ejecución, ejemplo de request/response y tabla de errores.
