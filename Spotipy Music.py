from audioop import cross
from dis import code_info
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import urllib.request
import re
import os
import io
import yt_dlp
from mutagen.mp4 import MP4, MP4Cover
from pydub import AudioSegment, effects
from tinytag import TinyTag
import asyncio

punc = '''!/:()[]?{};'"<>.@#$%^*_~'''

def syncAmplitude(sound, target_dBFS):
  delta_dBFS = target_dBFS - sound.dBFS
  return sound.apply_gain(delta_dBFS)

#songObject = AudioSegment.from_file(f"/music/Coda -}.m4a", "m4a")
#print(songObject.dBFS)

def trackReplacement(title: str, artist: str, link: str, crossfade: bool):

  fileDirectory = os.listdir()

  foundFile = False

  print("Locating File In Directory...")
  for file in fileDirectory :
    if (file[-4:] == ".m4a" and str(TinyTag.get(file).title).lower() == title.lower() and str(TinyTag.get(file).artist).lower() == artist.lower()):
      foundFile = True

      print("File Found")
      # Removing punctuations in string
      for letter in file:
        if letter in punc:
          fileName = file.replace(letter, "")

      ydl = yt_dlp.YoutubeDL({
          'format': 'bestaudio[ext=m4a]',
          'outtmpl': f"(new) {file}",
          'forceid': 'ytlink',
          'merge_output_format': 'm4a',
      })

      print("Downloading YouTube Video...")

      with ydl:
          ydl.download([link])

      print("Normalizing Audio...")
      songObject = AudioSegment.from_file(f"(new) {file}", "m4a")
      normalized_sound = effects.normalize(songObject)
      if (crossfade):
        normalized_sound = normalized_sound.fade_in(5000).fade_out(5000)
      normalized_sound.export(f"(new) {file}", format="mp4")
      print("Audio Normalization Complete.")


      #Save Song Metadata

      print("Adding Tags To New File...")
      songObject = MP4(f"(new) {file}")
      songObject['©nam'] = TinyTag.get(file).title
      songObject['\xa9day'] = TinyTag.get(file).year
      songObject['aART'] = TinyTag.get(file).albumartist
      songObject['©gen'] = MP4(file)['©gen']
      songObject['©ART'] = TinyTag.get(file).artist
      songObject['©alb'] = TinyTag.get(file).album
      trackNumber = str(TinyTag.get(file).track)
      trackTotal = str(TinyTag.get(file).track_total)
      songObject['trkn'] = [(int(trackNumber), int(trackTotal))]
      discNumber = str(TinyTag.get(file).disc)
      discTotal = str(TinyTag.get(file).disc_total)
      songObject['disk'] = [(int(discNumber), int(discTotal))]

      songObject["covr"] = MP4(file)['covr']

      songObject.save()

      print("Deleting Old File...")
      os.remove(file)
      print("Renaming New File...")
      os.rename(f"(new) {file}", file)
      print(f"Track Replacement Complete. New File: {file}")

"""Store URL for desired Spotify Playlist, and establish connection to Spotify API

"""

#playlist_url = 'https://open.spotify.com/playlist/3a03HaZt8Nz9S8YBPcYtMS?si=gbIndx5HTsiLVmGdbyb9Yg'

"""Store all songs within the given spotify playlist

Iterate through all the songs in the playlist, starting from the given index

Establish values for song Artist(s)
"""

