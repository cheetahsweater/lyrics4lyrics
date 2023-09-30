import os
from bs4 import BeautifulSoup
import requests
import time
import re
import json
import unidecode
import tkinter as tk #Hold up...let her cook

path = os.getcwd()

#Load config file and cast it to a dictionary so it can be referenced later
with open(f"{path}\\config.json", "r", encoding="utf-8") as file:
    config = file.read()
    essential = json.loads(config)
    print(essential) #DEBUG
    file.close()

#Checks whether the "output" folder exists in program folder and creates it if not
if essential["defaultOutputExists"] == "False":
    os.mkdir(f"{path}\\output")
    essential.update({"defaultOutputExists":"True"})
else:
    pass

#Turning on while loop variavkr 
lyricgrabbing = True
#Writes config back to config file (to signal that output folder is created) 
with open(f"{path}\\config.json", "w", encoding="utf-8") as file:
    config = json.dumps(essential)
    file.write(config)
    file.close()

#Formats artist, album, or song title to fit Genius URL format
#Note for Lillith: THIS is where we will be fixing the apostrophe issue
def urlFormat(string, stringType): #type parameters are "artist", "album", "song"
    string = string.replace("/", " ") #Gets rid of slashed, replaces with spaces
    #Artist-specific formatting
    if stringType == "artist":
        pass #Placeholder; erase this when adding formatting changes
    
    #Universal formatting
    string = re.sub(r'[^a-zA-Z0-9\s-]', '', string).strip(" ").lower() #Removes all non-alphanumeric characters besides "-"
    urlString = string.replace(" ", "-") #Replaces all spaces with hyphens
    return urlString

#Gets rid of characters that aren't filename-compatible
def sanitize(filename):
    newFilename = re.sub(r'[\\/*?:"<>|]',"", filename)
    return newFilename

#Actual lyric grabber function
def lyricsGet(max_retries, retry_wait_time, artist, song, link=None): #Wait time is in seconds
    #Removes feature credit if present
    if "(Ft." in song:
        feat = "(Ft."
        song = song.split(feat)[0]
        print(song) #DEBUG
    #Formats artist and song names to fit URL
    urlArtist = urlFormat(artist, "artist")
    urlSong = urlFormat(song, "song")
    #Try to grab HTML from lyrics page
    for attempt in range(max_retries):
        try:
            if link == None:
                url = f'https://www.genius.com/{urlArtist}-{urlSong}-lyrics'
            else:
                url = link
            print(url)
            response = requests.get(url)
            break
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                print(f"Request failed with error: {e}. Retrying in {retry_wait_time} seconds...")
                time.sleep(retry_wait_time)
            else:
                print(f"Request failed after {max_retries} attempts. Skipping word...")
                return []
    soup = BeautifulSoup(response.content, 'html.parser')
    #Extracts "lyric container" dividers from website
    lyricsContainer = soup.select("div[class^=Lyrics__Container]")
    lyrics = ""
    #Joins lyric container dividers together and separates them by newlines
    for word in lyricsContainer:
        lyrics += "\n".join(word.strings)
    return lyrics

#Function to grab albums
def albumGrab(max_retries, retry_wait_time, artist, album):
    urlArtist = urlFormat(artist, "artist")
    urlAlbum = urlFormat(album, "album")
    for attempt in range(max_retries):
        try:
            url = f'https://www.genius.com/albums/{urlArtist}/{urlAlbum}'
            response = requests.get(url)
            break
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                print(f"Request failed with error: {e}. Retrying in {retry_wait_time} seconds...")
                time.sleep(retry_wait_time)
            else:
                print(f"Request failed after {max_retries} attempts. Skipping word...")
                return []
    soup = BeautifulSoup(response.content, 'html.parser')
    tracklistRows = soup.select("h3.chart_row-content-title", recursive=False)
    trackLinks = soup.select("a.u-display_block", recursive=False)
    tracklist = dict()
    trackNum = 0
    for track in tracklistRows:
        # Extract the direct text within the <h3> element
        justTrack = ''.join(track.find_all(text=True, recursive=False)).strip()
        link = trackLinks[trackNum].get("href")
        tracklist.update({justTrack:link})
        trackNum += 1
    return tracklist

while lyricgrabbing == True:
    yesOrNo = input("Grab album (album) or song (song)? Say \"exit\" to exit. ")
    if yesOrNo.casefold() == "exit":
        exit()
    elif yesOrNo.casefold() == "song":
        artist = input("Artist name (please spell it right)? ")
        song = input("Song name (please also spell this right)? ")
        lyrics = lyricsGet(10, 10, artist, song)
        artistFile = sanitize(artist)
        songFile = sanitize(song)
        with open(f"{path}\\output\\{artistFile} - {songFile}.txt", "w", encoding="utf-8") as file:
            file.write(lyrics)
            file.close()
    elif yesOrNo.casefold() == "album":
        artist = input("Artist name (please spell it right)? ")
        album = input("Album name (please also spell this right)? ")
        artistFile = sanitize(artist)
        albumFile = sanitize(album)
        albumSongs = albumGrab(10, 10, artist, album)
        try:
            os.mkdir(f"{path}\\output\\{artistFile} - {albumFile}")
        except FileExistsError:
            pass
        for song, link in albumSongs.items():
            lyrics = lyricsGet(10, 10, artist, song, link)
            songFile = sanitize(song)
            with open(f"{path}\\output\\{artistFile} - {albumFile}\\{artistFile} - {songFile}.txt", "w", encoding="utf-8") as file:
                file.write(lyrics)
                file.close()