#import os
import os
import base64
import streamlit as st
from openai import OpenAI

# ---------- Util ----------
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

st.set_page_config(page_title="Análisis de imagen", layout="centered", initial_sidebar_state="collapsed")
st.markdown("""
    <style>
      .stApp {background: #000;}
      .stMarkdown, .stTextInput, .stFileUploader, .stExpander, .stButton, .stToggle, .stAlert, .stCaption, .stTextArea {color: #fff;}
      .stTextInput > div > div input, textarea {background:#111 !important; color:#fff !important; border:1px solid #333;}
      .stFileUploader > div {background:#111 !important; border:1px dashed #333;}
      .stButton button {background:#111 !important; color:#fff !important; border:1px solid #333;}
    </style>
""", unsafe_allow_html=True)

st.title("Análisis de Imagen:🤖🏞️")

# 1) Tomamos key desde secrets o entorno
key_from_secrets = st.secrets.get("OPENAI_API_KEY", "") if hasattr(st, "secrets") else ""
key_from_env = os.getenv("OPENAI_API_KEY", "")
api_key = key_from_secrets or key_from_env

# 2) Si no hay key, permitimos ingresarla (oculta)
if not api_key:
    api_key = st.text_input("Ingresa tu API key", type="password", help="Se recomienda usar Secrets para no escribirla cada vez.")

# 3) Si después de todo no hay key, avisamos (no rompemos la app)
if not api_key:
    st.info("Por favor agrega tu API key en *Secrets* o escríbela arriba para continuar.")
    st.stop()

# 4) Inicializamos cliente
client = OpenAI(api_key=api_key)

# 5) Subida de imagen
uploaded_file = st.file_uploader("Sube una imagen (JPG/PNG/JPEG)", type=["jpg", "jpeg", "png"])
if uploaded_file:
    with st.expander("Imagen", expanded=True):
        st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)

# 6) Opcional: pregunta adicional
show_details = st.toggle("Pregunta algo específico sobre la imagen", value=False)
additional_details = ""
if show_details:
    additional_details = st.text_area("Añade contexto de la imagen aquí:")

# 7) Acción
if st.button("Analiza la imagen", type="secondary"):
    if not uploaded_file:
        st.warning("Por favor sube una imagen.")
        st.stop()

    with st.spinner("Analizando ..."):
        try:
            b64 = encode_image(uploaded_file)
            prompt_text = "Describe lo que ves en la imagen en español."
            if show_details and additional_details.strip():
                prompt_text += f"\n\nContexto adicional del usuario:\n{additional_details.strip()}"

            messages = [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                ],
            }]

            # Streaming de respuesta
            full = ""
            placeholder = st.empty()
            for chunk in client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=1200,
                stream=True
            ):
                delta = chunk.choices[0].delta.content
                if delta:
                    full += delta
                    placeholder.markdown(full + "▌")
            placeholder.markdown(full)

        except Exception as e:
            msg = str(e)
            if "invalid_api_key" in msg or "Incorrect API key" in msg or "401" in msg:
                st.error("Tu API key no es válida o no tiene permisos. Verifícala, regenera una nueva y colócala en *Secrets* o en el campo de arriba.")
            else:
                st.error(f"Ocurrió un error: {e}")
