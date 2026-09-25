"""EcoTrack AI – v1 (primera generación, estilo por defecto)."""
import streamlit as st

from core.ai import ai_mode, extract, recommend
from core.calculator import analyze

st.set_page_config(page_title="EcoTrack AI", layout="wide")
st.title("EcoTrack AI")
st.write("Describe las actividades de tu negocio y calcula la huella de carbono.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

prompt = st.chat_input("Ej: Hoy usamos 5 camionetas de reparto y gastamos 200kWh de luz")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    analysis = analyze(extract(prompt))
    with st.chat_message("assistant"):
        if not analysis.lines:
            st.write("No encontré actividades.")
        else:
            st.table([{"Actividad": l.etiqueta, "Cantidad": l.cantidad, "Unidad": l.unidad, "kg CO2e": l.kg}
                      for l in analysis.lines])
            st.write(f"Total: {analysis.total_kg} kg CO2e")
            for tip in recommend(analysis):
                st.write("- " + tip)
    st.session_state.messages.append({"role": "assistant", "content": f"Total: {analysis.total_kg} kg CO2e"})

st.caption(ai_mode())
