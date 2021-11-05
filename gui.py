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

        #self.promt_login()

        self.frame = tk.Frame(self.master, width=100, height=100)
        self.frame.pack()
        self.show_application()

        #self.frame.grid(row=0, column=1, padx=0, pady=0, sticky='')    

    def create_widgets(self):
        pass

    def place_widgets(self):
        pass
    
    def update_application(self):
        for widgets in self.frame.winfo_children():
            widgets.destroy()
        self.show_application()

    def show_application(self):
        self.login_label = tk.Label(self.frame, font=(("Arial", 12, 'italic')), text='Logged in as: {}'.format(self.username))
        
        self.device_header_label = tk.Label(self.frame, font=(("Arial", 16, 'bold underline')), text='Playback device')
        self.device_label = tk.Label(self.frame, font=(("Arial", 12)), text='Choose playback device:')
        self.device_var = tk.StringVar(self.master)
        self.devices = self.client.get_devices() if self.client else ['']
        self.active_device = self.client.get_active_device() if self.client is not None else ''
        self.device_var.set(str(self.active_device))
        self.device_option_menu = tk.OptionMenu(self.frame, self.device_var, *self.devices)
        self.device_refresh_button = tk.Button(self.frame, font=(("Arial", 12)), text='Refresh devices', command=self.update_devices)
        self.device_var.trace('w', self.change_device)

        self.playlist_header_label = tk.Label(self.frame, font=(("Arial", 16, 'bold underline')), text='Playlist:')
        self.load_playlist_label = tk.Label(self.frame, font=(("Arial", 12)), text='Load playlist:')
        self.browse_playlist_button = tk.Button(self.frame, font=(("Arial", 12)), text='Browse...', command=self.load_playlist)

        self.add_playlist_label = tk.Label(self.frame, font=(("Arial", 12)), text='Add currently playing song to playlist:')
        self.add_playlist_button = tk.Button(self.frame, font=(("Arial", 12)), text='Add', command=self.add_song_to_playlist)
        self.save_playlist_label = tk.Label(self.frame, font=(("Arial", 12)), text='Save changes made to playlist:')
        self.save_playlist_button = tk.Button(self.frame, font=(("Arial", 12)), text='Save', command=self.save_playlist)
        self.save_as_playlist_button = tk.Button(self.frame, font=(("Arial", 12)), text='Save as...', command=self.save_playlist_as)

        self.current_playlist_label = tk.Label(self.frame, font=(("Arial", 12, "italic")), text='Current playlist: {} ({})'.format(self.playlist_name, self.playlist_status))

        self.dj_header_label = tk.Label(self.frame, font=(("Arial", 16, 'bold underline')), text='DJ Controls:')

        self.dj_label = tk.Label(self.frame, font=(("Arial", 12)), text='DJ Controls:')
        self.goal_button = tk.Button(self.frame, font=(("Arial", 12)), text='MÅL!', command=lambda: self.goal())
        self.penalty_button = tk.Button(self.frame, font=(("Arial", 12)), text='Straffe', command=None)
        self.expulsion = tk.Button(self.frame, font=(("Arial", 12)), text='2 min', command=None)

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
        self.expulsion.grid(row=31, column=2, padx=0, pady=0, sticky='W')
    
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
                self.client.prepear_song(song=self.playlist.get_current_song())
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
                if dev.name == device_name.split(' (')[0]:
                    self.client.set_active_device(dev.id)
                    return
        except Exception as e:
            messagebox.showerror('Device error', 'Could not set device: ' + str(e))
        
        messagebox.showerror('Device error', 'Could not set device: ' + str(device_name))

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
            try:
                self.client = SpotifyClient(username=self.username)
                self.destroy_login()
                self.show_application()
            except SpotifyException as e:
                messagebox.showerror('Spotify errror', 'Something went wrong when loggin into spotify: ' + str(e.msg))
            except Exception as e:
                raise e
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


    def goal(self):
        self.client.play_song(self.playlist.get_current_song())
        self.client.ramp_up_volume()
        time.sleep(10)
        self.client.ramp_down_volume()
        self.client.pause_playback()
        self.playlist.next_song()


    def function_runner(func):
        def wrapper(self, *args, **kwargs):
            try:
                thread = threading.Thread(target=func, args=args, kwargs=kwargs)
                thread.start()
                return thread
            except SpotifyException as e:
                self.get_token(self.username)
                result = func(self, *args, **kwargs)
            return result
        return wrapper
    

def main(): 
    root = tk.Tk()
    app = Application(root)
    root.after(10, app.show_login)
    root.mainloop()

if __name__ == '__main__':
    main()