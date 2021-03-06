# MatchDJ
**NOTE: To get acces to the app, you need to send me a request with your mail and full name, so I can give you acces to the application.**

Application for playing songs for a handball match via spotify. 

Under development. Bugs may occur. Executables are only available on Windows and Ubuntu.

**Please feel free to contribute to the project if you find any bugs :)**

Executables can be created for Mac ruuning these commands in a terminal (you need to have **git** and **python3** installed): 
```
git clone https://github.com/Hlanden/MatchDJ.git
cd MatchDJ
pip install -r requirements.txt
pip install pyinstaller
pyinstaller -n MatchDJ --onefile src/main.py --windowed
```

## How to use it

### Running from executable
Download the executable folder for your OS. Unzip it an run it in from the unzipped folder.
* [Windows download](https://github.com/Hlanden/MatchDJ/raw/master/Executables/MatchDJ_Windows.zip)
* [Ubuntu download](https://github.com/Hlanden/MatchDJ/raw/master/Executables/MatchDJ_Ubuntu.zip)

### Running from terminal
If you don't want to use the executable you can run it in the following way from the terminal (you need to have **git** and **python3** installed): 
```
git clone https://github.com/Hlanden/MatchDJ.git
cd MatchDJ
pip install -r requirements.txt
python3 src/main.py
```

### Login
When you open the application, you need to log into your spotify and accept that the application can control your spotify. When you have logged in, this descision will be remembered the next time you use it. 

### Select device
Log into spotify on the device you want to play from. If it does not appear in the list, play a song on the device and press "Refresh devices" and try again. 

### Creating or loading playlists: 
You need to create playlists to use the application. Each time you press "Goal" a song from the playlist will be played for 10 seconds, starting the song at a given offset (so it starts at thedrop for instance). This is done in the following procedure:

1. Play a song on spotify 
2. Find the drop of the song
3. Pause the song 
4. Press the "Add" button

This will add the song to the current playlist. You will then see that the current playlist is unsaved. Press "Save As"/"Save" to save the playlist.

### Loading playlist
You can load premade playlists pressing the "Browse..." button. 

**An example playlist is added in the download folder**, and you can edit this as you like (or make your own).

### Using the app
* Goal: Whis will play a song for 10 seconds ramping the sound up in the start and down in the end. It will play it on 100 % volume for 7 seconds, and then turn the volume down to 50 % the last three seconds so a speaker can announce the scorer etc.
* 2 min: This will play "Du k??re lille snickerbo" for 15 seconds
* Straffe: This will play "Darth Vaders theme" for 15 seconds

Enjoy :) 
