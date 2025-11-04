import os, base64
import numpy as np
import streamlit as st
from PIL import Image
from openai import OpenAI

# ---------- Página y tema (negro/blanco) ----------
st.set_page_config(page_title="Análisis de Imagen", layout="centered", initial_sidebar_state="collapsed")
st.markdown("""
<style>
  html, body, [data-testid="stAppViewContainer"] { background: #000 !important; color: #fff !important; }
  [data-testid="stHeader"] { background: transparent !important; }
  .stTextInput > div > div > input, textarea, .stFileUploader, .stButton button {
    background:#0a0a0a !important; color:#fff !important; border:1px solid #333 !important;
  }
  .stAlert { background:#140000 !important; }
</style>
""", unsafe_allow_html=True)

st.title("Análisis de Imagen: 🤖🏞️")

# ---------- Key: Secrets primero, luego input ----------
key_from_secrets = st.secrets.get("OPENAI_API_KEY", "").strip() if "OPENAI_API_KEY" in st.secrets else ""
key_input = st.text_input("Ingresa tu Clave (recomendado usar Secrets)", type="password").strip()
api_key = (key_from_secrets or key_input).strip()

def looks_like_key(k: str) -> bool:
    if not k: return False
    return (k.startswith("sk-proj-") or k.startswith("sk-")) and len(k) > 30

if not api_key:
    st.info("Pega tu API Key y presiona Enter (o configúrala en Settings → Secrets como OPENAI_API_KEY).")
else:
    if not looks_like_key(api_key):
        st.warning("Tu API key **no luce válida**. Asegúrate de copiarla completa del modal (prefijo `sk-proj-` o `sk-`) y sin espacios ocultos.")

# ---------- UI principal (siempre visible) ----------
uploaded_file = st.file_uploader("Sube una imagen (JPG/PNG/JPEG)", type=["jpg", "jpeg", "png"])
with st.expander("Imagen", expanded=True):
    if uploaded_file:
        st.image(uploaded_file, caption=uploaded_file.name, width="stretch")

ask_toggle = st.toggle("Pregunta algo específico sobre la imagen", value=False)
extra = st.text_area("Añade contexto de la imagen aquí:", disabled=not ask_toggle)

analyze = st.button("Analiza la imagen", type="secondary")

# ---------- Acción ----------
def encode_image(file) -> str:
    return base64.b64encode(file.getvalue()).decode("utf-8")

if analyze:
    if not api_key:
        st.error("No hay API key. Pégala arriba o añádela a Secrets.")
        st.stop()

    # Configura el cliente: por env var (más estándar con openai>=1.x)
    os.environ["OPENAI_API_KEY"] = api_key
    client = OpenAI()  # leerá la key del entorno

    if not uploaded_file:
        st.warning("Primero sube una imagen.")
        st.stop()

    base64_image = encode_image(uploaded_file)
    prompt = "Describe lo que ves en la imagen en español."
    if ask_toggle and extra:
        prompt += f"\n\nContexto adicional del usuario:\n{extra}"

    messages = [{
        "role": "user",
        "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url",
             "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
        ],
    }]

    with st.spinner("Analizando..."):
        try:
            # Puedes usar gpt-4o o gpt-4o-mini para más barato/rápido
            stream = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=800,
                stream=True,
            )
            full = ""
            ph = st.empty()
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    full += delta
                    ph.markdown(full + "▌")
            ph.markdown(full)
        except Exception as e:
            # Errores típicos: invalid_api_key, insufficient_quota, etc.
            msg = str(e)
            if "invalid_api_key" in msg or "Incorrect API key" in msg:
                st.error("Tu API key no es válida o está mal pegada. Copia la **clave completa** del modal (no la enmascarada) y sin espacios.")
            elif "insufficient_quota" in msg or "billing" in msg.lower():
                st.error("No hay créditos en tu cuenta/proyecto. Ve a **Billing → Add credits**.")
            else:
                st.error(f"Ocurrió un error: {e}")
