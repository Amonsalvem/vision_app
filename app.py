# app.py
import os
import base64
import numpy as np
import streamlit as st
from PIL import Image
from openai import OpenAI

# =========================
#   ESTILO: NEGRO / BLANCO
# =========================
st.set_page_config(page_title="Análisis de imagen", layout="centered", initial_sidebar_state="collapsed")
st.markdown("""
<style>
/* Fondo negro global */
.stApp, .main, .block-container { background: #000000 !important; }

/* Tipografía base en blanco */
body, .stMarkdown, .stTextInput, .stButton, .stAlert, .stFileUploader, .st-expander, .stRadio, .stCheckbox, .stSelectbox, .stTextArea {
  color: #FFFFFF !important;
}

/* Títulos */
h1, h2, h3, h4, h5, h6 { color: #FFFFFF !important; }

/* Inputs y cajas con borde gris */
div[data-baseweb="input"], textarea, .stTextInput, .stTextArea, .stTextArea textarea, .stFileUploader, .stTextInput input {
  background: #0c0c0c !important;
  color: #FFFFFF !important;
  border: 1px solid #2a2a2a !important;
  border-radius: 10px !important;
}

/* Uploader */
.stFileUploader div[data-testid="stFileUploaderDropzone"] {
  background: #0c0c0c !important;
  border: 1px dashed #2a2a2a !important;
}

/* Expander */
.streamlit-expanderHeader, .st-expanderHeader {
  background: #0c0c0c !important;
  color: #FFFFFF !important;
  border: 1px solid #2a2a2a !important;
  border-radius: 10px !important;
}

/* Botones: blanco sobre negro */
.stButton > button {
  background: #FFFFFF !important;
  color: #000000 !important;
  border-radius: 999px !important;
  border: none !important;
  font-weight: 600 !important;
}
.stButton > button:hover { opacity: 0.9 !important; }

/* Toggles / checkbox */
label, .stCheckbox label, .stToggle label { color: #FFFFFF !important; }

/* Alerts */
.stAlert { background: #111111 !important; border: 1px solid #2a2a2a !important; }

/* Tablas y markdown */
table, th, td { color: #FFFFFF !important; background: #000000 !important; border-color:#2a2a2a !important; }
code, pre { background:#0c0c0c !important; color:#fff !important; }
</style>
""", unsafe_allow_html=True)

# ==============
#   UTILIDAD
# ==============
def encode_image(file):
    return base64.b64encode(file.getvalue()).decode("utf-8")

# =========================
#   CABECERA / API KEY
# =========================
st.title("Análisis de Imagen: 🤖🏞️")

# 1) Primero intenta leer de secrets (recomendado en Streamlit Cloud)
api_key = st.secrets.get("OPENAI_API_KEY") if hasattr(st, "secrets") else None

# 2) Si no existe secret, permite que el usuario la ingrese (oculta)
if not api_key:
    api_key = st.text_input("Ingresa tu API key (OpenAI)", type="password", help="Guárdala en Manage app → Settings → Secrets como OPENAI_API_KEY para no escribirla cada vez.")

if api_key:
    os.environ["OPENAI_API_KEY"] = api_key

# =========================
#   CARGA DE IMAGEN
# =========================
uploaded_file = st.file_uploader("Sube una imagen (JPG, PNG, JPEG)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    with st.expander("Vista de la imagen", expanded=True):
        # ⚠️ sin use_container_width para evitar error en tu runtime
        st.image(uploaded_file, caption=uploaded_file.name)

# =========================
#   CONTEXTO OPCIONAL
# =========================
show_details = st.toggle("Pregunta algo específico sobre la imagen", value=False)
additional_details = ""
if show_details:
    additional_details = st.text_area("Añade contexto sobre la imagen aquí:")

# =========================
#   BOTÓN DE ANÁLISIS
# =========================
analyze = st.button("Analiza la imagen")

# =========================
#   INFERENCIA
# =========================
if analyze:
    if not api_key:
        st.warning("Por favor ingresa tu API key.")
    elif not uploaded_file:
        st.warning("Por favor sube una imagen.")
    else:
        try:
            client = OpenAI(api_key=api_key)

            base64_image = encode_image(uploaded_file)
            prompt_text = "Describe detalladamente lo que ves en la imagen en español."
            if show_details and additional_details.strip():
                prompt_text += f"\n\nContexto adicional del usuario:\n{additional_details.strip()}"

            messages = [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {"type": "image_url",
                     "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                ],
            }]

            full_response = ""
            placeholder = st.empty()
            with st.spinner("Analizando…"):
                for chunk in client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                    max_tokens=1200,
                    stream=True,
                ):
                    delta = chunk.choices[0].delta.content
                    if delta:
                        full_response += delta
                        # Mostrar texto blanco sobre negro
                        placeholder.markdown(f"<div style='color:#fff;'>{full_response}▌</div>", unsafe_allow_html=True)

            placeholder.markdown(f"<div style='color:#fff;'>{full_response}</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Ocurrió un error: {e}")

# =========================
#   AYUDA (opcional)
# =========================
with st.expander("¿Dónde pongo mi API key de forma segura?", expanded=False):
    st.markdown(
        "- En **Streamlit Cloud**: ve a **Manage app → Settings → Secrets** y crea `OPENAI_API_KEY = \"sk-...\"`. "
        "Después dale **Rerun** a la app.\n"
        "- Local: crea `.streamlit/secrets.toml` con:\n\n"
        "```toml\n[default]\nOPENAI_API_KEY = \"sk-xxxx\"\n```"
    )
