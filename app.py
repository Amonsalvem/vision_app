import streamlit as st
from openai import OpenAI

# --- API key solo desde Secrets o input local oculto ---
api_key = st.secrets.get("OPENAI_API_KEY", "")

# (Opcional) permitir pegar temporalmente una key durante pruebas
ke = st.text_input("Ingresa tu Clave (recomendado usar Secrets)", type="password")
if ke.strip():
    api_key = ke.strip()

if not api_key:
    st.warning("Por favor ingresa tu API key en Secrets o en el campo de arriba.")
    st.stop()

client = OpenAI(api_key=api_key)

# (Opcional) verificación rápida
try:
    client.models.list()
except Exception:
    st.error("Tu API key no es válida o no tiene permisos. Revisa Billing/Projects o vuelve a pegarla.")
    st.stop()
