import streamlit as st
import pandas as pd
import literature_mining as lt 
import base64

# Getting the API key of Faers
api_key = st.secrets["FAERS_API_KEY"]

# Configuring the page
st.set_page_config(
                page_title="Pharmacovigilance and literature mining hub",
                page_icon="💊",
                layout="wide")

st.title('Pharmacovigilance and literature mining hub')

# Function to load the example DataFrames from the example_data folder
def load_example_dataframe(filename):
    return pd.read_csv(f'./app/example_data/{filename}')

# Function to generate a download link for a DataFrame in CSV format
def get_table_download_link(df, filename):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download {filename}</a>'
    return href

def analysis_layout(df_diseases, df_drugs, df_adverse_effects = None):
           
    with left_column:
        st.write('### Pubmed:')
        with st.spinner('Processing data in PubMed...'):
            
            # Obtener resultados mediante la API (simulado en este ejemplo)
            pubmed_results = lt.iterative_pubmed_search(df_diseases, df_drugs)
            
            # Verificar si pubmed_results está vacío o es nulo
            if pubmed_results is None or pubmed_results.empty:
                st.info("You have reached the limit of calls to the PubMed API. Please try again later.")
            else:
                # Plotting results and updating in the central area
                with st.spinner('Generating graphics...'):
                
                    #Preprocessing the dataframe 
                    results_df_wide_pubmed, top_events_pubmed = lt.data_preprocessing(pubmed_results, rows = df_diseases.columns[0], columns = df_drugs.columns[0], cellValues = "Results", num_top_events = 12)
                    
                    #Generating figure
                    fig_pubmed = lt.bar_plot_results(results_df_wide_pubmed, top_events_pubmed, num_columns = 25, xlab = df_diseases.columns[0].capitalize(), 
                    plot_title ='Studies of co-occurrence by disease and drug. Source:PubMed', legend_title = df_drugs.columns[0].capitalize())
                    
                    st.pyplot(fig_pubmed)
                    st.dataframe(pubmed_results, use_container_width=True)

    with right_column:
        st.write('### Faers:')
        # Search in the Faers API for the adverse effects
        with st.spinner('Making query in FAERS...'):
            #Getting results from the Faers API
            results_faers = lt.obtain_fda_results_from_list(api_key, df_drugs)
                
        with st.spinner('Generating graphics...'):
                
            # Verifying if the adverse_effects list is not null
            if df_adverse_effects is not None:
                retain_terms = list(df_adverse_effects[df_adverse_effects.columns[0]])
                results_faers = results_faers[results_faers['term'].str.lower().isin([adverse_effect.lower() for adverse_effect in retain_terms])]
                
            #Preprocessing the dataframe
            results_df_wide_faers, top_events_faers = lt.data_preprocessing(results_faers)
            
            #Generating figure
            fig_faers = lt.bar_plot_results(results_df_wide_faers, top_events_faers, num_columns = 25, xlab = results_faers.columns[0].capitalize(),
            plot_title ='Drugs and adverse effect. Source:Faers', legend_title = results_faers.columns[1].capitalize())
                
            st.pyplot(fig_faers)
            st.dataframe(results_faers.rename(columns=lambda x: x.capitalize()), use_container_width=True)

# Loading the example DataFrames
df_example_diseases = load_example_dataframe('tipo_tumores.csv')
df_example_drugs = load_example_dataframe('farmacos.csv')
df_example_adverse_effects = load_example_dataframe('efectos_adversos.csv')


# Sidebar to upload CSV files
st.sidebar.header('Upload CSV files')
# Textbox for user input
diseases_file = st.sidebar.file_uploader('Select the CSV of Diseases', type=['csv'])
st.sidebar.markdown(get_table_download_link(df_example_diseases, 'diseases_template.csv'), unsafe_allow_html=True)

drugs_file = st.sidebar.file_uploader('Select the CSV of Drugs', type=['csv'])
st.sidebar.markdown(get_table_download_link(df_example_drugs, 'drugs_template.csv'), unsafe_allow_html=True)

adverse_effects = st.sidebar.file_uploader('Select the CSV of Adverse Effects: Not obligatory', type=['csv'])
st.sidebar.markdown(get_table_download_link(df_example_adverse_effects, 'adverse_effects_template.csv'), unsafe_allow_html=True)

left_column, right_column = st.columns(2)

# Button to perform the analysis
if st.sidebar.button('Analyze'):
    if diseases_file is not None and drugs_file is not None:
        # Loading data from the CSV files
        df_diseases = pd.read_csv(diseases_file)
        df_drugs = pd.read_csv(drugs_file)
        if adverse_effects is not None:
            df_adverse_effects = pd.read_csv(adverse_effects)
        else:
            df_adverse_effects = None
        # Performing the analysis and showing the results
        analysis_layout(df_diseases, df_drugs, df_adverse_effects)
    else:
        st.warning('Please upload both CSV files before analyzing.')
        
# Performing an example analysis to show how the results should look
if st.sidebar.button('Example Analysis'):
    analysis_layout(df_example_diseases, df_example_drugs, df_example_adverse_effects)
