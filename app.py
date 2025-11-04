import os
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Analisis de imagen", layout="centered", initial_sidebar_state="collapsed")
st.title("Análisis de Imagen:🤖🏞️")

# 1) Toma de Secrets si existe; si no, del input
api_from_secrets = st.secrets.get("OPENAI_API_KEY", "").strip() if "OPENAI_API_KEY" in st.secrets else ""
ke = st.text_input("Ingresa tu Clave (recomendado usar Secrets)", type="password").strip()

api_key = (api_from_secrets or ke).strip()

if not api_key:
    st.info("Pega tu API key (o configúrala en Settings → Secrets) y presiona Enter.")
    st.stop()

# Validación visual rápida (longitud ~ 80–100 y prefijo sk-proj-)
if not api_key.startswith("sk-proj-") or len(api_key) < 40:
    st.error("Tu API key no luce válida. Asegúrate de copiarla del modal completo (prefijo sk-proj-) y sin espacios.")
    st.stop()

os.environ["OPENAI_API_KEY"] = api_key
client = OpenAI()  # leerá la key del entorno
