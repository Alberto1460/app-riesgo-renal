import streamlit as st
from datetime import datetime
from utils_s3 import guardar_en_s3

st.title("🧪 Prueba de Guardado en S3")

nombre = st.text_input("Nombre del paciente")
edad = st.number_input("Edad", min_value=0, step=1)
creatinina = st.number_input("Nivel de creatinina", min_value=0.0, step=0.1)
bun = st.number_input("BUN", min_value=0.0, step=0.1)
diabetes = st.selectbox("¿Tiene diabetes?", ["Sí", "No"])
hipertension = st.selectbox("¿Tiene hipertensión?", ["Sí", "No"])
gfr = st.number_input("GFR", min_value=0.0, step=0.1)
diuresis = st.selectbox("Diuresis", ["Normal", "Reducida", "Aumentada"])
etapa = st.selectbox("Etapa de enfermedad renal", ["Etapa 1", "Etapa 2", "Etapa 3", "Etapa 4", "Etapa 5"])
prediccion = st.selectbox("Predicción", ["0 = Sin daño", "1 = Con daño"])

if st.button("📤 Guardar en S3"):
    registro = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "nombre": nombre,
        "age": edad,
        "creatinine_level": creatinina,
        "bun": bun,
        "diabetes": diabetes,
        "hypertension": hipertension,
        "gfr": gfr,
        "urine_output": diuresis,
        "ckd_status": etapa,
        "prediccion": int(prediccion[0])  # Extraemos el número (0 o 1)
    }

    guardar_en_s3(registro)
    st.success("✅ Registro enviado a S3")
