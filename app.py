import matplotlib.pyplot as plt
import pandas as pd
from flask import Flask, render_template
from plotnine import *
from plotnine import theme

plt.switch_backend('agg')
import plotly.express as px
from plotnine import ggplot



app = Flask(__name__,static_url_path='/static')

@app.route('/')
def index():
    # This will read the Excel file and load the data into a pandas dataframe
    df = pd.read_csv('data.csv')

    df_melted = df.melt(
        id_vars=['timestamp'],
        value_vars=['Conductivity', 'Dissolved Oxygen', 'Salinity', 'Temperature(F)', 'Turbidity', 'pH'],
        var_name='Variable',
        value_name='Value'
    )

    df_melted['Original_Value'] = df_melted['Value']

    df_melted.loc[df_melted['Variable'] == 'Salinity', 'Value'] *= 30
    df_melted.loc[df_melted['Variable'] == 'Dissolved Oxygen', 'Value'] *= 1
    df_melted.loc[df_melted['Variable'] == 'Temperature(F)', 'Value'] *= 1
    df_melted.loc[df_melted['Variable'] == 'Conductivity', 'Value'] *= 0.3
    df_melted.loc[df_melted['Variable'] == 'pH', 'Value'] *= 10
    df_melted.loc[df_melted['Variable'] == 'Turbidity', 'Value'] *= 1

    desired_order = ['Salinity', 'pH', 'Temperature(F)', 'Turbidity', 'Dissolved Oxygen', 'Conductivity']

    color_dict = {'Salinity': '#FF9F1C',
                  'Dissolved Oxygen': '#8FE1F4',
                  'Temperature(F)': '#169873',
                  'Conductivity': '#2081C3',
                  'pH': '#EFE9AE',
                  'Turbidity': '#B57BA6'}

    fig = px.area(df_melted, x='timestamp', y='Value', color='Variable', title='Stacked Sonification Graph',
                  color_discrete_map=color_dict,  # Apply custom color palette
                  hover_data={'Original_Value': False}, category_orders={'Variable': desired_order})

    fig.update_layout(
        xaxis=dict(title='Timestamp', showgrid=False, nticks = 10),
        yaxis=dict(title='Sensors', showgrid=False, showticklabels=False),
        barmode='stack', paper_bgcolor="#030227", legend_font_color="white", font_color="white",
        title_font_family="Balto", legend_tracegroupgap=0,
        margin_b=5, margin_l=25, margin_r=25, margin_t=30)

    #fig.legend(bbox_to_anchor=(1.1, 1.05))

     #Extract data parameters
    #data_params = {
    #    'y': [item.legendgroup for item in fig.data],
    #                    # Add other data parameters as needed
    #}

    print(fig)

    plot_html = fig.to_html(include_plotlyjs='cdn')
    return render_template('graph.html', plot=plot_html)

if __name__ == '__main__':
    app.run(debug=True)

