import os
import base64
import streamlit as st
from openai import OpenAI

# ---------- Estilos (negro/blanco) ----------
st.set_page_config(page_title="Análisis de imagen", layout="centered", initial_sidebar_state="collapsed")
st.markdown("""
<style>
  .stApp { background:#000; }
  .stMarkdown, .stTextInput, .stFileUploader, .stExpander, .stButton, .stToggle,
  .stAlert, .stCaption, .stTextArea, .stSlider, .stRadio, .stSelectbox { color:#fff; }
  .stTextInput input, textarea { background:#111 !important; color:#fff !important; border:1px solid #333; }
  .stFileUploader > div { background:#111 !important; border:1px dashed #333; }
  .stButton button { background:#111 !important; color:#fff !important; border:1px solid #333; }
  .stExpander { border:1px solid #333; border-radius:8px; }
</style>
""", unsafe_allow_html=True)

st.title("Análisis de Imagen:🤖🏞️")

# ---------- Util ----------
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

def clean(s: str | None) -> str:
    if not s:
        return ""
    # elimina espacios, saltos, y comillas pegadas
    return s.strip().strip('"').strip("'")

# 1) Cargar credenciales de Secrets o entorno
key_from_secrets = st.secrets.get("OPENAI_API_KEY", "") if hasattr(st, "secrets") else ""
org_from_secrets = st.secrets.get("OPENAI_ORG_ID", "") if hasattr(st, "secrets") else ""
proj_from_secrets = st.secrets.get("OPENAI_PROJECT", "") if hasattr(st, "secrets") else ""

api_key = clean(key_from_secrets) or clean(os.getenv("OPENAI_API_KEY"))
org_id  = clean(org_from_secrets) or clean(os.getenv("OPENAI_ORG_ID"))
proj_id = clean(proj_from_secrets) or clean(os.getenv("OPENAI_PROJECT"))

# 2) Si falta algo, permitir ingresarlo manualmente (oculto)
with st.expander("🔑 Credenciales (recomendado usar *Secrets*)", expanded=not bool(api_key)):
    api_key = clean(st.text_input("API Key (sk-...)", type="password", value=api_key)) or api_key
    col_org, col_proj = st.columns(2)
    org_id = clean(col_org.text_input("Organization ID (opcional)", value=org_id))
    proj_id = clean(col_proj.text_input("Project ID (opcional)", value=proj_id))
    st.caption("Consejo: en Streamlit Cloud → *Manage app → Settings → Secrets* guarda: "
               "OPENAI_API_KEY, OPENAI_ORG_ID (si aplica) y OPENAI_PROJECT (si aplica).")

if not api_key:
    st.info("Agrega tu API Key para continuar.")
    st.stop()

# 3) Inicializar cliente con headers adecuados
client_kwargs = {"api_key": api_key}
if org_id:
    client_kwargs["organization"] = org_id
if proj_id:
    # El SDK reconoce 'project' para enrutar la solicitud al proyecto correcto
    client_kwargs["project"] = proj_id

client = OpenAI(**client_kwargs)

# 4) Diagnóstico rápido de clave
def check_key():
    try:
        # llamada ligera para validar permisos; si falla, generará 401/403 claros
        _ = client.models.list()
        return True, "OK"
    except Exception as e:
        return False, str(e)

if st.button("🔍 Probar clave"):
    ok, msg = check_key()
    if ok:
        st.success("Tu API Key respondió correctamente.")
    else:
        if "invalid_api_key" in msg or "Incorrect API key" in msg or "401" in msg:
            st.error("La API Key es inválida o no corresponde al proyecto/organización. "
                     "Verifícala, regenera una nueva y guárdala en *Secrets*.")
        elif "organization" in msg.lower() or "project" in msg.lower() or "permission" in msg.lower() or "403" in msg:
            st.error("La clave existe pero no tiene permisos para el modelo/organización/proyecto configurado. "
                     "Revisa OPENAI_ORG_ID / OPENAI_PROJECT y que el modelo esté habilitado.")
        else:
            st.error(f"Error al validar la clave: {msg}")

# 5) Subida de imagen
uploaded_file = st.file_uploader("Sube una imagen (JPG/PNG/JPEG)", type=["jpg", "jpeg", "png"])
if uploaded_file:
    with st.expander("Imagen", expanded=True):
        st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)

# 6) Pregunta adicional
ask_more = st.toggle("Pregunta algo específico sobre la imagen", value=False)
extra = st.text_area("Añade contexto de la imagen aquí:", disabled=not ask_more) if ask_more else ""

# 7) Análisis
if st.button("Analiza la imagen", type="secondary"):
    if not uploaded_file:
        st.warning("Por favor sube una imagen.")
        st.stop()
    with st.spinner("Analizando ..."):
        try:
            b64 = encode_image(uploaded_file)
            prompt = "Describe lo que ves en la imagen en español."
            if ask_more and extra.strip():
                prompt += f"\n\nContexto adicional del usuario:\n{extra.strip()}"

            messages = [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}" }},
                ],
            }]

            full, box = "", st.empty()
            for chunk in client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=1200,
                stream=True,
            ):
                delta = chunk.choices[0].delta.content
                if delta:
                    full += delta
                    box.markdown(full + "▌")
            box.markdown(full)

        except Exception as e:
            msg = str(e)
            if "invalid_api_key" in msg or "Incorrect API key" in msg or "401" in msg:
                st.error("Tu API Key no es válida o no tiene permisos. Revisa *Secrets* o vuelve a ingresarla.")
            elif "insufficient_quota" in msg or "billing" in msg.lower():
                st.error("No hay cuota o el billing no está activo en esa cuenta/proyecto.")
            else:
                st.error(f"Ocurrió un error: {msg}")
