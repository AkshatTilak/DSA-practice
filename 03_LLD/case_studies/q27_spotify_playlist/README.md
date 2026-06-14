# Spotify Playlist Manager LLD

## 1. Overview & System Requirements

The **Spotify Playlist Manager** is a Low-Level Design (LLD) challenge focused on managing collections of media (songs) and controlling the playback experience. The system must handle the organization of songs into playlists, user ownership, and a playback engine capable of various modes (Sequential, Shuffle, Repeat).

### Core Entities
- **Song**: The atomic unit of the system containing metadata.
- **Playlist**: A named collection of songs that can be modified.
- **User**: The actor who creates and manages playlists.
- **MusicPlayer**: The engine that handles the logic of playing, skipping, and shuffling songs.

### Functional Requirements
1. **Playlist Management**:
    - Create a new playlist.
    - Add/Remove songs from a playlist.
    - Search for a song within a specific playlist.
2. **Playback Control**:
    - Play songs in a sequential order.
    - Shuffle the current playlist.
    - Repeat a single song or the entire playlist.
    - Skip to the next song or go back to the previous song.
3. **User Association**: 
    - Only the owner of a playlist (or an authorized user) should be able to modify it.

---

## 2. Design Principles & Patterns

To ensure the system is scalable and maintainable, the following OOP principles and design patterns are applied:

### SOLID Principles
- **Single Responsibility Principle (SRP)**: 
    - `Song` only holds data.
    - `Playlist` manages the collection of songs.
    - `MusicPlayer` handles the state of playback.
    - This prevents the "God Object" anti-pattern.
- **Open/Closed Principle (OCP)**: The playback logic is designed such that new playback strategies (e.g., "Smart Shuffle" or "Crossfade") can be added without modifying the core `MusicPlayer` class.
- **Interface Segregation**: By separating the `Playlist` interface from the `Playback` logic, we ensure that a user who only wants to organize songs isn't forced to deal with audio hardware/streaming logic.

### Design Patterns
- **Strategy Pattern**: Used for **Playback Modes**. Instead of using massive `if-else` blocks inside the `next_song()` method, we define strategies for `SequentialPlayback`, `ShufflePlayback`, and `RepeatPlayback`.
- **Singleton Pattern**: The `MusicPlayer` is typically implemented as a Singleton because a device usually has only one active audio output stream.
- **Observer Pattern (Conceptual)**: Though not explicitly coded in the basic version, an Observer pattern would be used to notify a UI component whenever the `current_song` changes.

---

## 3. Class Structure & Relationships

### Class Diagram (ASCII)

```text
+----------------+       1    * +------------------+
|      User      |-------------->|     Playlist     |
+----------------+               +------------------+
| - userId       |               | - playlistId     |
| - username     |               | - name           |
| - playlists[]  |               | - songs: List<Song>|
+----------------+               +------------------+
                                           | *
                                           v
+----------------+               +------------------+
|   MusicPlayer  | <------------ |       Song       |
+----------------+               +------------------+
| - currentSong  |               | - songId         |
| - currentIndex |               | - title          |
| - playbackMode |               | - artist         |
+----------------+               | - duration       |
| + play()       |               +------------------+
| + next()       |
| + shuffle()    |
+----------------+
```

### Relationships
- **User $\rightarrow$ Playlist**: One-to-Many (Composition/Aggregation). A user owns multiple playlists.
- **Playlist $\rightarrow$ Song**: Many-to-Many. A song can exist in multiple playlists, and a playlist contains many songs.
- **MusicPlayer $\rightarrow$ Playlist**: Association. The player operates on a specific playlist instance at a time.

---

## 4. Step-by-Step Logic & Code Walkthrough

### Implementation

