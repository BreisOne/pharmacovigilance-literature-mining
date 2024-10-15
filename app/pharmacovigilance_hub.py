import streamlit as st
import pandas as pd
import literature_mining as lt 
import base64

# Obtener la API key de Faers
api_key = st.secrets["FAERS_API_KEY"]

# Configuración de la página
st.title('Análisis de Enfermedades y Fármacos')

# Función para cargar los DataFrames de ejemplo desde la carpeta example_data
def load_example_dataframe(filename):
    return pd.read_csv(f'./app/example_data/{filename}')

# Función para generar enlace de descarga para un DataFrame en CSV
def get_table_download_link(df, filename):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Descargar {filename}</a>'
    return href

def analysis_layout(df_diseases, df_drugs, df_adverse_effects = None):
           
    with left_column:
        st.write('### Pubmed:')
        with st.spinner('Procesando datos en PubMed...'):
            
            # Obtener resultados mediante la API (simulado en este ejemplo)
            pubmed_results = lt.iterative_pubmed_search(df_diseases, df_drugs)
            
            # Verificar si pubmed_results está vacío o es nulo
            if pubmed_results is None or pubmed_results.empty:
                st.info("Se ha alcanzado el límite de llamadas a la API de PubMed. Por favor, intente de nuevo más tarde.")
            else:
                # Graficar resultados y actualizar en la zona central
                with st.spinner('Generando gráficos...'):
                
                    #Preprocesado del dataframe 
                    results_df_wide_pubmed, top_events_pubmed = lt.data_preprocessing(pubmed_results, rows = df_diseases.columns[0], columns = df_drugs.columns[0], cellValues = "Resultados", num_top_events = 12)
                    
                    #Generar figura
                    fig_pubmed = lt.bar_plot_results(results_df_wide_pubmed, top_events_pubmed, num_columns = 25, xlab = df_diseases.columns[0], 
                    plot_title ='Estudios de co-ocurrencia por enfermedad y farmaco. Source:PubMed', legend_title = df_drugs.columns[0])
                    
                    st.pyplot(fig_pubmed)
                    st.write(pubmed_results)
        
    with right_column:
        st.write('### Faers:')
        # Busqueda en la API de faers de los efectos adversos
        with st.spinner('Haciendo consulta en FAERS...'):
            #Obtener resultados de la API de Faers
            results_faers = lt.obtain_fda_results_from_list(api_key, df_drugs)
                
        with st.spinner('Generando gráficos...'):
                
            # Verificar si la lista adverse_effects no es nula
            if df_adverse_effects is not None:
                retain_terms = list(df_adverse_effects[df_adverse_effects.columns[0]])
                results_faers = results_faers[results_faers['term'].str.lower().isin([adverse_effect.lower() for adverse_effect in retain_terms])]
                
            #Preprocesado del daframe
            results_df_wide_faers, top_events_faers = lt.data_preprocessing(results_faers)
                
            #Generar figura
            fig_faers = lt.bar_plot_results(results_df_wide_faers, top_events_faers, num_columns = 25, xlab = results_faers.columns[0],
            plot_title ='Farmacos y efecto adverso. Source:Faers', legend_title = results_faers.columns[1])
                
            st.pyplot(fig_faers)
            st.dataframe(results_faers.rename(columns=lambda x: x.capitalize()), use_container_width=True)

# Cargar los DataFrames de ejemplo
df_example_diseases = load_example_dataframe('tipo_tumores.csv')
df_example_drugs = load_example_dataframe('farmacos.csv')
df_example_adverse_effects = load_example_dataframe('efectos_adversos.csv')


# Barra lateral para cargar archivos CSV
st.sidebar.header('Cargar archivos CSV')
# Cuadro de texto para input del usuario
diseases_file = st.sidebar.file_uploader('Selecciona el CSV de Enfermedades', type=['csv'])
st.sidebar.markdown(get_table_download_link(df_example_diseases, 'Plantilla_Enfermedades.csv'), unsafe_allow_html=True)

drugs_file = st.sidebar.file_uploader('Selecciona el CSV de Fármacos', type=['csv'])
st.sidebar.markdown(get_table_download_link(df_example_drugs, 'Plantilla_Farmacos.csv' ), unsafe_allow_html=True)

adverse_effects = st.sidebar.file_uploader('Selecciona el CSV de Efectos adversos: No obligatorio', type=['csv'])
st.sidebar.markdown(get_table_download_link(df_example_adverse_effects, 'Plantilla_Efectos_adversos.csv'), unsafe_allow_html=True)

left_column, right_column = st.columns(2)

# Botón para realizar el análisis
if st.sidebar.button('Analizar'):
    if diseases_file is not None and drugs_file is not None:
        # Cargar datos desde los archivos CSV
        df_diseases = pd.read_csv(diseases_file)
        df_drugs = pd.read_csv(drugs_file)
        if adverse_effects is not None:
            df_adverse_effects = pd.read_csv(adverse_effects)
        else:
            df_adverse_effects = None
        # Hacer el analisis y mostrar los resultados
        analysis_layout(df_diseases, df_drugs, df_adverse_effects)
    else:
        st.warning('Por favor, carga ambos archivos CSV antes de analizar.')
        
#Realizar un análisis de ejemplo para mostrar como se debería ver el resultado
if st.sidebar.button('Analisis de Ejemplo'):
    analysis_layout(df_example_diseases, df_example_drugs, df_example_adverse_effects)
