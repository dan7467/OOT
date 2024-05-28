import tkinter as tk
from tkinter.messagebox import showinfo

import numpy as np
from PIL import Image, ImageTk

from compare import ComparedSongs, dtwElementInfo
from frontend.SongComponent import SongComponent
from frontend.VirtualPiano import VirtualPiano
from frontend.OutOfTune import OutOfTune
from filesAccess import *


class MainContent(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#121212")
        self.oot = None
        self.dbAccess = DBAccess("Roni")
        self.create_main_content()
        self.comparedSongsObject = None

    def create_main_content(self):
        songsDict = printAvailableSongs(self.dbAccess)
        songsList = list(songsDict.values())
        self.songs = [{"img": "./images/example.png", "title": str(i), "artist": "Artist 1"} for i in songsList]
        # self.songs = [
        #     {"img": "./images/example.png", "title": "Song 1", "artist": "Artist 1"},
        #     {"img": "./images/example.png", "title": "Song 2", "artist": "Artist 2"},
        #     {"img": "./images/example.png", "title": "Song 3", "artist": "Artist 3"},
        #     {"img": "./images/example.png", "title": "Song 4", "artist": "Artist 4"},
        #     {"img": "./images/example.png", "title": "Song 5", "artist": "Artist 5"},
        #     {"img": "./images/example.png", "title": "Song 6", "artist": "Artist 6"},
        # ]
        self.refresh_content()

    def refresh_content(self):
        for widget in self.winfo_children():
            widget.destroy()
        columns_per_row = 3  # Number of columns per row
        for idx, song in enumerate(self.songs):
            row = idx // columns_per_row
            column = idx % columns_per_row
            song_component = SongComponent(self, song)
            song_component.grid(row=row, column=column, pady=20, padx=20, sticky="n")

    def display_play_page(self, song):
        for widget in self.winfo_children():
            widget.destroy()

        play_frame = tk.Frame(self, bg="#121212")
        play_frame.pack(expand=True, fill="both")

        try:
            img = Image.open(song["img"])
            img = img.resize((200, 200), Image.LANCZOS)
            img = ImageTk.PhotoImage(img)
        except FileNotFoundError:
            showinfo("Error", f"Image file '{song['img']}' not found.")
            return
        except Exception as e:
            showinfo("Error", f"Unable to open image: {e}")
            return

        img_label = tk.Label(play_frame, image=img, bg="#121212")
        img_label.image = img  # Keep a reference to avoid garbage collection
        img_label.pack(pady=20)

        song_title = tk.Label(play_frame, text=song["title"], fg="white", bg="#121212", font=("Helvetica", 24))
        song_title.pack(pady=10)

        song_artist = tk.Label(play_frame, text=song["artist"], fg="gray", bg="#121212", font=("Helvetica", 18))
        song_artist.pack(pady=5)

        play_button = tk.Button(play_frame, text="Play", command=lambda: self.startMic(song["title"]), bg="#1DB954", fg="white", font=("Helvetica", 14))
        play_button.pack(pady=20)

        history_button = tk.Button(play_frame, text="History", command=lambda: self.showHistoryOfSong(song["title"]), bg="#1DB954", fg="white", font=("Helvetica", 14))
        history_button.pack(pady=20)

    def startMic(self, songName):
        self.oot = OutOfTune()
        self.oot.read_from_mic(songName)
        print(self.getGrade())

        #self.printGraph()


    def getGrade(self):
        if self.comparedSongsObject is None:
            return 0
        return self.comparedSongsObject.score


    def printGraph(self):
        self.comparedSongsObject.showBarGraph()
        self.comparedSongsObject.hearClips()


    def showHistoryOfSong(self, songName):
        #get grades of older song, and choose one of them
        songNameWithoutUserName = songName.split('_')[0]
        result = self.dbAccess.fetchPerformancesFromUser(songNameWithoutUserName)

        resultDict = {}
        for num, performance in enumerate(result):
            resultDict[num] = performance
            print(f'{num}){songName}, Score: {performance["score"]}')

        #performanceChosenIndex = int(input("\nSelect specific Performance: "))

        performanceChosenIndex = 0  #In here we will put the index of the performance we chose
        self.compareOldSongsInFront(songNameWithoutUserName, resultDict[performanceChosenIndex])

        self.printGraph()
        self.oot.hearClips()
        pass



    def display_virtual_piano(self):
        for widget in self.winfo_children():
            widget.destroy()

        piano = VirtualPiano(self, width=1600, height=800)  # Adjust width here
        piano.pack(fill=tk.BOTH, expand=True)
        return piano


    def compareOldSongsInFront(self, archivedName, performanceObject):
        performanceId = performanceObject["_id"]
        performanceSongName = performanceObject["song_name"] + performanceId
        songData = getDataFromFile(archivedName)

        origFreqsAndSeconds = songData.notesDict
        dtw_path_str = performanceObject["dtw_lst"]
        dtw_path = [(int(x[0]), int(x[1])) for x in dtw_path_str]
        performanceFreqsAndSeconds = performanceObject["performance_notes_dict"]

        y = np.array([float(x) for x in performanceFreqsAndSeconds.values()])
        yTime = [float(x) for x in performanceFreqsAndSeconds.keys()]
        x = np.array([x for x in origFreqsAndSeconds.values()])
        xTime = [x for x in origFreqsAndSeconds.keys()]


        infoDict = {}
        for xIdx, yIdx in dtw_path:
            infoDict[(xIdx, yIdx)] = dtwElementInfo(x[xIdx], y[yIdx], xIdx, yIdx, xTime[xIdx], yTime[yIdx])

        self.comparedSongsObject = ComparedSongs(archivedName, performanceSongName, performanceObject["score"], infoDict, x, y, dtw_path)