from dataclasses import dataclass, field
from typing import List
import json 
import random

@dataclass
class Song: 
    uri: str
    timestamp: int
    name: str = ''

    def __eq__(self, o: object) -> bool:
        return self.uri == o.uri

class Playlist:
    def __init__(self) -> None:
        self.song_index = 0
        self.playlist: List[Song] = []

    def add_song_to_playlist(self, song):
        if song not in self.playlist:
            self.playlist.append(song)
        else:
            self.playlist[self.playlist.index(song)].timestamp = song.timestamp
    
    def shuffle_playlist(self):
        random.shuffle(self.playlist)
    
    def get_next_song(self):
        self.song_index += 1
        if self.song_index >= len(self.playlist):
            self.song_index = 0
        return self.playlist[self.song_index]

    def save_playlist(self, path:str):
        with open(path, 'w+') as file:
            data = json.dumps([song.__dict__ for song in self.playlist])
            file.write(data)

    def load_playlist(self, path:str):
        with open(path, 'r') as file:
            data = [Song(**song) for song in json.load(file)]
            self.playlist = data
    
    def __repr__(self) -> str:
        s = ''
        for song in self.playlist:
            s += str(song) + '\n' 
        return s


if __name__ == '__main__':
    song = Song(uri='spotify:track:3Sxd2zTEoWwMPAVbBJGwAC', timestamp=164872)
    playlist = Playlist()
    playlist.add_song_to_playlist(song)
    playlist.save_playlist(path = 'playlists/test_playlist.json')
    

    playlist2 = Playlist()
    playlist2.load_playlist(path = 'playlists/test_playlist.json')

    print(playlist)
    # print(playlist2)
    # print(playlist.playlist[0] == playlist2.playlist[0])
    song.timestamp = 10
    playlist.add_song_to_playlist(song)
    print(playlist)