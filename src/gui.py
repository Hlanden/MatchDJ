import tkinter as tk
from tkinter import filedialog

from spotipy.exceptions import SpotifyException
from client import SpotifyClient
from playlist import Playlist, Song
from tkinter import StringVar
import time 
import os
from tkinter import messagebox
import threading
import glob

class Application:
    def __init__(self, master):
        self.master = master
        self.username = ''
        self.client = None
        self.active_device = None
        self.devices = []
        self.playlist = Playlist()
        self.playlist_name = 'New Playlist'
        self.playlist_path = ''
        self.playlist_status = 'unsaved'
        self.thread_queue = []
        
        
        self.penalty_song = Song(uri='spotify:track:2bw4WgXyXP90hIex7ur58y',
                                 timestamp=10000,
                                 name='The Imperial Match (Darth Vaders Theme)')
        self.expulsion_song = Song(uri='spotify:track:13XKaf7SFcvG4iXmFkNiWr',
                                   timestamp=17000,
                                   name='Du käre lille snickerbo')

        #self.promt_login()

        self.frame = tk.Frame(self.master, width=100, height=100, bg='#e1f5fe')
        self.frame.pack()
        self.show_application()

        #self.frame.grid(row=0, column=1, padx=0, pady=0, sticky='')    
    
    def _spotify_function_runner(func):
        def wrapper(self, *args, **kwargs):
            try:
                if not self.username: 
                    messagebox.showerror('Not logged in', 'Please log in with a spotify user')
                    return
                if not self.client:
                    messagebox.showerror('No spotify connected', 'Please connect to a spotify application.')
                    return
                if not self.active_device:
                    messagebox.showerror('No active device', 'Please open a spotify application, refresh devices and connect to a device.')
                    return 
                if not self.playlist.playlist:
                    messagebox.showerror('No playlist selected', 'Please create or load a playlist.')
                    return 
                
                if len(threading.enumerate()) > 1:
                    messagebox.showerror('Spotify function already running', 'Spotify function allready running. Please wait.')
                else:
                    thread = threading.Thread(target=func, args=(self, *args), kwargs=kwargs)
                    thread.start()
                    return thread
                
            except SpotifyException as e:
                self.get_token(self.username)
                thread = threading.Thread(target=func, args=(self, *args), kwargs=kwargs)
                thread.start()
                return thread
        return wrapper
    
    def create_widgets(self):
        pass

    def place_widgets(self):
        pass
    
    def update_application(self):
        for widgets in self.frame.winfo_children():
            widgets.destroy()
        self.show_application()

    def show_application(self):
        self.login_label = tk.Label(self.frame, 
                                    font=(("Arial", 12, 'italic')), 
                                    text='Logged in as: {}'.format(self.username), 
                                    bg='#e1f5fe')
        
        self.device_header_label = tk.Label(self.frame, 
                                            font=(("Arial", 16, 'bold underline')), 
                                            text='Playback device', 
                                            bg='#e1f5fe')
        self.device_label = tk.Label(self.frame, 
                                     font=(("Arial", 12)), 
                                     text='Choose playback device:', 
                                     bg='#e1f5fe')
        
        self.device_var = tk.StringVar(self.master)
        self.devices = self.client.get_devices() if self.client else [None]
        if not self.devices: 
            self.devices.append(None)
        self.active_device = self.client.get_active_device() if self.client is not None else None
        self.device_var.set(str(self.active_device))
        
        self.device_option_menu = tk.OptionMenu(self.frame, self.device_var, *self.devices)
        self.device_option_menu.configure(bg='#bbdefb')
        self.device_refresh_button = tk.Button(self.frame, 
                                               font=(("Arial", 12)), 
                                               text='Refresh devices', 
                                               command=self.update_devices,
                                               bg='#bbdefb')
        self.device_var.trace('w', self.change_device)

        self.playlist_header_label = tk.Label(self.frame, 
                                              font=(("Arial", 16, 'bold underline')), 
                                              text='Playlist:', 
                                              bg='#e1f5fe')
        self.load_playlist_label = tk.Label(self.frame, 
                                            font=(("Arial", 12)), 
                                            text='Load playlist:', 
                                            bg='#e1f5fe')
        self.browse_playlist_button = tk.Button(self.frame, 
                                                font=(("Arial", 12)), 
                                                text='Browse...', 
                                                command=self.load_playlist,
                                                bg='#bbdefb')

        self.add_playlist_label = tk.Label(self.frame, 
                                           font=(("Arial", 12)), 
                                           text='Add currently playing song to playlist:',
                                           bg='#e1f5fe')
        self.add_playlist_button = tk.Button(self.frame, 
                                             font=(("Arial", 12)), 
                                             text='Add', 
                                             command=self.add_song_to_playlist,
                                             bg='#bbdefb')
        self.save_playlist_label = tk.Label(self.frame, 
                                            font=(("Arial", 12)), 
                                            text='Save changes made to playlist:',
                                            bg='#e1f5fe')
        self.save_playlist_button = tk.Button(self.frame, 
                                              font=(("Arial", 12)), 
                                              text='Save', 
                                              command=self.save_playlist,
                                              bg='#bbdefb')
        self.save_as_playlist_button = tk.Button(self.frame, 
                                                 font=(("Arial", 12)), 
                                                 text='Save as...', 
                                                 command=self.save_playlist_as,
                                                 bg='#bbdefb')

        self.current_playlist_label = tk.Label(self.frame, 
                                               font=(("Arial", 12, "italic")), 
                                               text='Current playlist: {} ({})'.format(self.playlist_name.split('.') [0], self.playlist_status),
                                               bg='#e1f5fe')

        self.dj_header_label = tk.Label(self.frame, 
                                        font=(("Arial", 16, 'bold underline')), 
                                        text='DJ Controls:',
                                        bg='#e1f5fe')

        self.dj_label = tk.Label(self.frame, 
                                 font=(("Arial", 12)), 
                                 text='DJ Controls:',
                                 bg='#e1f5fe')
        self.goal_button = tk.Button(self.frame, 
                                     font=(("Arial", 12)), 
                                     text='MÅL!', 
                                     command=lambda: self.goal(),
                                     bg='green')
        self.penalty_button = tk.Button(self.frame, 
                                        font=(("Arial", 12)), 
                                        text='Straffe', 
                                        command=lambda: self.penalty(),
                                        bg='yellow')
        self.expulsion_button = tk.Button(self.frame, 
                                          font=(("Arial", 12)), 
                                          text='2 min', 
                                          command=lambda: self.expulsion(),
                                          bg='red')

        self.login_label.grid(row=1, column=1, padx=0, pady=5, sticky='')

        self.device_header_label.grid(row=2, column=1, padx=0, pady=5, sticky='')
        self.device_label.grid(row=3, column=1, padx=0, pady=5, sticky='')
        self.device_option_menu.grid(row=4, column=1, padx=0, pady=0, sticky='')
        self.device_refresh_button.grid(row=5, column=1, padx=0, pady=0, sticky='')

        self.playlist_header_label.grid(row=9, column=1, padx=0, pady=10, sticky='')
        self.current_playlist_label.grid(row=10, column=1, padx=0, pady=10, sticky='')
        self.load_playlist_label.grid(row=11, column=1, padx=0, pady=0, sticky='')
        self.browse_playlist_button.grid(row=12, column=1, padx=0, pady=0, sticky='')

        self.add_playlist_label.grid(row=20, column=1, padx=0, pady=5, sticky='')
        self.add_playlist_button.grid(row=21, column=1, padx=0, pady=0, sticky='')
        self.save_playlist_label.grid(row=22, column=1, padx=0, pady=0, sticky='') 
        self.save_playlist_button.grid(row=23, column=1, padx=0, pady=0, sticky='W')
        self.save_as_playlist_button.grid(row=23, column=1, padx=0, pady=0, sticky='E')


        self.dj_header_label.grid(row=29, column=1, padx=0, pady=10, sticky='')
        self.dj_label.grid(row=30, column=1, padx=0, pady=0, sticky='')
        self.penalty_button.grid(row=31, column=0, padx=0, pady=0, sticky='E')
        self.goal_button.grid(row=31, column=1, padx=0, pady=0, sticky='')
        self.expulsion_button.grid(row=31, column=2, padx=0, pady=0, sticky='W')
    
    def load_playlist(self):
        filename = filedialog.askopenfilename(filetypes=[('JSON Files', '*.json')])
        try:
            if filename:
                playlist = Playlist()
                playlist.load_playlist(filename)
                self.playlist_path = filename
                self.playlist_name = os.path.basename(filename)
                self.playlist = playlist
                self.playlist_status = 'saved'
                self.update_application()
        except Exception as e:
            messagebox.showerror('Load error', 'Could not load playlist: ' + str(e))
            
    def save_playlist(self):
        try:
            if self.playlist_name == 'New Playlist':
                self.save_playlist_as()
            elif self.playlist and self.playlist_path:
                self.playlist.save_playlist(self.playlist_path)
                self.playlist_status = 'saved'
                self.update_application()
        except Exception as e:
            messagebox.showerror('Save error', 'Could not save playlist: ' + str(e))

    def save_playlist_as(self):
        filename = filedialog.asksaveasfilename(filetypes=[('JSON Files', '*.json')])
        try:
            if filename:
                self.playlist_path = filename
                self.playlist_name = os.path.basename(self.playlist_path)
                self.playlist.save_playlist(self.playlist_path + '.json')
                self.playlist_status = 'saved'
                self.update_application()
        except Exception as e:
            messagebox.showerror('Save error', 'Could not save playlist: ' + str(e))
    
    def add_song_to_playlist(self):
        try:
            song = self.client.get_current_song()
            self.playlist.add_song_to_playlist(song)
            if self.playlist_status != 'unsaved changes':
                self.playlist_status = 'unsaved changes'
                self.update_application()
        except Exception as e:
            messagebox.showerror('Error', 'Could not add song to playlist: ' + str(e))

    def change_device(self, *args):
        try: 
            device_name = self.device_var.get()
            for dev in self.devices:
                if device_name != 'None' and dev is not None and dev.name == device_name.split(' (')[0]:
                    self.client.set_active_device(dev.id)
                    return
        except Exception as e:
            messagebox.showerror('Device error', 'Could not set device: ' + str(device_name) + '\nError: ' + str(e))

    def update_devices(self, *args):
        try: 
            self.devices = self.client.get_devices() if self.client else ['']
            print('Devices: ', str(self.devices))
            self.active_device = self.client.get_active_device() if self.client is not None else ''
            self.device_var.set(str(self.active_device))
            #self.device_option_menu = tk.OptionMenu(self.frame, self.device_var, *self.devices)
            self.device_option_menu.children['menu'].delete(0, 'end')
            for value in self.devices:
                self.device_option_menu.children['menu'].add_command(label=value, command=lambda v=value: self.device_var.set(v))
        except Exception as e:
            messagebox.showerror('Device error', 'Could not set device: ' + str(e))


    def show_login(self):
        self.window_login = tk.Toplevel(self.master)
        self.frame_login = tk.Frame(self.window_login)
        self.frame_login.focus_set()
        self.frame_login.pack()

        self.username_label = tk.Label(self.frame_login, font=(("Arial", 12)), text="User Name")
        self.username_var = tk.StringVar()
        self.username_entry = tk.Entry(self.frame_login, textvariable=self.username_var)
        self.username_entry.bind('<Return>', lambda x: self.login())
        self.login_button = tk.Button(self.frame_login, text = 'Login', width = 25, command = self.login)

        self.username_label.grid(row=0, column=1, padx=0, pady=0, sticky='')
        self.username_entry.grid(row=1, column=1, padx=0, pady=0, sticky='')
        self.login_button.grid(row=2, column=1, padx=0, pady=0, sticky='')
    
    def login(self):
        if self.username_var.get():
            self.username = self.username_var.get()
            tokens = [os.path.basename(x) for x in glob.glob(os.path.join(os.getcwd(), 'tokens/.*'))]
            print('Tokens: ', tokens)
            if not ".cache-" +self.username in tokens:
                yesno= messagebox.askyesno("New user", f"User: {self.username} does not exist. Do you want to add a new user?")
                if not yesno:
                    self.username = ''
                    return 
            try:
                self.client = SpotifyClient(username=self.username)
                self.destroy_login()
                self.show_application()
            except SpotifyException as e:
                messagebox.showerror('Spotify errror', 'Something went wrong when loggin into spotify: ' + str(e.msg))
                self.username = ''
            except Exception as e:
                self.username = ''
                messagebox.showerror('Error', 'Something went wrong when loggin into spotify: ' + str(e))
        else:
            messagebox.showerror('Error', 'Enter a valid username')
            # self.hide_login()
            # self.show_application()

    def destroy_login(self):
        for widgets in self.frame_login.winfo_children():
            widgets.destroy()
        self.window_login.destroy()

    def quit(self):
        self.master.destroy()

    @_spotify_function_runner
    def goal(self):
        self.client.volume(0)
        self.playlist.next_song()
        self.client.play_song(self.playlist.get_current_song())
        self.client.ramp_up_volume(number_of_steps=5, pause=0.2)
        time.sleep(10)
        self.client.ramp_down_volume(number_of_steps=5, pause=0.2)
        self.client.pause_playback()
        
    @_spotify_function_runner
    def penalty(self):
        self.client.play_for_time_duration(self.penalty_song, 
                                           time_duration=8,
                                           number_of_steps=5,
                                           pause=0.2)
    
    @_spotify_function_runner
    def expulsion(self):
        self.client.play_for_time_duration(self.expulsion_song, 
                                           time_duration=10,
                                           number_of_steps=5,
                                           pause=0.2)