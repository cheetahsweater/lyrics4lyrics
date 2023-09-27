import os
from bs4 import BeautifulSoup
import requests
import time
import re
import tkinter as tk #Hold up...let her cook

path = os.getcwd()
lyricgrabbing = True

#Grabs information from random person generator and outputs to filetype of choice
def lyricsGet(max_retries, retry_wait_time, artist, song): #Wait time is in seconds, "role" is type of person being generated, e.g. "employee", "customer"
    artist = re.sub(r'[^a-zA-Z0-9\s-]', '', artist).strip(" ").lower()
    urlArtist = artist.replace(" ", "-")
    song = re.sub(r'[^a-zA-Z0-9\s-]', '', song).strip(" ").lower()
    urlSong = song.replace(" ", "-")
    for attempt in range(max_retries):
        try:
            url = f'https://www.genius.com/{urlArtist}-{urlSong}-lyrics'
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
    lyricsContainer = soup.select("div[class^=Lyrics__Container]")
    lyrics = ""
    for word in lyricsContainer:
        lyrics += "\n".join(word.strings)
    return(lyrics)
    
while lyricgrabbing == True:
    yesOrNo = input("Grab lyrics (grab) or exit (exit)? ")
    if yesOrNo.casefold() == "exit":
        input("Goodbye! (press enter)")
        exit()
    else:
        artist = input("Artist name (please spell it right)? ")
        song = input("Song name (please also spell this right)? ")
        lyrics = lyricsGet(10, 10, artist, song)

        with open(f"{path}\\{artist} - {song}.txt", "w", encoding="utf-8") as file:
            file.write(lyrics)
            file.close()