def songToM4A(song_url: str, crossfade: bool = False, directory: str = ""):
  try:
    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials('19d6a0a29a1b47ee801ed0c10493b11d', '34d4b0b1acef4324a22656c49a98dfe9'), requests_timeout=10, retries=10)

    song = spotify.track(song_url)
    song_artists = ""
    for artist in song['artists']:
        if len(song['artists']) > 1:
            if artist == song['artists'][-1]:
              song_artists += artist['name']
            else:
              song_artists += artist['name'] + ", "
        else:
            song_artists += artist['name']
    print("Artists: " + str(song_artists))


    songName = song['name']
    print( ("Track Name: " + songName).encode(errors='ignore').decode() )


    albumName = song['album']['name']
    print(("Album: " + albumName).encode(errors='ignore').decode())


    trackNumber = str(song['track_number'])
    print("Track Number: " + trackNumber)


    discNumber = str(song['disc_number'])
    print("Disc Number: " + discNumber)


    totalTracks = str(song['album']['total_tracks'])
    print("Total Tracks: " + totalTracks)


    album_artists = ""
    for artist in song['album']['artists']:
        if len(song['album']['artists']) > 1:
            if artist == song['album']['artists'][-1]:
              album_artists += artist['name']
            else:
              album_artists += artist['name'] + ", "
        else:
            album_artists += artist['name']
    print(("Album Artists: " + str(album_artists)).encode(errors='ignore').decode())


    releaseDate = str(song['album']['release_date'])
    print("Release Date: " + releaseDate)

    if (len(spotify.artist(song['artists'][0]['external_urls']['spotify'])['genres']) > 0):
      songGenres = spotify.artist(song['artists'][0]['external_urls']['spotify'])['genres'][0].title()
    else:
      songGenres = "None"

    """
    for genre in spotify.artist(song['artists'][0]['external_urls']['spotify'])['genres']:
        if len(spotify.artist(song['artists'][0]['external_urls']['spotify'])['genres']) > 1:
            if genre == (spotify.artist(song['artists'][0]['external_urls']['spotify'])['genres'][-1]):
              songGenres += genre
            else:
              songGenres += genre + ", "
        else:
            songGenres += genre
    """

    print("Song Genres: " + str(songGenres))

    isExplicit = song['explicit']

    coverArtURL = song['album']['images'][-1]['url']
    print (song['album']['images'])

    print("Cover Art: " + coverArtURL)



    if isExplicit:
      ytSearch = songName + " " + song_artists + ' uncensored'
      print (ytSearch)
    else:
      ytSearch = songName + " " + song_artists + ' music'

    ytSearch = urllib.parse.quote(ytSearch)

    print ("Query: " + "https://www.youtube.com/results?search_query=" + ytSearch)

    try:
        ytSearchURL = urllib.request.urlopen(("https://www.youtube.com/results?search_query=" + ytSearch))
    except UnicodeEncodeError:
        ytSearchURL = urllib.request.urlopen(("https://www.youtube.com/results?search_query=" + songName))


    video_ids = re.findall(r"watch\?v=(\S{11})", ytSearchURL.read().decode())
    ytURL = ("https://www.youtube.com/watch?v=" + video_ids[0])
    print("Video URL: " + ytURL)

    fileName = (f"{directory}{song_artists} - {songName}").encode(errors='ignore').decode()
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
        ydl.download([ytURL])

    print("Downloaded: " + (fileName.encode('utf-8').decode() + ".m4a"))

    """
    print("Normalizing Audio...")
    songObject = AudioSegment.from_file(f"{fileName}.m4a", "m4a")
    normalized_sound = effects.normalize(songObject)
    if (crossfade):
      normalized_sound = normalized_sound.fade_in(5000).fade_out(5000)
    normalized_sound.export(f"{fileName}.m4a", format="mp4")
    print("Audio Normalization Complete.")
    """

    #Save Song Metadata
    songObject = MP4(f"{fileName}.m4a")
    songObject['©nam'] = songName.encode(errors='ignore').decode()
    songObject['\xa9day'] = releaseDate[0:4]
    songObject['aART'] = album_artists.encode(errors='ignore').decode()
    songObject['©gen'] = str(songGenres)
    songObject['©ART'] = song_artists.encode(errors='ignore').decode()
    songObject['©alb'] = albumName.encode(errors='ignore').decode()
    songObject['trkn'] = [(int(trackNumber), int(totalTracks))]
    songObject['disk'] = [(int(discNumber), int(discNumber))]

    urllib.request.urlretrieve(coverArtURL , "cover_art.jpg")

    with open("cover_art.jpg", "rb") as cover:
        songObject["covr"] = [
            MP4Cover(cover.read(), imageformat=MP4Cover.FORMAT_JPEG)
        ]


    songObject.save()


    print(f"Song Download Complete: {fileName}.m4a")
    print('\n')

    #with_style = beginning.append(end, crossfade=1500
  except:
    try:
      return songName
    except:
      return "Null / Unknown"


