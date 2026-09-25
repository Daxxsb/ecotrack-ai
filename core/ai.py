"""Capa de IA de EcoTrack AI.

1. extract(): convierte la descripción del negocio en actividades estructuradas.
2. recommend(): genera recomendaciones accionables a partir del análisis.

Modo real: si existe ANTHROPIC_API_KEY u OPENAI_API_KEY, se usa un LLM con salida JSON.
Modo simulado: si no hay clave o la respuesta es inválida, un motor NLP por reglas
imita la extracción para que el MVP funcione siempre.
"""
from __future__ import annotations

import json
import os
import re
import unicodedata

from core.calculator import ASSUMPTIONS, FACTORS, Activity, Analysis

# ---------------------------------------------------------------- utilidades

WORD_NUMBERS = {"un": 1, "una": 1, "uno": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5,
                "seis": 6, "siete": 7, "ocho": 8, "nueve": 9, "diez": 10}
NUM = r"(\d+(?:[.,]\d+)?|" + "|".join(WORD_NUMBERS) + r")"


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in text if not unicodedata.combining(c))


def to_number(raw: str) -> float:
    raw = raw.strip()
    if raw in WORD_NUMBERS:
        return float(WORD_NUMBERS[raw])
    return float(raw.replace(",", "."))


def ai_mode() -> str:
    if os.getenv("ANTHROPIC_API_KEY"):
        return "IA real (Claude)"
    if os.getenv("OPENAI_API_KEY"):
        return "IA real (GPT-4o)"
    return "IA simulada (NLP por reglas)"


# ---------------------------------------------------------------- motor simulado

VEHICLES = {
    "camioneta": r"camionetas?|furgon(?:es|etas?)?|vans?",
    "camion": r"camion(?:es)?",
    "carro": r"carros?|autos?|vehiculos? particulares?",
    "moto": r"motos?|motocicletas?",
}

QUANTITY_RULES = [
    ("electricidad", NUM + r"\s*(?:kwh|kilovatios?)"),
    ("diesel",       NUM + r"\s*(?:litros?|l)\s+de\s+(?:diesel|acpm)"),
    ("gasolina",     NUM + r"\s*(?:litros?|l)\s+de\s+gasolina"),
    ("diesel",       NUM + r"\s*galon(?:es)?\s+de\s+(?:diesel|acpm)"),
    ("gasolina",     NUM + r"\s*galon(?:es)?\s+de\s+gasolina"),
    ("gas_natural",  NUM + r"\s*(?:m3|metros? cubicos?)\s+de\s+gas"),
    ("glp",          NUM + r"\s*(?:kg|kilos?)\s+de\s+(?:gas propano|propano|glp|gas)"),
    ("residuos",     NUM + r"\s*(?:kg|kilos?)\s+de\s+(?:basura|residuos|desechos)"),
    ("papel",        NUM + r"\s*resmas?"),
    ("agua",         NUM + r"\s*(?:m3|metros? cubicos?)\s+de\s+agua"),
    ("vuelo",        NUM + r"\s*km\s+(?:en\s+)?(?:avion|vuelo)"),
]
GALLON_TO_LITER = 3.785


def extract_simulated(text: str) -> list[Activity]:
    """Extracción por reglas: vehículos (con o sin km) y consumos con unidad explícita."""
    norm = normalize(text)
    activities: list[Activity] = []

    for tipo, rule in QUANTITY_RULES:
        for m in re.finditer(rule, norm):
            qty = to_number(m.group(1))
            detalle = m.group(0)
            if "galon" in m.group(0):
                qty = round(qty * GALLON_TO_LITER, 2)
                detalle += f" → {qty} litros"
            activities.append(Activity(tipo, qty, detalle))

    for tipo, pattern in VEHICLES.items():
        for m in re.finditer(NUM + r"\s+(?:" + pattern + r")\b", norm):
            count = to_number(m.group(1))
            tail = norm[m.end(): m.end() + 60]
            km_match = re.search(NUM + r"\s*(?:km|kilometros?)", tail)
            if km_match:
                km = to_number(km_match.group(1))
                each = bool(re.search(r"cada un[oa]|por vehiculo|c/u", tail))
                total = km * count if each else km
                detalle = f"{count:g} vehículos × {km:g} km" if each else f"{km:g} km en total"
                activities.append(Activity(tipo, total, detalle))
            else:
                km = ASSUMPTIONS["km_por_vehiculo_dia"]
                activities.append(Activity(tipo, count * km, f"{count:g} vehículos × {km} km (promedio)", True))
    return activities


