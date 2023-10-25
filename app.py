from flask import Flask, render_template
import plotly
import plotly.graph_objects as go
import pandas as pd
from plotnine import *
import matplotlib.pyplot as plt
import pygame
from pydub import AudioSegment
from plotnine import options, ggplot, theme
import plotly.offline as pyo
from flask import jsonify

plt.switch_backend('agg')
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
import json
from plotnine import ggplot



app = Flask(__name__)

@app.route('/')
def index():
    # This will read the Excel file and load the data into a pandas dataframe
    df = pd.read_excel(
        r'/Users/louisamoquete/Library/Containers/com.microsoft.Excel/Data/Desktop/School/Coding Projects/BlueCoLab/Book1.xlsx')
    print(df)

    df_melted = df.melt(
        id_vars=['timestamp'],
        value_vars=['Conductivity', 'Dissolved Oxygen', 'Salinity', 'Temperature(F)', 'Turbidity', 'pH'],
        var_name='Variable',
        value_name='Value'
    )

    # Sal range: 0.20 - 0.47
    # pH range: 6.87 - 9.09
    # Temp range: 3.17 - 29.14 (Celsius)
    # TempF range: 37.71 - 84.45
    # Turb range: 0.71 - 286.50
    # DOpct range:3.67 - 178.42
    # Cond range:317.00 - 994.83

    df_melted['Original_Value'] = df_melted['Value']

    df_melted.loc[df_melted['Variable'] == 'Salinity', 'Value'] *= 30
    df_melted.loc[df_melted['Variable'] == 'Dissolved Oxygen', 'Value'] *= 1
    df_melted.loc[df_melted['Variable'] == 'Temperature(F)', 'Value'] *= 1
    df_melted.loc[df_melted['Variable'] == 'Conductivity', 'Value'] *= 0.3
    df_melted.loc[df_melted['Variable'] == 'pH', 'Value'] *= 10
    df_melted.loc[df_melted['Variable'] == 'Turbidity', 'Value'] *= 1

    desired_order = ['Salinity', 'pH', 'Temperature(F)', 'Turbidity', 'Dissolved Oxygen', 'Conductivity']

    # Define the custom color palette in HEX format (replace these with your desired colors)
    custom_color_palette = ['#FF9F1C', '#8FE1F4', '#169873', '#2081C3', '#EFE9AE', '#B57BA6']

    color_dict = {'Salinity': '#FF9F1C',
                  'Dissolved Oxygen': '#8FE1F4',
                  'Temperature(F)': '#169873',
                  'Conductivity': '#2081C3',
                  'pH': '#EFE9AE',
                  'Turbidity': '#B57BA6'}

    custom_theme = theme(
        # Background and grid
        panel_background=element_rect(fill='lightgray', color='white'),
        panel_grid_major=element_line(color='white', size=0.1),
        panel_grid_minor=element_blank(),

        # Axis
        axis_text=element_text(color='black', size=10, family='Arial'),
        axis_line=element_line(size=0.5),
        axis_ticks_major=element_line(size=0.5),
        axis_ticks_minor=element_blank(),

        # Legend
        legend_title=element_text(size=12),
        legend_key=element_blank(),

        # Plot title
        plot_title=element_text(size=16, hjust=0.5),
    )

    ggplot(data=df, mapping=aes(x='timestamp', y='value', fill='Group')) + \
    geom_bar(stat="identity", position=position_dodge()) + \
    theme_classic()

    p = (
            ggplot(df_melted, aes(x='timestamp', y='Value', fill='Variable')) +
            geom_area(stat='identity', position='stack') +
            ylim(0, 1000) +
            facet_wrap('Variable', nrow=len(df_melted['Variable'].unique())) +
            custom_theme +
            scale_fill_manual(values=custom_color_palette)  # Apply custom color palette
    )

    fig = px.area(df_melted, x='timestamp', y='Value', color='Variable', title='Stacked Sonification Graph',
                  color_discrete_map=color_dict,  # Apply custom color palette
                  hover_data={'Original_Value': False}, category_orders={'Variable': desired_order})

    fig.update_layout(
        xaxis=dict(title='Timestamp', showgrid=False),
        yaxis=dict(title='Sensors', showgrid=False, showticklabels=False),
        barmode='stack')

    plot_html = fig.to_html(include_plotlyjs='cdn')
    return render_template('graph.html', plot=plot_html)

if __name__ == '__main__':
    app.run(debug=True)
