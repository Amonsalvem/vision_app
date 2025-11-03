import os
import re
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Analisis de imagen", layout="centered", initial_sidebar_state="collapsed")
st.title("Análisis de Imagen:🤖🏞️")

# 1) Leer de Secrets primero
raw_key = st.secrets.get("OPENAI_API_KEY", "")

# 2) Si no hay en Secrets, permitir input manual (para pruebas locales)
if not raw_key:
    raw_key = st.text_input("Ingresa tu Clave (recomendado usar Secrets)", type="password")

# 3) Normalizar: quitar espacios/quotes ocultos
def normalize(k: str) -> str:
    if not k:
        return ""
    k = k.strip()              # espacios y \n a los lados
    k = k.strip('"').strip("'")# comillas sobrantes
    k = re.sub(r"\s+", "", k)  # espacios/saltos incrustados
    return k

API_KEY = normalize(raw_key)

# 4) Validación rápida de formato
if not (API_KEY.startswith("sk-") and len(API_KEY) > 40):
    st.error("Tu API key no luce válida. Revisa que pegaste la **clave completa** del modal (no la enmascarada) y que no tenga espacios ocultos.")
    st.stop()

# 5) Instanciar cliente
client = OpenAI(api_key=API_KEY)

# 6) Ping de diagnóstico: si falla aquí, es clave o proyecto
try:
    _ = client.models.list()
except Exception as e:
    st.error(f"No pude autenticar con OpenAI. Detalle: {e}")
    st.stop()
