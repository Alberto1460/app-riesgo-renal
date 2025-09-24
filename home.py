import streamlit as st
from app import mostrar_app_riesgo
from login import mostrar_panel_control

# Configura los ajustes básicos de la página
st.set_page_config(page_title='App Renal Multipágina', layout='centered')

# Menú en la barra lateral que verán los usuarios
st.sidebar.title('Menú de Navegación')
opcion = st.sidebar.radio('Selecciona una sección:', ['🩺 Evaluación Renal', '🔐 Panel de Control'])

# Mostrar la sección correspondiente
if opcion == '🩺 Evaluación Renal':
    mostrar_app_riesgo()
    
elif opcion == '🔐 Panel de Control':
    mostrar_panel_control()