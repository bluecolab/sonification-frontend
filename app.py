import matplotlib.pyplot as plt  # Importing matplotlib for plotting
import pandas as pd  # Importing pandas for data manipulation
from flask import Flask, render_template, request # Importing Flask for web app and render_template for rendering HTML templates
from plotnine import *  # Importing plotnine for ggplot functionality
import os
import datetime as dt
import re
from audiolazy_functions import str2midi, midi2str
from midiutil import MIDIFile 
import subprocess
import fluidsynth

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

    file_names = [file_object(x) for x in os.scandir(base_folder_path)] 
    # Adds time from 1-294 to csv file (timestamp returns a string and convertion to int returns a large int)
    # Check time, if time is in the csv file returns true else adds time into the file
    list_of_column_names = list(df.columns)
    if 'time' not in list_of_column_names:
        print("time was not found, adding time now!!!!")
        add_time_to_csv(selected_file)
    else:
        print("time was found, not adding time!!!!")

    wav_files = [x for x in os.scandir('./static/audio/')]
    print(wav_files)
    generate_mp3_files = False
    for data in desired_order:
        target_file = selected_file + '_' + data + '.wav'
        if any(x.name == target_file for x in wav_files):
            pass
        else:
            generate_mp3_files = True
            
    if generate_mp3_files == True:
        for data in desired_order:
            convert_to_music(selected_file, data)
        # for data in desired_order:
        #     subprocess.run(["ffmpeg", "-y", "-i", './static/audio/' + selected_file + '_' + data + '.mid', "-codec:a", "libmp3lame", './static/audio/' + selected_file + '_' + data + '.mp3'])

    # Converting the plot to HTML format to embed in the web page using Plotly
    plot_html = fig.to_html(include_plotlyjs='cdn')   
    
    # Rendering the graph.html template and passing the plot HTML to it using Flask
    return render_template('graph.html', plot=plot_html, files=file_names, current_file=selected_file)

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

def add_time_to_csv(filename):
    # Reads csv file
    df = pd.read_csv('./data/' + filename + '.csv')  #load data as a pandas dataframe
    time = []
    for i in range(0, len(df)):
        time.append(i)
    df['time'] = time
    df.to_csv('./data/' + filename + '.csv', index=False)

def convert_to_music(filename, data):
    df = pd.read_csv('./data/' + filename + '.csv')

    # soundfont_path = './static/soundfont/Guitar.sf2'
    match data:
        case "sensors__pH":
            soundfont_path = './static/soundfont/Flute.sf2'
            tempo = 1
        case "sensors__Cond":
            soundfont_path = './static/soundfont/Solo Violin.sf2'
            tempo = 3
        case "sensors__DOpct":
            soundfont_path = './static/soundfont/Tuba.sf2'
            tempo = 2
        case "sensors__Sal":
            soundfont_path = './static/soundfont/Acoustic Guitar.sf2'
            tempo = 1
        case "sensors__Temp":
            soundfont_path = './static/soundfont/Octave Choir.sf2'
            tempo = 1
        case "sensors__Turb":
            soundfont_path = './static/soundfont/Acoustic Piano.sf2'
            tempo = 2
    
    ages = df['time'].values   #get age values in an array
    diameters = df[data].values  #get diameter values in an array

    times_myrs = max(ages) - ages  #measure time from 1st impact in data

    myrs_per_beat = 5  #conversion factor: Myrs for each beat of music
    t_data = times_myrs/myrs_per_beat #compress impact times from Myrs to beats

    y_data = map_value(diameters, min(diameters), max(diameters), 0, 1) 

    # y_scale = 0.5  #lower than 1 to spread out more evenly
    # y_data = y_data**y_scale
    # note_names = ['C2','D2','E2','G2','A2',
    #          'C3','D3','E3','G3','A3',
    #          'C4','D4','E4','G4','A4']
    note_names = ['C1','C2','G2',
             'C3','E3','G3','A3','B3',
             'D4','E4','G4','A4','B4',
             'D5','E5','G5','A5','B5',
             'D6','E6','F#6','G6','A6']
    note_midis = [str2midi(n) for n in note_names] 
    n_notes = len(note_midis)
    midi_data = []
    for i in range(len(y_data)):
        note_index = round(map_value(y_data[i], 0, 1, n_notes-1, 0)) 
        midi_data.append(note_midis[note_index])

    vel_min,vel_max = 35,117   #minimum and maximum note velocity
    vel_data = []
    for i in range(len(y_data)):
        note_velocity = round(map_value(y_data[i],0,1,vel_min, vel_max)) 
        vel_data.append(note_velocity)

    #create midi file object, add tempo
    my_midi_file = MIDIFile(1) #one track 
    my_midi_file.addTempo(track=0, time=0, tempo=tempo) 
    #add midi notes
    for i in range(len(t_data)):
        my_midi_file.addNote(track=0, channel=0, time=t_data[i], pitch=midi_data[i], volume=vel_data[i], duration=2)
    #create and save the midi file itself
    with open('./static/audio/' + filename + '_' + data +'.mid', "wb") as f:
        my_midi_file.writeFile(f)

    audio_path = './static/audio/' + filename + '_' + data + '.wav'
        
    command = [
        'fluidsynth',
        '-ni',  # non-interactive mode
        '-F', audio_path,  # output file
        soundfont_path,
        './static/audio/' + filename + '_' + data +'.mid'
    ]
    
    subprocess.run(command, check=True)
    # pygame.init()
    # pygame.mixer.music.load(filename + '.mid')
    # pygame.mixer.music.play()

def map_value(value, min_value, max_value, min_result, max_result):
    result = min_result + (value - min_value)/(max_value - min_value)*(max_result - min_result)
    return result

# Running the Flask application
if __name__ == '__main__':
    app.run(debug=True)
