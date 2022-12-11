import tkinter as tk
import tkinter.font as font
import tkinter.filedialog as fd
from tkinter import * 
from tkinter.ttk import *
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import urllib.request
import re
import os
import yt_dlp
from mutagen.mp4 import MP4, MP4Cover
from pydub import AudioSegment, effects
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
from lyricsgenius import Genius

import os



scope = "user-library-read"

load_dotenv()
spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
  scope=scope,
  # client_id=os.getenv('SPOTIPY_CLIENT_ID'),
    client_id='19d6a0a29a1b47ee801ed0c10493b11d',
  # client_secret=os.getenv('SPOTIPY_CLIENT_SECRET'),
    client_secret='a8203a38ec7b4f9a8b910c29af68f944',
  redirect_uri='http://127.0.0.1:9090',
  open_browser=True
  ))




punc = '''!:()[]?{};'"<>.@#$%^*_~'''



class Song:
  title = ""

  artist = ""
  artists = []

  album_title = ""
  album_artist = ""
  track_number = ""
  disc_number = ""
  album_total_tracks = ""

  release_date = ""
  release_year = ""

  genre = ""
  genres = []

  explicit = False

  spotify_url = ""
  youtube_url = ""

  image_urls = []
  cover_art = ""

  lyrics = ""

  fileDirectory = ""


  def __init__(self, URL):
    """Initialize a song object with a Spotify URL"""
    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
      scope=scope,
      # client_id='19d6a0a29a1b47ee801ed0c10493b11d',
      client_id=os.getenv('SPOTIPY_CLIENT_ID'),
      # client_secret='a8203a38ec7b4f9a8b910c29af68f944',
      client_secret=os.getenv('SPOTIPY_CLIENT_SECRET'),
      redirect_uri='http://127.0.0.1:9090',
      open_browser=True
    ))


    song = spotify.track(URL)

    self.spotify_url = URL

    for artist in song['artists']:
      if len(song['artists']) > 1:
        if artist == song['artists'][-1]:
          self.artist += artist['name']
        else:
          self.artist += artist['name'] + ", "
        self.artists.append(artist['name'])
      else:
        self.artist += artist['name']
        self.artists.append(artist['name'])

    self.title = song['name']
    print( ("Track Name: " + self.title).encode(errors='ignore').decode() )

    albumName = song['album']['name']
    self.album_title = albumName
    print(("Album: " + self.album_title).encode(errors='ignore').decode())

    self.track_number = str(song['track_number'])
    print("Track Number: " + self.track_number)

    self.disc_number = str(song['disc_number'])
    print("Disc Number: " + self.disc_number)

    self.album_total_tracks = str(song['album']['total_tracks'])
    print("Total Tracks: " + self.album_total_tracks)

    album_artists = ""
    for artist in song['album']['artists']:
      if len(song['album']['artists']) > 1:
        if artist == song['album']['artists'][-1]:
          self.album_artist += artist['name']
        else:
          self.album_artist += artist['name'] + ", "
      else:
          self.album_artist += artist['name']
   
    print(("Album Artists: " + str(self.album_artist)).encode(errors='ignore').decode())

    self.release_date = str(song['album']['release_date'])
    self.release_year = self.release_date[:4]
    print("Release Date: " + self.release_date)

    for genre in spotify.artist(song['artists'][0]['external_urls']['spotify'])['genres']:
      self.genres.append(genre.title())
      
    if len(self.genres) >= 1:
      self.genre = self.genres[0]
    else:
      self.genre = "None"
    print("Song Genres: " + str(self.genre))

    self.explicit = song['explicit']

    
    self.image_urls = song['album']['images']

    for url in self.image_urls:
      if url['height'] == 640:
        self.cover_art = url['url']
        break
      elif url['height'] == 300:
        self.cover_art = url['url']
        break
      elif url['height'] == 64:
        self.cover_art = url['url']
        break

    self.lyrics = self.getLyrics()
    print(self.lyrics)

    print("Cover Art: " + self.cover_art)
    print("Metadata Retrieval Complete.")
    print("\n")


  def autoDownload(self, directory):
    """Automatically download the song from YouTube"""
    if self.explicit:
      youtubeSearch = f"{self.title} {self.artist} uncensored"
      print (f"Youtube Search: {youtubeSearch}")
    else:
      youtubeSearch = f"{self.title} {self.artist} audio"
      print (f"Youtube Search: {youtubeSearch}")

    ytSearch = urllib.parse.quote(str(youtubeSearch))

    print ("URL Query: " + "https://www.youtube.com/results?search_query=" + ytSearch)

    try: 
      ytSearchURL = urllib.request.urlopen(("https://www.youtube.com/results?search_query=" + ytSearch))
    except UnicodeEncodeError:
      ytSearchURL = urllib.request.urlopen(("https://www.youtube.com/results?search_query=" + self.title))


    video_ids = re.findall(r"watch\?v=(\S{11})", ytSearchURL.read().decode())
    youtubeURL: str = ("https://www.youtube.com/watch?v=" + video_ids[0])
    self.youtube_url = youtubeURL
    print("Video URL: " + youtubeURL)

    fileName = (f"{directory}{self.artist} - {self.title}").encode(errors='ignore').decode()
    fileName = fileName.replace("#", "")

    # Removing punctuations in string
    for letter in fileName:
      if letter in punc:
        fileName = fileName.replace(letter, "")

    ydl = yt_dlp.YoutubeDL({
        'format': 'bestaudio[ext=m4a]',
        'outtmpl': f"{fileName}.m4a",
        'forceid': 'ytlink',
        'merge_output_format': 'm4a',
    })

    with ydl:
      ydl.download([youtubeURL])

    downloaded_fileName = fileName.encode('utf-8').decode() + ".m4a"
    print("Downloaded: " + downloaded_fileName)

    self.fileDirectory = downloaded_fileName  
    print("Download Complete.")
    print("\n")

  def saveMetaData(self):
    """Save the metadata to the song file"""

    songObject = MP4(self.fileDirectory)
    songObject['©nam'] = self.title
    songObject['\xa9day'] = self.release_year
    songObject['aART'] = self.album_artist
    songObject['©gen'] = self.genre
    songObject['©ART'] = self.artist
    songObject['©alb'] = self.album_title
    songObject['trkn'] = [(int(self.track_number), int(self.album_total_tracks))]
    songObject['disk'] = [(int(self.disc_number), int(self.disc_number))]
    songObject['©lyr'] = self.lyrics

    urllib.request.urlretrieve(self.cover_art , "cover_art.jpg")

    with open("cover_art.jpg", "rb") as cover:
      songObject["covr"] = [
          MP4Cover(cover.read(), imageformat=MP4Cover.FORMAT_JPEG)
      ]

    songObject.save()

    os.remove("cover_art.jpg")
    print("Metadata Saved.")
    print("\n")

  def audioProcessing(self):
    """Process the audio file"""

    """
    print("Normalizing Audio...")
    songObject = AudioSegment.from_file(f"{fileName}.m4a", "m4a")
    normalized_sound = effects.normalize(songObject)
    if (crossfade):
      normalized_sound = normalized_sound.fade_in(5000).fade_out(5000)
    normalized_sound.export(f"{fileName}.m4a", format="mp4")
    print("Audio Normalization Complete.")
    """

  def getLyrics(self) -> str:
    """Get the lyrics from Genius"""
    genius = Genius('0TLMfeIdmKDR84fOWWBmxH5LGDLrFii_Hqzf9masPnV4fd5MEyKL8qQnBj9BXxDU')
    try:
      lyrics = genius.search_song(self.title, self.artist)
      lyrics = lyrics.lyrics
      return lyrics
    except:
      return "None"