def albumToM4A(album_url: str, crossfade: bool = False, directory: str = ""):
  spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials('19d6a0a29a1b47ee801ed0c10493b11d', '34d4b0b1acef4324a22656c49a98dfe9'))
  album = spotify.album(album_url)
  albumSongs = album['tracks']['items']

  invalidSongs = {}
  for song in albumSongs:
      spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials('19d6a0a29a1b47ee801ed0c10493b11d', '34d4b0b1acef4324a22656c49a98dfe9'))
      try:
        songToM4A(song['external_urls']['spotify'], crossfade=crossfade, directory=directory)
      except IndexError:
        invalidSongs[song['name']] = "Couldn't Find YouTube Video"
      except yt_dlp.utils.ExtractorError:
        invalidSongs[song['name']] = "This video is restricted by YouTube."

  for item in invalidSongs.keys():
    print(f"{item}: {invalidSongs[item]}")
  print (invalidSongs)

def artistToM4A(artist_url: str, crossfade: bool = False, directory: str = ""):
  spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials('19d6a0a29a1b47ee801ed0c10493b11d', '34d4b0b1acef4324a22656c49a98dfe9'))

  invalidSongs = {}
  artistAlbums = spotify.artist_albums(artist_url, album_type='album')

  albums = artistAlbums['items']

  print(artistAlbums['items'])

  for album in albums:
    albumToM4A(album['external_urls']['spotify'], crossfade=crossfade, directory=directory)



def playlistToM4A(playlist_url: str, startingSong: int = 0, crossfade: bool = False) :
  spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials('19d6a0a29a1b47ee801ed0c10493b11d', '34d4b0b1acef4324a22656c49a98dfe9'))

  invalidSongs = {}
  playlistTracks = spotify.playlist(playlist_url)['tracks']

  playlistSongs = playlistTracks['items']

  while playlistTracks['next']:
      playlistTracks = spotify.next(playlistTracks)
      playlistSongs.extend(playlistTracks['items'])



  for song in playlistSongs[startingSong - 1:] :
    try:
      spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials('19d6a0a29a1b47ee801ed0c10493b11d', '34d4b0b1acef4324a22656c49a98dfe9'))
      returnedSong = songToM4A(song['track']['external_urls']['spotify'], crossfade)
    except Exception as exception:
      invalidSongs[returnedSong] = exception


  for item in invalidSongs.keys():
    print(f"{item}: {invalidSongs[item]}")
  print (invalidSongs)



"""
while (True):
  userChoice = input("Download or Replace [d/r]: ").lower()

  if (userChoice == "d"):
    songInput = input("Spotify Link: ")
    desireToCrossFade = input('Crossfade? [Y/N]: ')
    if desireToCrossFade.upper() == 'Y':
      desireToCrossFade = True
    elif desireToCrossFade.upper() == 'N':
      desireToCrossFade = False
    else:
      desireToCrossFade = True
    songToM4A(songInput, desireToCrossFade)
    print('\n')
  elif (userChoice == "r"):
    songName = input("Song Name: ")
    artistName = input("Artist Name: ")
    replacementLink = input("Replacement Link: ")
    desireToCrossFade = input('Crossfade? [Y/N]: ')
    if desireToCrossFade.upper() == 'Y':
      desireToCrossFade = True
    elif desireToCrossFade.upper() == 'N':
      desireToCrossFade = False
    else:
      desireToCrossFade = True
    trackReplacement(songName, artistName, replacementLink, desireToCrossFade)
    print('\n')
"""



songToM4A("https://open.spotify.com/track/2kS6td1yvmpNgZTt1q5pQq?si=6af05569724e4d05")
# urllib.request.urlretrieve("https://i.scdn.co/image/ab67616d00004851e7c12faa0fad19dbf84c087f", "cover_art.jpg")