A How-To Sonification Guide by Alex Rosenberg and Lloyd Boadi-Amoah

1. Clone both the Sonify-API-Data and Sonification Frontend repositories found on Github  

2. Obtain the data from the API (We used 8 months worth of data)  
   1. You will need to change the link of the start date/time, and the end date/time. For example:   
      1. For example, it will be from this: https://colabprod01.pace.edu/api/influx/sensordata/Alan/range?start\_date=2011-01-01T00:00:00\&stop\_date=2012-02-01T23:59:59 to this: https://colabprod01.pace.edu/api/influx/sensordata/Alan/range?start\_date=2011-08-01T00:00:00\&stop\_date=2013-02-01T23:59:59  
      2. You can also change the data name from Alan to Odin or any location relevant to Blue CoLab that you would prefer.  
   2. Turn that .json file into a csv file  

3. In the Sonify-API-Datarepository…  
   1. Put your csv file in the examples folder  
   2. Open [PresentationSounds.ipynb](http://PresentationSounds.py) (We used and recommend VS Code)  
   3. Create a Virtual Environment in VS Code (SONIFICATION_GUIDE.md will show you how to do that)  
   4. Install required libraries from requirements.txt  
   5. Change the csv file name in the code to match your file  
   6. Run the program and you should have 14 .mid files  

4. Now that you have the midi…  
   1. Ignore water\_sensor files  
   2. Ignore \_year files  
   3. Take the 6 midi files and convert them to .mp3 files  
      1. You can do this in a DAW (Digital Audio Workstation) We used [bandlab.com](http://bandlab.com) you could use Garageband if you have a Mac  
      2. You can also use a midi to mp3 website. (This will assign all instruments to basic piano, but that’s not recommended)  
   4. Take the 6 mp3 files and put them in sonification-flask/static/audio folder  

5. Put your data csv file in the sonification frontend repo  

6. Open [app.py](http://app.py)  
   1. Create a virtual environment like before and install required libraries from requirements.txt  
   2. Change the csv file name in the code to match your file  
   3. Run the program   
   4. Click the link in the terminal  
   5. You will now see the full sonification with your graph\!