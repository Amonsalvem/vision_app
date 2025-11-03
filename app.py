import os
import streamlit as st
import base64
from openai import OpenAI

st.set_page_config(page_title="Analisis de imagen", layout="centered", initial_sidebar_state="collapsed")
st.title("Análisis de Imagen:🤖🏞️")

# 1) Clave: primero Secrets, luego variable de entorno; opcionalmente input solo si no hay nada
API_KEY = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
if not API_KEY:
    ke = st.text_input("Ingresa tu Clave (recomendado usar Secrets)", type="password")
    if ke:
        API_KEY = ke

if not API_KEY:
    st.error("Tu API key no es válida o no tiene permisos. Revisa Billing/Projects o vuelve a pegarla.")
    st.stop()

client = OpenAI(api_key=API_KEY)

# 2) Ping de diagnóstico: muestra el error real si falla la auth/billing
try:
    _ = client.models.list()
except Exception as e:
    st.error(f"No pude autenticar con OpenAI. Detalle: {e}")
    st.stop()
