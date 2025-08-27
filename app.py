import streamlit as st
import pandas as pd
import joblib
import numpy as np
import matplotlib.pyplot as plt
import re
from datetime import datetime
from pathlib import Path
from sqlalchemy import create_engine

st.set_page_config(page_title='Prueba Renal', layout='centered')


st.markdown("<h1 style='text-align: center; color: #007BFF;'>🩺" \
"Bienvenido a tu prueba Renal</h1>", unsafe_allow_html=True)
st.write('Por favor, llena los siguientes datos para evaluar tu salud renal.')

# Pedir el nombre del paciente y validarlo
nombre = st.text_input('Nombre del Paciente: ')

if nombre:
     # Validamos solo letras y espacios
    if re.fullmatch(r'[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+', nombre):
          st.success(f'Hola, {nombre} bienvenido a tu prueba renal.')
    else:
         st.error('Por favor, ingresa un nombre válido (solo letras y espacios).')


# Estilo CSS personalizado
st.markdown("---")
st.subheader("📊 Datos de evaluación renal")

# Pedir datos al usuario
age = st.number_input('Edad (años)', min_value=0, max_value=120)
creatinine_level = st.number_input('Nivel de Creatinina (mg/dL)', min_value=0.0)
bun = st.number_input('Nitrógeno Ureico en Sangre - BUN (mg/dL)', min_value=0.0)
diabetes = st.selectbox('¿Tienes diabetes?', ('Si', 'No'))
diabetes = 1 if diabetes == 'Si' else 0
hypertension = st.selectbox('Eres hipertenso?', ('Si', 'No'))
hypertension = 1 if hypertension == 'Si' else 0
gfr = st.number_input('Dame tu Tasa de Filtración Glomerular (GFR)', min_value=0.0)
urine_output = st.number_input('Volumen de Orina (mL/día)', min_value=0.0)
ckd_status = st.selectbox('¿Tienes enfermedad renal crónica (CKD)?', ('Si', 'No'))
ckd_status = 1 if ckd_status == 'Si' else 0


# Cargar el modelo entrenaod
modelo = joblib.load('modelo_renal.pkl')

# Ruta donde se guardará el CSV
ruta_csv = Path('registros_prueba_renal.csv')

# Crear un DataFrame con los datos del usuario
df_usuario = pd.DataFrame([[age, creatinine_level, bun, diabetes, hypertension, 
                            gfr, urine_output, ckd_status]], columns=['age', 
                            'creatinine_level', 'bun', 'diabetes', 'hypertension', 
                            'gfr', 'urine_output', 'ckd_status'])


# Crear columnas para centrar el botón
col1, col2, col3 = st.columns([1, 1, 1])

# Poner el botón en la columna del medio
with col2:
    evaluar = st.button('🔎 Evaluar Riesgo Renal')

# Hacer la predicción con el modelo cargado
if evaluar:
        st.subheader('📋 Datos ingresados:')
        st.write(df_usuario)

        # Predecir y mostrar el resultado
        prediccion = modelo.predict(df_usuario)

        if prediccion[0] == 1:
            st.error('⚠️ Alto riesgo de enfermedad renal. Por favor, consulta a un médico.')
        else:
            st.success('✅ Bajo riesgo de enfermedad renal. ¡Sigue cuidando tu salud!')

        # Guardar los datos en un CSV
        registro = {'timestamp': datetime.now().isoformat(timespec='seconds'),
                    'nombre': nombre,
                    'age': age,
                    'creatinine_level': creatinine_level,
                    'bun': bun,
                    'diabetes': diabetes,
                    'hypertension': hypertension,
                    'gfr': gfr,
                    'urine_output': urine_output,
                    'ckd_status': ckd_status,
                    'prediccion': int(prediccion[0])}
        
        # Convertir en DataFrame
        df_registro = pd.DataFrame([registro])

        # Guardar en CSV (crear o agregar)
        if ruta_csv.exists():
             df_registro.to_csv(ruta_csv, mode='a', header=False, index=False, encoding='utf-8')
        else:
             df_registro.to_csv(ruta_csv, mode='w', header=True, index=False, encoding='utf-8')
        
        st.info("🗂️ Tus datos fueron agregados correctamente en 'registros_prueba_renal.csv'.")

        # Crear la conexión a la Base de Datos en Supabase
        engine = create_engine('postgresql://postgres.uzvqvjxnzazhokzhsiad:villasol1460@aws-1-us-west-1.pooler.supabase.com:6543/postgres')
        
        # Guarda el registro en Supabase
        try:
            df_registro.to_sql('registros', con=engine, if_exists='append', index=False)
            st.success('✅ Datos enviados correctamente a Supabase.')
        except Exception as e:
            st.error(f'❌ Error al enviar datos a Supabase: {e}')
        

        # Mostrar gráfico de barras con los datos del usuario
        st.subheader(f'📈 Visualización de los datos del Paciente: {nombre}')

        # Datos del usuario para el gráfico
        valores_usuario = [creatinine_level, gfr, bun]
        
        # Rangos saludables aproximados
        rangos_normales = {'Creatinina (mg/dL)': (0.6, 1.3),
                           'GFR (mL/min/1.73m^2)': (90, 120),
                           'BUN (mg/dL)': (7, 20)}


        nombres = list(rangos_normales.keys())
        rangos_min = [rango[0] for rango in rangos_normales.values()]
        rangos_max = [rango[1] for rango in rangos_normales.values()]

        # Crear el gráfico de barras
        fig, ax = plt.subplots()
        ax.bar(nombres, valores_usuario, color='skyblue', label='Paciente')
        ax.plot(nombres, rangos_min, linestyle='--', marker='o', color='green', label='Min. saludable')
        ax.plot(nombres, rangos_max, linestyle='--', marker='o', color='red', label='Max. saludable')

        ax.set_ylabel('Valores')
        ax.set_title('Comparación con valores saludables')
        ax.legend()
        
        st.pyplot(fig)


with st.expander("🧠 Acerca del modelo de predicción"):
    st.write("""
    Este modelo fue entrenado con datos clínicos de pacientes, utilizando técnicas de aprendizaje automático
    (como Random Forest) para predecir el riesgo de daño renal a partir de biomarcadores
    como creatinina, GFR, BUN, y otros factores como diabetes o hipertensión.
    """)

