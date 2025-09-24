def mostrar_panel_control():

    import streamlit as st # Librería principal para crear la interfaz web
    from supabase import create_client, Client # Cliente para conectar con Supabase
    import pandas as pd
    from utils_s3 import obtener_csv_desde_s3

    # Conexión global a Supabase
    url = 'https://uzvqvjxnzazhokzhsiad.supabase.co' 
    key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV6dnF2anhuemF6aG9remhzaWFkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTYyMzM5NzAsImV4cCI6MjA3MTgwOTk3MH0.b5Obj6gsjsTYZyHbnAo5VDiRsQfwDJavBdAX8Jg0S-Q'
    supabase: Client = create_client(url, key) # Crear cliente Supabase para hacer consultas


    def show_login():
        st.title('🔐 Iniciar Sesión') # Título principal del Login

        email = st.text_input('Correo Electrónico') # Input para correo
        password = st.text_input('Contraseña', type='password') # Input para contraseña oculta los caracteres

        if st.button('Iniciar Sesión'): # Botón de login
            try:
                # 1. Autenticación del usuario contra Supabase Auth
                user = supabase.auth.sign_in_with_password({'email':email, 'password':password})
                user_id = user.user.id # Obtener ID del usuario autenticado

                # 2. Buscar el perfil del usuario en la tabla personalizada "usuarios"
                result = supabase.table('usuarios').select('nombre', 'rol').eq('id', user_id).execute()

                if result.data and len(result.data) > 0:
                    # 3. Guardar datos en sesión si existe en tabla "usuarios"
                    datos = result.data[0]
                    st.session_state['user'] = user
                    st.session_state['email'] = email
                    st.session_state['nombre'] = datos['nombre']
                    st.session_state['rol'] = datos['rol']
                    st.success(f"Inicio de sesión exitoso ✅ Bienvenido {datos['nombre']}")
                    st.experimental_rerun() # Refrescar la app para que detecte sesión activa
                else:
                    # Usuario autenticado, pero no tiene perfil en tabla "usuarios"
                    st.error("⚠️ Usuario autenticado, pero no tiene perfil en la tabla `usuarios`. Contacta al administrador.")
            except Exception as es:
                # Error en login (correo o contraseña incorrectos)
                st.error(f'Correo o contraseña incorrectos ❌ {es}')

    def obtener_dataframe(nombre_tabla: str):
        # Función que consulta todos los registros de una Tabla de Supabase y los devuelve como DataFrame
        try:
            response = supabase.table(nombre_tabla).select('*').execute()
            data =  response.data

            if not data:
                st.warning(f'No hay datos en la tabla {nombre_tabla}')
                return None
            return pd.DataFrame(data) # Convertir los datos a DataFrame
        
        except Exception as e:
            st.error(f'Error al obtener los datos: {e}')
            return None

    def mostrar_tabla():
        df = obtener_dataframe('registros')
        if df is not None:
            st.subheader('Registros') # Título para la sección
            st.dataframe(df)        # Mostrar la tabla en la app

    def eliminar_registros():
        st.subheader('🗑️ Eliminar todos los registros')

        # Advertencia previa
        st.warning('⚠️ Esta acción eliminará todos los registros de la base de datos')
        st.info('Por favor, asegúrate de haber descargado el archivo CSV antes de continuar.')

        # Checkbox para confirmar
        confirmar = st.checkbox('Sí, entiendo y quiero borrar todos los registros.')

        if confirmar:
            if st.button('Eliminar Registros ahora'):
                registros = obtener_dataframe('registros')
                if registros is None or registros.empty:
                    return
                try:
                    # Eliminar todos los registros donde el id sea mayor o igual a 0 (todos)
                    supabase.table('registros').delete().gte('nombre', 0).execute()
                    st.success('✅ Todos los registros han sido eliminados.')
                except Exception as e:
                    st.error(f'Ocurrió un error {e}')

    def descargar_csv():
        st.subheader('⬇️ Descargar datos como CSV')
        df = obtener_dataframe('registros')

        if df is not None:
            st.dataframe(df) # Mostrar DataFrame para vista previa
            csv = df.to_csv(index=False).encode('utf-8') # Convertir DataFrame a CSV
            st.download_button(label='📥 Descargar CSV', data=csv, file_name='registros.csv', \
            mime='text/csv')
    
    def descargar_desde_s3():
        if st.button('📥 Descargar registros históricos desde S3'):
            df_s3 = obtener_csv_desde_s3()
            if df_s3.empty:
                st.warning('⚠️ No hay registros aún en S3.')
            else:
                st.dataframe(df_s3)
                csv = df_s3.to_csv(index=False).encode('utf-8')
                st.download_button('⬇️ Descargar CSV', data=csv, file_name='registros_renal_histórico.csv', mime='text/csv')


    def main():
        if 'user' in st.session_state: # Si hay sesión iniciada

            nombre = st.session_state['nombre']
            rol = st.session_state['rol']

            # Menú lateral con opciones según el rol
            st.sidebar.title('Panel de Control')

            # Opiones del menú según el rol
            if rol.lower() == 'admin' or rol.lower() == 'ceo':
                opciones = ['Inicio', 'Mostrar Registros', 'Eliminar Registros', 'Descargar Registros', 'Descargar Registros Históricos']
            else:
                opciones = ['Inicio', 'Mostrar Registros']

            # Selector de opción    
            opcion = st.sidebar.radio('Selecciona una opción: ', opciones)


            # Botón para cerrar sesión
            if st.sidebar.button('Cerrar Sesión'):
                st.session_state.clear()
                st.experimental_rerun()

            # Mensaje de bienvenida
            st.success(f'✅ ¡Bienvenido **{rol.upper()}** **{nombre}** !')


            # Mostrar contenido según la opción seleccionada
            if opcion == 'Inicio':
                st.write('Selecciona una opción en el menú lateral.')
            elif opcion == 'Mostrar Registros':
                mostrar_tabla()
            elif opcion == 'Eliminar Registros':
                eliminar_registros()
            elif opcion == 'Descargar Registros':
                descargar_csv()
            elif opcion == 'Descargar Registros Históricos':
                descargar_desde_s3()
        else:
            show_login() # Si no hay sesión, mostrar el login

    main()