# ---------------------------------------------------------------- motor LLM

EXTRACT_PROMPT = """Eres el motor de extracción de EcoTrack AI. Del texto de un pequeño negocio,
extrae sus actividades del día y responde SOLO con JSON válido:
{{"actividades": [{{"tipo": "...", "cantidad": 0, "detalle": "...", "supuesto": false}}]}}
Tipos permitidos y unidad de "cantidad": {tipos}.
Reglas: convierte galones a litros (×3.785). Para vehículos sin distancia, asume
{km} km por vehículo y marca "supuesto": true. No inventes actividades no mencionadas.
Texto: {text}"""

RECOMMEND_PROMPT = """Eres un consultor de sostenibilidad para pequeños negocios en Colombia.
Con este análisis de emisiones diarias (kg CO2e): {data}
Da exactamente 3 recomendaciones concretas, breves y de bajo costo, priorizando la mayor fuente.
Responde SOLO con JSON: {{"recomendaciones": ["...", "...", "..."]}}"""


def _call_llm(prompt: str) -> str | None:
    if os.getenv("ANTHROPIC_API_KEY"):
        import anthropic
        msg = anthropic.Anthropic().messages.create(
            model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest"),
            max_tokens=700, messages=[{"role": "user", "content": prompt}])
        return msg.content[0].text
    if os.getenv("OPENAI_API_KEY"):
        from openai import OpenAI
        resp = OpenAI().chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"})
        return resp.choices[0].message.content
    return None


def _parse_json(raw: str | None) -> dict | None:
    if not raw:
        return None
    try:
        return json.loads(raw[raw.find("{"): raw.rfind("}") + 1])
    except (ValueError, TypeError):
        return None


def extract(text: str) -> list[Activity]:
    """LLM primero; motor simulado como respaldo."""
    tipos = ", ".join(f"{k} ({v['unidad']})" for k, v in FACTORS.items())
    try:
        data = _parse_json(_call_llm(EXTRACT_PROMPT.format(
            tipos=tipos, km=ASSUMPTIONS["km_por_vehiculo_dia"], text=text)))
        if data and data.get("actividades"):
            return [Activity(a["tipo"], float(a["cantidad"]), a.get("detalle", ""),
                             bool(a.get("supuesto", False)))
                    for a in data["actividades"] if a.get("tipo") in FACTORS]
    except Exception:
        pass
    return extract_simulated(text)


# ---------------------------------------------------------------- recomendaciones

RULE_TIPS = {
    "Transporte": "Optimiza las rutas de reparto agrupando entregas por zona: reducir un 15% los km recorridos baja en la misma proporción las emisiones de la flota.",
    "Combustibles": "Revisa presión de llantas y mantenimiento de motores: un vehículo bien calibrado consume hasta 10% menos combustible.",
    "Energía": "Cambia a iluminación LED y apaga equipos fuera de horario; en comercios suele reducir 20-30% el consumo eléctrico.",
    "Residuos": "Separa en la fuente y vende o dona el material aprovechable (cartón, plástico): lo que no llega al relleno no emite metano.",
    "Insumos": "Digitaliza facturas y documentos internos para reducir el consumo de papel.",
}


def recommend(analysis: Analysis) -> list[str]:
    """Recomendaciones con LLM si hay clave; si no, reglas ordenadas por impacto."""
    try:
        payload = json.dumps(analysis.por_categoria, ensure_ascii=False)
        data = _parse_json(_call_llm(RECOMMEND_PROMPT.format(data=payload)))
        if data and data.get("recomendaciones"):
            return data["recomendaciones"][:3]
    except Exception:
        pass
    ordered = sorted(analysis.por_categoria.items(), key=lambda kv: kv[1], reverse=True)
    tips = [RULE_TIPS[c] for c, kg in ordered if kg > 0 and c in RULE_TIPS]
    return tips[:3]