APP_TITLE: str = "Slifer"
BLACK: str = "#191414"
GREEN: str = "#1DB954"
DOWNLOAD_OPTIONS = ["Song", "Album",  "Artist", "Playlist"]


root = tk.Tk()
root.title(APP_TITLE)
root.geometry("1920x1080")
root.configure(bg=GREEN)

MAIN_MENU_FONT = font.Font(family='Broadway', size=100, underline=1)
SUBTITLE_FONT = font.Font(family='Broadway', size=25)
STATUS_FONT = font.Font(family='Broadway', size=70)
LARGE_BUTTON_FONT = font.Font(family='Broadway', size=50)

DOWNLOAD_IMAGE = PhotoImage(file = "buttons/Download-Button.png")
SETTINGS_IMAGE = PhotoImage(file = "buttons/Settings-Button.png")
RETURN_IMAGE = PhotoImage(file = "buttons/Return-Button.png")
CHOOSE_DIRECTORY_IMAGE = PhotoImage(file = "buttons/ChooseDirectory-Button.png")
DOWNLOAD_SQUARED_IMAGE = PhotoImage(file = "buttons/DownloadSquared-Button.png")

def main_page() -> None:
    global root

    global main_title
    main_title = tk.Label(
        root,
        text = APP_TITLE,
        foreground=BLACK,
        background=GREEN,
        font=MAIN_MENU_FONT
    )

    global sub_title
    sub_title = tk.Label(
        root,
        text = "An application designed for converting your favorite spotify music to an easily accessible, local format.",
        foreground=BLACK,
        background=GREEN,
        font=SUBTITLE_FONT
    )
    global download_button
    download_button = tk.Button(
        root,
        text = "Download",
        font = SUBTITLE_FONT,
        bg = "#63666A",
        fg = "black",
        command = main_to_download,
        image=DOWNLOAD_IMAGE
    )

    global settings_button
    settings_button = tk.Button(
        root,
        text = "Settings",
        font = SUBTITLE_FONT,
        bg = "#63666A",
        fg = "black",
        command = main_to_settings,
        image=SETTINGS_IMAGE
    )

    global spacer0
    spacer0 = tk.Label(root, "", height=5, bg=GREEN)

    global spacer1
    spacer1 = tk.Label(root, "", height=10, bg=GREEN)

    global spacer2
    spacer2 = tk.Label(root, "", height=10, bg=GREEN)

    global spacer3
    spacer3 = tk.Label(root, "", height=2, bg=GREEN)

    main_title.pack()
    spacer0.pack()
    sub_title.pack()
    spacer1.pack()
    download_button.pack()
    spacer3.pack()
    settings_button.pack()
    spacer2.pack()

