import matplotlib.pyplot as plt  # Importing matplotlib for plotting
import pandas as pd  # Importing pandas for data manipulation
from flask import Flask, render_template, request, redirect  # Importing Flask for web app and render_template for rendering HTML templates
from plotnine import *  # Importing plotnine for ggplot functionality
from plotnine import theme  # Importing theme module from plotnine for customizing plots
import os
import datetime as dt
# Switching the backend for matplotlib to 'agg' to enable plotting in a non-interactive backend
plt.switch_backend('agg')

import plotly.express as px  # Importing plotly.express for creating interactive plots

# Initializing the Flask application
app = Flask(__name__, static_url_path='/static')

baseFolderPath = './data'

def getTimeStampString(tsec: float) -> str:
    time_obj = dt.datetime.fromtimestamp(tsec)
    time_str = dt.datetime.strftime(time_obj, '%Y-%m-%d')
    return time_str


@app.route('/', methods=["GET","POST"])
def index():
    if request.method == 'POST':
        selected_file = request.form.get('name')
        new_file = './data/' + str(selected_file)
        df = pd.read_csv(new_file)
    else:
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
        title_font_family="Roboto",  # Setting title font family
        legend_tracegroupgap=0,  # Setting gap between legend items
    title={
        'y':.96,
        'x':.46,
        'xanchor': 'center'},
        margin_b=10,  # Setting bottom margin
        margin_l=25,  # Setting left margin
        margin_r=25,  # Setting right margin
        margin_t=40  # Setting top margin
    )

    #fig.legend(bbox_to_anchor=(1.1, 1.05))
    #Extract data parameters
    #data_params = {
    #    'y': [item.legendgroup for item in fig.data],
    #                    # Add other data parameters as needed
    #}

    # Printing the figure to the console for debugging purposes
    print(fig)

    def file_object(inputed_file):
        file = inputed_file.stat()
        file_date = getTimeStampString(file.st_mtime)
        return {'name': inputed_file.name, 'date': file_date}
    file_names = [file_object(x) for x in os.scandir(baseFolderPath)] 

    # Converting the plot to HTML format to embed in the web page using Plotly
    plot_html = fig.to_html(include_plotlyjs='cdn')   
    
    # Rendering the graph.html template and passing the plot HTML to it using Flask
    return render_template('graph.html', plot=plot_html, files=file_names)
    

# Running the Flask application
if __name__ == '__main__':
    app.run(debug=True)
