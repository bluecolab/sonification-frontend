import matplotlib.pyplot as plt  # Importing matplotlib for plotting
import pandas as pd  # Importing pandas for data manipulation
from flask import Flask, render_template  # Importing Flask for web app and render_template for rendering HTML templates
from plotnine import *  # Importing plotnine for ggplot functionality
from plotnine import theme  # Importing theme module from plotnine for customizing plots

# Switching the backend for matplotlib to 'agg' to enable plotting in a non-interactive backend
plt.switch_backend('agg')

import plotly.express as px  # Importing plotly.express for creating interactive plots

# Initializing the Flask application
app = Flask(__name__, static_url_path='/static')

@app.route('/')
def index():
    # Reading the CSV file and loading the data into a pandas dataframe
    df = pd.read_csv('./data/data.csv')

    # Melting the dataframe to a long format for easier plotting using pandas
    df_melted = df.melt(
        id_vars=['timestamp'],
        value_vars=['Conductivity', 'Dissolved Oxygen', 'Salinity', 'Temperature(F)', 'Turbidity', 'pH'],
        var_name='Variable',
        value_name='Value'
    )

    # Keeping a copy of the original values before scaling
    df_melted['Original_Value'] = df_melted['Value']

    # Scaling the values for each variable to make them comparable in the stacked area plot using pandas
    df_melted.loc[df_melted['Variable'] == 'Salinity', 'Value'] *= 30
    df_melted.loc[df_melted['Variable'] == 'Dissolved Oxygen', 'Value'] *= 1
    df_melted.loc[df_melted['Variable'] == 'Temperature(F)', 'Value'] *= 1
    df_melted.loc[df_melted['Variable'] == 'Conductivity', 'Value'] *= 0.3
    df_melted.loc[df_melted['Variable'] == 'pH', 'Value'] *= 10
    df_melted.loc[df_melted['Variable'] == 'Turbidity', 'Value'] *= 1

    # Defining the desired order of the variables for the legend and plotting
    desired_order = ['Salinity', 'pH', 'Temperature(F)', 'Turbidity', 'Dissolved Oxygen', 'Conductivity']

    # Defining custom colors for each variable
    color_dict = {
        'Salinity': '#FF9F1C',
        'Dissolved Oxygen': '#8FE1F4',
        'Temperature(F)': '#169873',
        'Conductivity': '#2081C3',
        'pH': '#EFE9AE',
        'Turbidity': '#B57BA6'
    }

    # Creating a stacked area plot using Plotly Express
    fig = px.area(
        df_melted,
        x='timestamp',
        y='Value',
        color='Variable',
        title='Stacked Sonification Graph',
        color_discrete_map=color_dict,  # Applying custom color palette
        hover_data={'Original_Value': False},  # Disabling hover data for original values
        category_orders={'Variable': desired_order}  # Setting the order of the categories
    )

    # Updating layout to customize the appearance of the plot using Plotly Express
    fig.update_layout(
        xaxis=dict(title='Timestamp', showgrid=False, nticks=10),
        yaxis=dict(title='Sensors', showgrid=False, showticklabels=False),
        barmode='stack',  # Stacking the areas
        paper_bgcolor="#030227",  # Setting background color
        legend_font_color="white",  # Setting legend font color
        font_color="white",  # Setting main font color
        title_font_family="Balto",  # Setting title font family
        legend_tracegroupgap=0,  # Setting gap between legend items
        margin_b=5,  # Setting bottom margin
        margin_l=25,  # Setting left margin
        margin_r=25,  # Setting right margin
        margin_t=30  # Setting top margin
    )

    #fig.legend(bbox_to_anchor=(1.1, 1.05))
    #Extract data parameters
    #data_params = {
    #    'y': [item.legendgroup for item in fig.data],
    #                    # Add other data parameters as needed
    #}

    # Printing the figure to the console for debugging purposes
    print(fig)

    # Converting the plot to HTML format to embed in the web page using Plotly
    plot_html = fig.to_html(include_plotlyjs='cdn')
    
    # Rendering the graph.html template and passing the plot HTML to it using Flask
    return render_template('graph.html', plot=plot_html)

# Running the Flask application
if __name__ == '__main__':
    app.run(debug=True)