def remove_main_page() -> None:
    main_title.pack_forget()
    spacer0.pack_forget()
    sub_title.pack_forget()
    spacer1.pack_forget()
    download_button.pack_forget()
    settings_button.pack_forget()
    spacer2.pack_forget()
    spacer3.pack_forget()
    
def download_page() -> None:
    global root


    global selected_download_option
    selected_download_option = tk.StringVar(root)
    selected_download_option.set("Song")

    global selected_file_directory
    selected_file_directory = tk.StringVar(root)
    selected_file_directory.set("~")

    global selected_url
    selected_url = tk.StringVar(root)
    selected_url.set("")

    global download_status
    download_status = tk.StringVar(root)
    download_status.set("Status: Idle")


    
    global download_main_title
    download_main_title = tk.Label(
        root,
        text = "Download",
        foreground=BLACK,
        background=GREEN,
        font=MAIN_MENU_FONT
    )
    download_main_title.pack()

    global download_spacer
    download_spacer = tk.Label(root, "", height=2, bg=GREEN)
    download_spacer.pack()

    global download_url_entry
    global download_url_label

    download_url_label = tk.Label(
        root,
        text="Enter URL:",
        # width=50,
        font=SUBTITLE_FONT,
        background=GREEN,
        fg=BLACK
    )
    download_url_label.pack()

    download_url_entry = tk.Entry(
        root,
        textvariable=selected_url,
        width=44,
        font=SUBTITLE_FONT,
        bg=BLACK,
        fg=GREEN,
    )
    download_url_entry.pack()

    global download_spacer2
    download_spacer2 = tk.Label(root, "", height=2, bg=GREEN)
    download_spacer2.pack()

    global download_directory_label
    download_directory_label = tk.Label(
        root,
        text="Directory:",
        width=51,
        font=SUBTITLE_FONT,
        background=GREEN,
        fg=BLACK
    )
    download_directory_label.pack()

    global download_directory_button
    download_directory_button = tk.Button(
        root,
        text = "Choose Directory",
        font = SUBTITLE_FONT,
        bg = BLACK,
        image=CHOOSE_DIRECTORY_IMAGE,
        command = lambda: selected_file_directory.set(f"{fd.askdirectory()}/")
    )
    download_directory_button.pack() 

    global download_directory_entry
    download_directory_entry = tk.Entry(
        root,
        textvariable = selected_file_directory,
        width=44,
        font = SUBTITLE_FONT,
        bg=BLACK,
        fg=GREEN
    )
    download_directory_entry.pack()

    global download_spacer3
    download_spacer3 = tk.Label(root, "", height=2, bg=GREEN)
    download_spacer3.pack()

    global download_button
    download_button = tk.Button(
        root,
        text = "Download",
        font = SUBTITLE_FONT,
        bg = BLACK,
        # height = 10,
        image=DOWNLOAD_SQUARED_IMAGE, 
        # command= lambda: print(selected_download_option.get())
        command = lambda: download_process()
    )
    download_button.pack() 

    global download_spacer4
    download_spacer4 = tk.Label(root, "", height=2, bg=GREEN)
    download_spacer4.pack()

    global download_status_label
    download_status_label = tk.Label(
        root,
        textvariable = download_status,
        foreground=BLACK,
        background=GREEN,
        font=STATUS_FONT
    )
    download_status_label.pack()

    global return_to_main_button
    return_to_main_button = tk.Button(
        root, 
        text = "Return",
        font = SUBTITLE_FONT,
        background = BLACK,
        # width = 19,
        image=RETURN_IMAGE,
        # height=60,
        command = lambda: download_to_main()
    )
    return_to_main_button.pack()

