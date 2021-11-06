from os import name
import spotipy
from spotipy.exceptions import SpotifyException
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOauthError
from dataclasses import dataclass, field
from typing import List
import time
from playlist import Playlist, Song
from pathlib import Path

class SpotifyInitException(Exception):
    pass

class GetDevicesException(Exception):
    pass

class SetDeviceException(Exception):
    pass

@dataclass
class PlaybackDevice: 
    name: str
    type: str
    id: str
    is_active: bool
    volume_percent: int
    is_private_session: bool
    is_restricted: bool

    def __repr__(self) -> str:
        return '{} ({})'.format(self.name, self.type)

class SpotifyClient(spotipy.Spotify):
    def __init__(self, username, **kwargs):
        self.username = username
        self.token: str = ''
        self.playbackDevices: List[PlaybackDevice] = []
        self.active_device: PlaybackDevice = None
        Path("tokens/").mkdir(parents=True, exist_ok=True)


        try:
            self.token = self.get_token(self.username)
            super().__init__(auth=self.token, **kwargs)
        except Exception as e:
            raise SpotifyInitException('Could not initialize spotify client: ' + str(e))

        self.playbackDevices = self.get_devices()
    
    def _refresh_token_if_expired(func):
        def wrapper(self, *args, **kwargs):
            try:
                result = func(self, *args, **kwargs)
            except SpotifyOauthError:
                self.get_token(self.username)
                result = func(self, *args, **kwargs)
            return result
        return wrapper

    def get_token(self, username:str):
        token = util.prompt_for_user_token(username,
                                           scope=('user-modify-playback-state '
                                                  'user-read-currently-playing '
                                                  'user-read-playback-state '
                                                  'user-read-playback-position'),
                                           client_id='deaee968a7a64560a77b72ab06b7095b',
                                           client_secret='ab6950b1df03424d81631fbb790e71be',
                                           redirect_uri='http://localhost:8080/',
                                           cache_path='tokens/.cache-{}'.format(username)
                                           )
        return token                                       

    @_refresh_token_if_expired
    def get_devices(self):
        try:
            devices = [PlaybackDevice(**dev) for dev in self.devices()['devices']]
        except Exception as e:
            raise GetDevicesException('Could not get active devices from spotify client: \n' + str(e))

        return devices
    
    @_refresh_token_if_expired
    def get_active_device(self):
        for dev in self.get_devices():
            if dev.is_active:
                self.active_device = dev
                return dev
        return None
    
    @_refresh_token_if_expired
    def set_active_device(self, device_id: str):
        try:
            super().transfer_playback(device_id=device_id)
        except SpotifyException as e:
            raise SetDeviceException('Coiuld not activate given device: ' + str(e))

    
    @_refresh_token_if_expired
    def ramp_up_volume(self, number_of_steps:int=10, pause:float=0.1):
        self.volume(0)
        for i in range(number_of_steps):
            self.volume(int(i*100/number_of_steps))
            time.sleep(pause)
        self.volume(100)
    
    @_refresh_token_if_expired
    def ramp_down_volume(self, number_of_steps:int=10, pause:float=0.1, goal_vol=0):
        current_vol = self.get_current_volume()
        for i in range(number_of_steps):
            self.volume(current_vol - int(i*(current_vol-goal_vol)/number_of_steps))
            time.sleep(pause)
        self.volume(goal_vol)

    @_refresh_token_if_expired
    def start_playback(self, **kwargs):
        try:
            super().start_playback(**kwargs)
        except spotipy.SpotifyException as e:
            if e.http_status == 403:
                # Already playing
                return
            else:
                raise e
    
    @_refresh_token_if_expired
    def pause_playback(self, **kwargs):
        try:
            super().pause_playback(**kwargs)
        except spotipy.SpotifyException as e:
            if e.http_status == 403:
                # Already paused
                return
            else:
                raise e
    
    @_refresh_token_if_expired
    def play_for_time_duration(self, song:Song, time_duration:float=10, number_of_steps:int=10, pause:float=0.1, **kwargs):
        self.play_song(song)
        self.ramp_up_volume(number_of_steps=number_of_steps, pause=pause)
        time.sleep(time_duration)
        self.ramp_down_volume(number_of_steps=number_of_steps, pause=pause)
        self.pause_playback()

    @_refresh_token_if_expired
    def get_current_song(self):
        playback_dict = self.current_playback()
        try: 
            name = playback_dict['item']['name']
            uri = playback_dict['item']['uri']
            timestamp = playback_dict['progress_ms']
            return Song(uri=uri, timestamp=timestamp, name=name)
        except Exception as e:
            print('Failed to get current song: ', e)
            return
    
    @_refresh_token_if_expired
    def get_current_volume(self):
        volume = self.current_playback()['device']['volume_percent']
        return volume

    @_refresh_token_if_expired
    def prepear_song(self, song:Song):
        self.volume(0)
        self.start_playback(uris=[song.uri],
                            position_ms=song.timestamp)
        self.pause_playback()
    
    @_refresh_token_if_expired
    def play_song(self, song:Song):
        self.start_playback(uris=[song.uri],
                            position_ms=song.timestamp)

if __name__=='__main__':
    username = 'jorgen1998'
    sp = SpotifyClient(username=username)
    song = Song(uri='spotify:track:3Sxd2zTEoWwMPAVbBJGwAC', timestamp=164872)
    print(sp.prepear_song(song))
    #sp.play_for_time_duration()
    #sp.pause_playback()
