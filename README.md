# FORMULISTIC

## Description:
>**Formulistic is an app that visualize telemetry data**. It makes use of "Formula1 2020" players to visualise their driving mistakes. This program records all the data of the car during a game session and generate a telemetry sheet. This application is a tool at the disposal of the player allowing a post analysis of his behavior on the track – providing both absolute and comparative analysis.

## Installation:
> 1. **Download the App**  
   Use this [link](https://codeload.github.com/Biboux07/FORMULISTIC/zip/main).<br/>A windows operating system as well as an [Python interpreter](https://docs.python.org/3/using/windows.html#windows-store) are required .

> 2. **Install the necessary python modules**  
    Open a terminal, go to the Formulistic folder and 
    type `$ pip3 install -r requirements.txt`,  
    depending on your python version, you might need to type
    `pip` instead of `pip3`.

> 3. **Launch the game**  
    To launch the game you can either create a shortcut on your desktop or use a terminal. In this case, go to your Formulistic folder and type `$ python3 main.py`, depending on your python version, you might need to type
    `python` instead of `python3`. 

## F1 2020 settings:
> 1. **Correctly set up the game**  
   There is few settings that need te be change in F1 2020 before recording data. <br/>First, go at `GAME-OPTIONS>Settings>Telemetry-Settings` and check that all variables are as follow: 

    UDP Telemetry: ON | UDP Broadcast Mode: ON | UDP IP Address: 127.0.0.1 | UDP Port: 20777 | UDP Send Rate: 20HZ | UDP Format 2020

> 2. **Gamemode**  
  `Time Trial` is the easiest gamemode to use while recording telemetry data. Moreover, remember that it is your last completed lap that will be shown in the graph. (not always your fastest) 

> 3. **Sessions**  
  Sessions are named like so : `FORMULISTIC_Sessionnumber.sqlite3`. They will appear in your `general formulistic folder`. Feel free to put them into your session folder as wished.


## Extra:
>Note, the app is currently in BETA. Updates will come over time. However,  if you are facing major issues feel free to conctact me at: `romain.pitton@gmail.com`. This app was been made by @Biboux07 as part of a post-secondary school capstone project. All rights reserved.