```python
import random
from enum import Enum
from typing import List, Optional

class PlaybackMode(Enum):
    SEQUENTIAL = 1
    SHUFFLE = 2
    REPEAT_ONE = 3
    REPEAT_ALL = 4

class Song:
    def __init__(self, song_id: str, title: str, artist: str, duration: int):
        self.song_id = song_id
        self.title = title
        self.artist = artist
        self.duration = duration

    def __repr__(self):
        return f"'{self.title}' by {self.artist}"

class Playlist:
    def __init__(self, playlist_id: str, name: str, owner: 'User'):
        self.playlist_id = playlist_id
        self.name = name
        self.owner = owner
        self.songs: List[Song] = []

    def add_song(self, song: Song):
        self.songs.append(song)
        print(f"Added {song.title} to {self.name}")

    def remove_song(self, song_id: str):
        self.songs = [s for s in self.songs if s.song_id != song_id]

    def search_song(self, query: str) -> List[Song]:
        return [s for s in self.songs if query.lower() in s.title.lower()]

class MusicPlayer:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MusicPlayer, cls).__new__(cls)
            cls._instance._init_player()
        return cls._instance

    def _init_player(self):
        self.current_playlist: Optional[Playlist] = None
        self.current_song_index = 0
        self.mode = PlaybackMode.SEQUENTIAL
        self.is_playing = False

    def load_playlist(self, playlist: Playlist):
        self.current_playlist = playlist
        self.current_song_index = 0
        print(f"Loaded playlist: {playlist.name}")

    def set_mode(self, mode: PlaybackMode):
        self.mode = mode
        print(f"Playback mode changed to: {mode.name}")

    def play(self):
        if not self.current_playlist or not self.current_playlist.songs:
            print("No songs to play.")
            return
        
        song = self.current_playlist.songs[self.current_song_index]
        print(f"Playing: {song}")
        self.is_playing = True

    def next(self):
        if not self.current_playlist: return

        songs = self.current_playlist.songs
        if self.mode == PlaybackMode.REPEAT_ONE:
            print("Repeat One enabled. Playing same song.")
            return

        if self.mode == PlaybackMode.SHUFFLE:
            self.current_song_index = random.randint(0, len(songs) - 1)
        else: # SEQUENTIAL or REPEAT_ALL
            self.current_song_index = (self.current_song_index + 1) % len(songs)
        
        self.play()

    def previous(self):
        if not self.current_playlist: return
        
        songs = self.current_playlist.songs
        # Move back, wrap around if at the start
        self.current_song_index = (self.current_song_index - 1) % len(songs)
        self.play()

class User:
    def __init__(self, user_id: str, username: str):
        self.user_id = user_id
        self.username = username
        self.playlists: List[Playlist] = []

    def create_playlist(self, playlist_id: str, name: str) -> Playlist:
        new_playlist = Playlist(playlist_id, name, self)
        self.playlists.append(new_playlist)
        return new_playlist

# --- Execution Example ---
if __name__ == "__main__":
    # Setup Data
    user1 = User("U1", "Alice")
    s1 = Song("S1", "Blinding Lights", "The Weeknd", 200)
    s2 = Song("S2", "Stay", "Justin Bieber", 180)
    s3 = Song("S3", "Levitating", "Dua Lipa", 210)

    my_list = user1.create_playlist("P1", "Gym Hits")
    my_list.add_song(s1)
    my_list.add_song(s2)
    my_list.add_song(s3)

    # Playback Logic
    player = MusicPlayer()
    player.load_playlist(my_list)
    
    player.play()       # Plays Blinding Lights
    player.next()       # Plays Stay
    
    player.set_mode(PlaybackMode.SHUFFLE)
    player.next()       # Plays a random song
    
    player.set_mode(PlaybackMode.REPEAT_ONE)
    player.next()       # Plays the same song again
```

### Logic Walkthrough
1. **Initialization**: The `User` creates a `Playlist` object. This playlist acts as a wrapper around a `List[Song]`.
2. **Loading**: The `MusicPlayer` (Singleton) loads the playlist. This sets the context for all subsequent `play`, `next`, and `previous` calls.
3. **State Management**: The `MusicPlayer` maintains a `current_song_index`. 
4. **Mode Handling**:
    - **Sequential**: Increments index by 1. Uses modulo operator (`% len(songs)`) to wrap back to the start (effectively `REPEAT_ALL`).
    - **Shuffle**: Uses `random.randint` to jump to any index in the list.
    - **Repeat One**: Simply ignores the `next()` command's index increment logic.

---

## 5. Complexity Analysis

| Operation | Time Complexity | Space Complexity | Note |
| :--- | :--- | :--- | :--- |
| `add_song` | $O(1)$ | $O(1)$ | Appending to a list. |
| `remove_song` | $O(N)$ | $O(1)$ | Must iterate to find the song ID. |
| `search_song` | $O(N)$ | $O(K)$ | $N$ is total songs, $K$ is matches found. |
| `next/previous` | $O(1)$ | $O(1)$ | Simple index manipulation. |
| `shuffle` | $O(1)$ | $O(1)$ | Random index selection is constant time. |

---

## 6. Real-World Applications

This LLD pattern is fundamental to almost all media consumption software:
1. **Music Streaming (Spotify, Apple Music)**: The core logic of queues, shuffle, and repeat is exactly as modeled here.
2. **Video Platforms (YouTube Playlists)**: YouTube uses a similar "Queue" system where a user can add videos to a temporary playlist and toggle "Loop" or "Shuffle."
3. **Podcast Apps**: Managing episodes within a series follows the `Playlist` $\rightarrow$ `Song` (Episode) relationship.
4. **Slideshow Software**: Image viewers that cycle through a folder of photos utilize the same sequential/shuffle playback logic.