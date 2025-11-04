import os
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Analisis de imagen", layout="centered", initial_sidebar_state="collapsed")
st.title("Análisis de Imagen:🤖🏞️")

# 1) intenta leer de Secrets; 2) si no hay, usa el input
ke_ui = st.text_input("Ingresa tu Clave (recomendado usar Secrets)", type="password").strip()
ke = (st.secrets.get("OPENAI_API_KEY", "") or ke_ui).strip()

if not ke:
    st.warning("Ingresa tu API key o configúrala en Secrets.")
    st.stop()

os.environ["OPENAI_API_KEY"] = ke
client = OpenAI()  # ya toma la key del entorno