def remove_download_page() -> None:
    download_main_title.pack_forget()
    download_url_entry.pack_forget()
    download_url_label.pack_forget()
    download_directory_entry.pack_forget()
    download_directory_button.pack_forget()
    download_button.pack_forget()
    download_status_label.pack_forget()
    return_to_main_button.pack_forget()
    download_spacer.pack_forget()
    download_spacer2.pack_forget()
    download_directory_label.pack_forget()
    download_spacer3.pack_forget()
    download_spacer4.pack_forget()

def settings_page() -> None:
    global root

    global settings_main_title
    settings_main_title = tk.Label(
        root,
        text = "Settings",
        foreground=BLACK,
        background=GREEN,
        font=MAIN_MENU_FONT
    )
    settings_main_title.pack()

    global return_to_main_button
    return_to_main_button = tk.Button(
        root, 
        text = "Return to Main Menu",
        font = SUBTITLE_FONT,
        bg = BLACK,
        width = 25,
        command = lambda: settings_to_main()
    )
    return_to_main_button.pack()

def remove_settings_page() -> None:
    settings_main_title.pack_forget()
    return_to_main_button.pack_forget()

def main_to_download() -> None:
  remove_main_page()
  download_page()

def download_to_main() -> None:
  remove_download_page()
  main_page()

def main_to_settings() -> None:
  remove_main_page()
  settings_page()

def settings_to_main() -> None:
  remove_settings_page()
  main_page()

def download_song(URL: str):
  
  download_status.set("Status: Retrieving Song Data...")
  newSong: Song = Song(URL)

  download_status.set("Status: Downloading Song...")
  newSong.autoDownload(selected_file_directory.get())

  download_status.set("Status: Updating Downloaded File with Saved Data...")
  newSong.saveMetaData()

def download_album(URL: str):
  spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
    scope=scope,
    client_id='19d6a0a29a1b47ee801ed0c10493b11d',
    client_secret='a8203a38ec7b4f9a8b910c29af68f944',
    redirect_uri='http://127.0.0.1:9090',
    open_browser=True
  ))
    
  album_object = spotify.album(URL)
 

  album_urls = album_object['tracks']['items']

  download_status.set("Downloading...")
  for url in album_urls:
    download_song(url['external_urls']['spotify'])
    download_status.set("Downloading Album...")
    root.update()
  download_status.set("Download Complete!")

def download_artist(URL: str):
  spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
    scope=scope,
    client_id='19d6a0a29a1b47ee801ed0c10493b11d',
    client_secret='a8203a38ec7b4f9a8b910c29af68f944',
    redirect_uri='http://127.0.0.1:9090',
    open_browser=True
  ))
  artistAlbums = spotify.artist_albums(URL, album_type='album')['items']


  download_status.set("Downloading...")
  for album in artistAlbums:
    download_album(album['external_urls']['spotify'])
    download_status.set("Downloading Artist\'s Songs...")
    root.update()
  download_status.set("Download Complete!")

def download_playlist(URL: str):
  spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
    scope=scope,
    client_id='19d6a0a29a1b47ee801ed0c10493b11d',
    client_secret='a8203a38ec7b4f9a8b910c29af68f944',
    redirect_uri='http://127.0.0.1:9090',
    open_browser=True
  ))

  playlistTracks = spotify.playlist(URL)['tracks']

  playlistSongs = playlistTracks['items']

  while playlistTracks['next']:
    playlistTracks = spotify.next(playlistTracks)
    playlistSongs.extend(playlistTracks['items'])
  download_status.set("Downloading...")
  for song in playlistSongs:
    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
      scope=scope,
      client_id='19d6a0a29a1b47ee801ed0c10493b11d',
      client_secret='34d4b0b1acef4324a22656c49a98dfe9',
      redirect_uri='http://127.0.0.1:9090',
      open_browser=True
    ))
    download_song(song['track']['external_urls']['spotify'])
    download_status.set("Downloading Playlist Songs...")
    root.update()
  download_status.set("Download Complete!")
  
def download_process() -> None:

  if ('track' in selected_url.get()):
    download_status.set("Downloading...")
    download_song(selected_url.get())
    download_status.set("Status: Download Complete!")
  
  elif ('album' in selected_url.get()):
    download_status.set("Downloading...")
    download_album(selected_url.get())
      
  elif ('artist' in selected_url.get()):  
    download_status.set("Downloading...")
    download_artist(selected_url.get())
    
  elif ('playlist' in selected_url.get()):
    download_status.set("Downloading...")
    download_playlist(selected_url.get())

  else: 
    download_status.set("Error: Invalid URL")


main_page()
root.mainloop()
