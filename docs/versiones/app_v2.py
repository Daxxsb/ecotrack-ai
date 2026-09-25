"""EcoTrack AI – huella de carbono para pequeños negocios, en lenguaje natural."""
import pandas as pd
import streamlit as st

from core.ai import ai_mode, extract, recommend
from core.calculator import ASSUMPTIONS, Analysis, analyze

st.set_page_config(page_title="EcoTrack AI", page_icon="🌿", layout="centered")

st.markdown(
    """
    <style>
    #MainMenu, footer {visibility: hidden;}
    .block-container {padding-top: 2.2rem; max-width: 820px;}
    h1 {font-weight: 700; letter-spacing: -0.02em; color: #1B5E20; margin-bottom: 0;}
    .subtitle {color: #5B6B60; margin-top: .2rem; margin-bottom: 1.2rem;}
    .pill {display:inline-block; padding: .15rem .6rem; border-radius: 999px; font-size: .78rem;
           background:#E8F3EC; color:#2E7D32; border:1px solid #CFE6D6;}
    div[data-testid="stMetric"] {background:#FFFFFF; border:1px solid #DCEBE1; border-radius:14px;
           padding: .8rem 1rem;}
    div[data-testid="stMetricValue"] {color:#1B5E20;}
    .tip {background:#FFFFFF; border-left:4px solid #43A047; border-radius:10px; padding:.6rem .9rem;
          margin-bottom:.5rem; color:#1F2D24;}
    </style>
    """,
    unsafe_allow_html=True,
)

EXAMPLES = [
    "Hoy usamos 5 camionetas de reparto y gastamos 200kWh de luz",
    "Las 3 camionetas recorrieron 120 km cada una y botamos 25 kilos de basura",
    "Gastamos 350 kWh, 12 m3 de gas natural y 2 resmas de papel",
]

# ------------------------------------------------------------------ barra lateral
with st.sidebar:
    st.markdown("### 🌿 Tu negocio")
    negocio = st.text_input("Nombre", value="Mi negocio")
    st.markdown("### Prueba con un ejemplo")
    for ex in EXAMPLES:
        if st.button(ex, use_container_width=True):
            st.session_state.pending = ex
    st.divider()
    st.markdown(f'<span class="pill">Motor: {ai_mode()}</span>', unsafe_allow_html=True)
    st.caption("Agrega ANTHROPIC_API_KEY u OPENAI_API_KEY en Secrets para activar la IA real.")
    if st.button("Nueva conversación", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ------------------------------------------------------------------ encabezado
st.title("EcoTrack AI")
st.markdown('<p class="subtitle">Cuéntame qué hizo tu negocio hoy y te doy su huella de carbono '
            'en segundos. Sin formularios.</p>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []


def render_analysis(analysis: Analysis, tips: list[str]) -> None:
    """Pinta la respuesta completa del asistente (se reutiliza al redibujar el historial)."""
    if not analysis.lines:
        st.markdown("No identifiqué actividades con consumo. Prueba mencionando cantidades, por ejemplo: "
                    "*“3 camionetas de 100 km cada una y 150 kWh de luz”*.")
        return

    c1, c2, c3 = st.columns(3)
    c1.metric("Hoy", f"{analysis.total_kg:,.1f} kg CO₂e")
    c2.metric("Proyección mensual", f"{analysis.proyeccion_mensual_kg / 1000:,.2f} t CO₂e",
              help=f"Hoy × {ASSUMPTIONS['dias_laborales_mes']} días laborales")
    c3.metric("Árboles para compensar", f"{analysis.arboles_equivalentes:,}",
              help=f"Un árbol absorbe ~{ASSUMPTIONS['kg_co2_absorbidos_por_arbol_anio']} kg CO₂ al año")

    df = pd.DataFrame(
        [{"Actividad": l.etiqueta, "Interpretación": l.detalle or f"{l.cantidad:g} {l.unidad}",
          "Cantidad": f"{l.cantidad:,.2f}".rstrip("0").rstrip(".") + f" {l.unidad}",
          "kg CO₂e": round(l.kg, 1)} for l in analysis.lines]
    )
    st.dataframe(df, hide_index=True, use_container_width=True)

    cat = pd.DataFrame({"Categoría": list(analysis.por_categoria),
                        "kg CO₂e": list(analysis.por_categoria.values())}).set_index("Categoría")
    st.bar_chart(cat, color="#43A047", horizontal=True, height=220)

    for warn in analysis.advertencias:
        st.warning(warn, icon="⚠️")

    st.markdown("**Recomendaciones**")
    for tip in tips:
        st.markdown(f'<div class="tip">{tip}</div>', unsafe_allow_html=True)


# ------------------------------------------------------------------ historial
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑‍💼" if msg["role"] == "user" else "🌿"):
        if msg["role"] == "user":
            st.markdown(msg["content"])
        else:
            render_analysis(msg["analysis"], msg["tips"])

if not st.session_state.messages:
    with st.chat_message("assistant", avatar="🌿"):
        st.markdown(f"¡Hola, **{negocio}**! Descríbeme las actividades de hoy: vehículos, kWh de luz, "
                    "combustible, gas, residuos o papel. Yo me encargo del resto.")

# ------------------------------------------------------------------ entrada
prompt = st.chat_input("Ej: Hoy usamos 5 camionetas de reparto y gastamos 200kWh de luz")
prompt = prompt or st.session_state.pop("pending", None)

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍💼"):
        st.markdown(prompt)
    with st.chat_message("assistant", avatar="🌿"):
        with st.spinner("Analizando tus actividades..."):
            analysis = analyze(extract(prompt))
            tips = recommend(analysis)
        render_analysis(analysis, tips)
    st.session_state.messages.append({"role": "assistant", "analysis": analysis, "tips": tips})

st.caption("Estimación con factores de referencia (EPA, DEFRA, UPME). La IA interpreta el texto; "
           "el cálculo es determinístico y trazable.")
