from pymed import PubMed
import requests
import pandas as pd
import time
import matplotlib.pyplot as plt
import seaborn as sns


# Function to get the number of results
def get_results_count(query):
    pubmed = PubMed(tool="MyTool", email="testemails@gmail.com")
    try:
        return pubmed.getTotalResultsCount(query)
    except Exception as e:
        print(f"Error getting results for the query '{query}': {e}")
        return None
# Function to process a single combination of disease and drug
def process_combination(disease, drug):
        query = f"{disease} AND {drug}"
        results_count = get_results_count(query)
        return {'disease': disease, 'drug': drug, 'results': results_count}


def obtain_fda_results(api_key, drug_term):
    base_url = "https://api.fda.gov/drug/event.json"
    
    # Search parameters
    params = {
        'api_key': api_key,
        'search': f'"patient.drug.medicinalproduct.exact:""{drug_term}"',
        'count': "patient.reaction.reactionmeddrapt.exact"
        }

    headers = {
        'Content-Type': 'application/json',
    }

    try:
        # Performing the API call
        response = requests.get(base_url,  params=params, headers=headers)
        response.raise_for_status()  # Verifying if there are errors in the HTTP response

        # Converting the response to JSON
        data = response.json()

        # Verifying if 'results' is present
        if 'results' in data:
            # Returning the resulting JSON
            return data
        else:
            print(f"No results found for {drug_term}")
            return None
    
    except requests.exceptions.RequestException as e:
        print(f"Error in the API call for {drug_term}: {e}")
        return None
    
def obtain_fda_results_from_list(api_key, drugs):
    
    df_results = pd.DataFrame(columns=['drug', 'term', 'count'])

    for drug in drugs[drugs.columns[0]]:
        data = obtain_fda_results(api_key,drug)
        
        # Verifying if 'results' is present in data
        if data is not None and 'results' in data:
            # Creating a DataFrame for the current drug results
            df_drug = pd.DataFrame(data['results'])
            df_drug['drug'] = drug
            
            # Concatenating to the main DataFrame
            df_results = pd.concat([df_results, df_drug], ignore_index=True)
        # Adding a 1 second wait
        time.sleep(1)
        
        #Capitalizing the drug and term columns
        df_results["drug"] = df_results["drug"].str.capitalize()
        df_results["term"] = df_results["term"].str.capitalize()
        
    return df_results

#Function to preprocess data

def data_preprocessing(results_df, rows = "drug", columns = "term", cellValues = "count", num_top_events = 12):
    #Preprocessing the dataframe

    # We use the pivot_table function (handles duplicates) to convert the long DataFrame to a wide one
    results_df_wide = results_df.pivot_table(index=rows, columns=columns, values=cellValues)

    #We remove the drug label as a column name
    results_df_wide.columns.name = None

    #We reset the indices so that the disease and drug names are at the same level
    results_df_wide.reset_index(inplace=True)

    #We extract the 25 events with the highest number of results in the bibliography. Independently of the disease
    top_events = results_df_wide.drop(columns=[rows]).sum().sort_values(ascending=False).head(num_top_events)

    #We filter the dataframe to keep only the disease and drugs with the highest results
    results_df_wide = results_df_wide[[rows] + list(top_events.index)]

    #We define the disease as the indices of the dataframe
    results_df_wide.set_index(rows, inplace=True)

    # We sum the total of results of the 15 drugs for each disease and create a new column called 'TotalResults'
    results_df_wide['TotalResults'] = results_df_wide[list(top_events.index)].sum(axis=1)

    # We sort the DataFrame by the new 'TotalResults' column in descending order
    results_df_wide = results_df_wide.sort_values(by='TotalResults', ascending=False).reset_index()
    results_df_wide = results_df_wide[[rows] + list(top_events.index)]
    results_df_wide.set_index(rows, inplace=True)

    results_df = results_df_wide.infer_objects(copy=False)
    
    return results_df, top_events

def bar_plot_results(results_df_wide, top_events, num_columns = 25, xlab = 'Drugs', 
                     plot_title ='Drugs and adverse effect. Source:Faers', legend_title = 'Adverse effect'):
    # Visualizing the results of each drug in relation to the disease
    fig, ax = plt.subplots(figsize=(10, 6))

    # Configuring the unique color palette for each drug with Seaborn
    colors = sns.color_palette("Set3", n_colors=len(top_events))

    # Creating a stacked bar plot
    results_df_wide.head(num_columns).plot(kind='bar', stacked=True, ax=ax, color = colors, width=0.8)

    # Adding labels and title
    ax.set_xlabel(xlab, fontsize=12)
    ax.set_ylabel('Number of results', fontsize=12)
    ax.set_title(plot_title, fontsize=14)
    ax.legend(title= legend_title, bbox_to_anchor=(1.05, 1), loc='upper left')  # Placing the legend to the right
    plt.xticks(rotation=45, ha='right')  # Rotating the x-axis labels
    plt.tight_layout()  # Adjusting the plot layout
    
    return fig
    
def iterative_pubmed_search(first_list, second_list):
    # Initializing a list to store the results
    results_list = []
    
    try:
        # Nested loop to combine disease and drug
        for first_list_element in first_list[first_list.columns[0]]:
            for second_list_element in second_list[second_list.columns[0]]:
                # Creating the query combining the disease and the drug
                query = f"{first_list_element} AND {second_list_element}"
                # Getting the number of results
                results_count = get_results_count(query)
                # Adding the results to the list
                results_list.append({f'{first_list.columns[0]}': first_list_element, f'{second_list.columns[0]}': second_list_element, 'Results': results_count})

        # Creating a DataFrame from the results list
        results_df = pd.DataFrame(results_list)
        return results_df
    except requests.exceptions.RequestException as e:
        print(f"Error in the iterative PUBMED search: {e}")
    