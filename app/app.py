import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import literature_mining as lt 

# Configuración de la página
st.title('Análisis de Enfermedades y Fármacos')

# Imagen de encabezado
#header_image = './header.png'  # Reemplaza esto con la URL de tu imagen
#st.image(header_image, use_column_width=True)
st.set_option('deprecation.showPyplotGlobalUse', False)

# Barra lateral para cargar archivos CSV
st.sidebar.header('Cargar archivos CSV')
# Cuadro de texto para input del usuario
diseases_file = st.sidebar.file_uploader('Selecciona el CSV de Enfermedades', type=['csv'])
drugs_file = st.sidebar.file_uploader('Selecciona el CSV de Fármacos', type=['csv'])
adverse_effects = st.sidebar.file_uploader('Selecciona el CSV de Efectos adversos: No obligatorio', type=['csv'])

left_column, right_column = st.columns(2)

# Botón para realizar el análisis
if st.sidebar.button('Analizar'):
    if diseases_file is not None and drugs_file is not None:
        # Cargar datos desde los archivos CSV
        df_diseases = pd.read_csv(diseases_file)
        df_drugs = pd.read_csv(drugs_file)
        if adverse_effects is not None:
            df_adverse_effects = pd.read_csv(adverse_effects)
        # Mostrar los datos cargados
        # Mostrar loader mientras se procesan los datos
        with left_column:
            st.write('### Pubmed:')
            with st.spinner('Procesando datos en PubMed...'):
            
                # Obtener resultados mediante la API (simulado en este ejemplo)
                pubmed_results = lt.iterative_pubmed_search(df_diseases, df_drugs)

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
                results_faers = lt.obtain_fda_results_from_list('pqnh6L01FAfMHzGvbu6PoEXoHoqQLIXFgxWCAaoH', df_drugs)
                
            with st.spinner('Generando gráficos...'):
                
                # Verificar si la lista adverse_effects no es nula
                if adverse_effects is not None:
                    retain_terms = list(df_adverse_effects[df_adverse_effects.columns[0]])
                    results_faers = results_faers[results_faers['term'].str.lower().isin([adverse_effect.lower() for adverse_effect in retain_terms])]
                
                #Preprocesado del daframe
                results_df_wide_faers, top_events_faers = lt.data_preprocessing(results_faers)
                
                #Generar figura
                fig_faers = lt.bar_plot_results(results_df_wide_faers, top_events_faers, num_columns = 25, xlab = results_faers.columns[0],
                        plot_title ='Farmacos y efecto adverso. Source:Faers', legend_title = results_faers.columns[1])
                
                st.pyplot(fig_faers)
                st.write(results_faers)

        
        
    else:
        st.warning('Por favor, carga ambos archivos CSV antes de analizar.')
