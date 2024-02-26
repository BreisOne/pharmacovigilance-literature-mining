import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
from io import BytesIO

# Función para realizar peticiones a la API y obtener resultados
def obtener_resultados(enfermedades, farmacos):
    # Simulación de un proceso demorado
    import time
    time.sleep(3)

    # Aquí debes colocar la lógica de tu API para obtener los resultados
    # Puedes adaptar esto según la estructura de tu API y cómo procesar los datos
    # La función debe devolver los resultados en un formato adecuado para el gráfico
    # En este ejemplo, se genera un conjunto de datos aleatorio
    resultados = {'Enfermedad': [], 'Farmaco': [], 'Score': []}
    for enfermedad in enfermedades:
        for farmaco in farmacos:
            # Simulación de puntuaciones aleatorias
            score = round((len(enfermedad) + len(farmaco)) / 2, 2)
            resultados['Enfermedad'].append(enfermedad)
            resultados['Farmaco'].append(farmaco)
            resultados['Score'].append(score)
    return resultados

# Función para graficar los resultados
def graficar_resultados(resultados):
    df_resultados = pd.DataFrame(resultados)
    fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(10, 8))

    for i, enfermedad in enumerate(df_resultados['Enfermedad'].unique()):
        subset = df_resultados[df_resultados['Enfermedad'] == enfermedad]
        row, col = divmod(i, 2)
        subset.plot(kind='bar', x='Farmaco', y='Score', ax=axs[row, col], legend=False)
        axs[row, col].set_ylabel('Score')
        axs[row, col].set_title(f'Resultados para {enfermedad}')

    plt.tight_layout()
    return fig

# Configuración de la página
st.title('Análisis de Enfermedades y Fármacos')

# Imagen de encabezado
header_image = './header.png'  # Reemplaza esto con la URL de tu imagen
#st.image(header_image, use_column_width=True)

# Barra lateral para cargar archivos CSV
st.sidebar.header('Cargar archivos CSV')
archivo_enfermedades = st.sidebar.file_uploader('Selecciona el CSV de Enfermedades', type=['csv'])
archivo_farmacos = st.sidebar.file_uploader('Selecciona el CSV de Fármacos', type=['csv'])

# Botón para realizar el análisis
if st.sidebar.button('Analizar'):
    if archivo_enfermedades is not None and archivo_farmacos is not None:
        # Cargar datos desde los archivos CSV
        df_enfermedades = pd.read_csv(archivo_enfermedades)
        df_farmacos = pd.read_csv(archivo_farmacos)

        # Mostrar loader mientras se procesan los datos
        with st.spinner('Procesando datos...'):
            # Obtener resultados mediante la API (simulado en este ejemplo)
            resultados = obtener_resultados(df_enfermedades['Enfermedad'].tolist(), df_farmacos['Farmaco'].tolist())

        # Graficar resultados y actualizar en la zona central
        with st.spinner('Generando gráficos...'):
            fig = graficar_resultados(resultados)
            st.pyplot(fig)
        
        # Mostrar los datos cargados
        st.header('Datos cargados:')
        st.write('### Enfermedades:')
        st.write(df_enfermedades)
        st.write('### Fármacos:')
        st.write(df_farmacos)
    else:
        st.warning('Por favor, carga ambos archivos CSV antes de analizar.')
