import matplotlib.pyplot as plt  # Importing matplotlib for plotting
import pandas as pd  # Importing pandas for data manipulation
from flask import Flask, render_template, request # Importing Flask for web app and render_template for rendering HTML templates
from plotnine import *  # Importing plotnine for ggplot functionality
import os
import datetime as dt
import re
# Switching the backend for matplotlib to 'agg' to enable plotting in a non-interactive backend
plt.switch_backend('agg')

import plotly.express as px  # Importing plotly.express for creating interactive plots

# Initializing the Flask application
app = Flask(__name__, static_url_path='/static')

# Base folder where the program will find the csv files
base_folder_path = './data'

# formats the dates to only have Year, month, and date (hours, minutes and seconds are excluded)
def getTimeStampString(tsec: float) -> str:
    time_obj = dt.datetime.fromtimestamp(tsec)
    time_str = dt.datetime.strftime(time_obj, '%Y-%m-%d')
    return time_str


@app.route('/', methods=["GET","POST"])
def index():
    if request.method == 'POST' or request.method == "GET":
        selected_file = request.form.get('name')
        if str(selected_file) == "None":
            selected_file = "Default"
        new_file = './data/' + selected_file + '.csv'
        df = pd.read_csv(new_file)

    # Melting the dataframe to a long format for easier plotting using pandas
    df_melted = df.melt(
        id_vars=['timestamp'],
        value_vars=['sensors__Cond', 'sensors__DOpct', 'sensors__Sal', 'sensors__Temp', 'sensors__Turb', 'sensors__pH'],
        var_name='Variable',
        value_name='Value'
    )

    # Keeping a copy of the original values before scaling
    df_melted['Original_Value'] = df_melted['Value']

    # Scaling the values for each variable to make them comparable in the stacked area plot using pandas
    df_melted.loc[df_melted['Variable'] == 'sensors__Sal', 'Value'] *= 30
    df_melted.loc[df_melted['Variable'] == 'sensors__DOpct', 'Value'] *= 1
    df_melted.loc[df_melted['Variable'] == 'sensors__Temp', 'Value'] *= 1
    df_melted.loc[df_melted['Variable'] == 'sensors__Cond', 'Value'] *= 0.3
    df_melted.loc[df_melted['Variable'] == 'sensors__pH', 'Value'] *= 10
    df_melted.loc[df_melted['Variable'] == 'sensors__Turb', 'Value'] *= 1

    # Defining the desired order of the variables for the legend and plotting
    desired_order = ['sensors__Sal', 'sensors__pH', 'sensors__Temp', 'sensors__Turb', 'sensors__DOpct', 'sensors__Cond']

    # Defining custom colors for each variable
    color_dict = {
        'sensors__Sal': '#FF9F1C',
        'sensors__DOpct': '#8FE1F4',
        'sensors__Temp': '#169873',
        'sensors__Cond': '#2081C3',
        'sensors__pH': '#EFE9AE',
        'sensors__Turb': '#B57BA6'
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
        title={'y':.96, 'x':.46, 'xanchor': 'center'},
        plot_bgcolor = "#030227",
        margin_b=10,  # Setting bottom margin
        margin_l=25,  # Setting left margin
        margin_r=25,  # Setting right margin
        margin_t=40  # Setting top margin
    )

    #Changes the names of the imported data set to be more readable 
    newnames = {'sensors__Cond' : 'Conductivity', 'sensors__DOpct' : 'Dissolved Oxygen', 'sensors__Sal' : 'Salinity', 'sensors__Temp' : 'Temperature(F)', 'sensors__Turb' : 'Turbidity', 'sensors__pH' : 'pH'}
    fig.for_each_trace(lambda t: t.update(name = newnames[t.name], legendgroup = newnames[t.name], hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])))

    #fig.legend(bbox_to_anchor=(1.1, 1.05))
    #Extract data parameters
    #data_params = {
    #    'y': [item.legendgroup for item in fig.data],
    #                    # Add other data parameters as needed
    #}

    # Printing the figure to the console for debugging purposes
    print(fig)

    file_names = [file_object(x) for x in os.scandir(base_folder_path)] 

    # Converting the plot to HTML format to embed in the web page using Plotly
    plot_html = fig.to_html(include_plotlyjs='cdn')   
    
    # Rendering the graph.html template and passing the plot HTML to it using Flask
    return render_template('graph.html', plot=plot_html, files=file_names)

# Searches the data folder for file names and imports them
# Return a object of the file name only (no extension ".csv")
pattern = r"\\(.+)"
def file_object(inputed_file):
    # import date of files
    # file = inputed_file.stat()
    # file_date = getTimeStampString(file.st_mtime)
    name_only = os.path.splitext(inputed_file)[0]
    match = re.search(pattern, name_only)
    # import date of file in the object
    # return {'name': match.group(1), 'date': file_date}
    return {'name': match.group(1)}


# Running the Flask application
if __name__ == '__main__':
    app.run(debug=True)
