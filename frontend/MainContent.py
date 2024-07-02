import tkinter as tk
from tkinter import messagebox
from tkinter.messagebox import showinfo

import numpy as np
from PIL import Image, ImageTk

from compare import ComparedSongs, dtwElementInfo
from frontend.SongComponent import SongComponent
from frontend.SongPerformanceEntry import SongPerformanceEntry
from frontend.VirtualPiano import VirtualPiano
from frontend.OutOfTune import OutOfTune
from filesAccess import *


class MainContent(tk.Frame):
    def __init__(self, parent, userName):
        super().__init__(parent, bg="#EEEEEE")
        self.oot = None
        self.userName = userName
        self.dbAccess = DBAccess(self.userName)
        self.create_main_content()
        self.comparedSongsObject = None


    def create_main_content(self):
        songsDict = printAvailableSongs(self.dbAccess)
        songsList = list(songsDict.values())
        self.songs = [{"img": "./images/images.jpeg", "title": str(i), "artist": "Artist 1"} for i in songsList]
        self.refresh_content()

    def refresh_content(self):
        for widget in self.winfo_children():
            widget.destroy()
        columns_per_row = 6
        for idx, song in enumerate(self.songs):
            row = idx // columns_per_row
            column = idx % columns_per_row
            song_component = SongComponent(self, song)
            song_component.grid(row=row, column=column, pady=20, padx=20, sticky="n")

    # def addSong(self):
    #     for widget in self.winfo_children():
    #         widget.destroy()
    #
    #     self.label = tk.Label(self, text="Enter song name:")
    #     self.label.pack()
    #
    #     self.name_entry = tk.Entry(self, bg="#FFEADD")
    #     self.name_entry.pack()
    #
    #     self.add_button = tk.Button(self, text="Add", command=self.save_song)
    #     self.add_button.pack()
    #
    #     # Display the available songs
    #     available_songs = self.dbAccess.getAvailableWavs()
    #     self.songs_label = tk.Label(self, text="Available Songs:")
    #     self.songs_label.pack()
    #
    #     self.songs_listbox = tk.Listbox(self, bg="#EEEEEE")
    #     for song in available_songs.values():
    #         self.songs_listbox.insert(tk.END, song)
    #     self.songs_listbox.pack()

    def addSong(self):
        available_wavs = self.dbAccess.getAvailableWavsToAdd()
        for widget in self.winfo_children():
            widget.destroy()

        self.label = tk.Label(self, text="Select a song to add:")
        self.label.pack()

        self.song_listbox = tk.Listbox(self)
        for song in available_wavs:
            self.song_listbox.insert(tk.END, song)
        self.song_listbox.pack()

        self.add_button = tk.Button(self, text="Add", command=self.confirm_song)
        self.add_button.pack()

    def confirm_song(self):
        selected_song = self.song_listbox.get(tk.ACTIVE)
        if selected_song:
            if messagebox.askyesno("Confirm Song", f"Are you sure you want to add '{selected_song}'?"):
                self.save_song(selected_song)

    def save_song(self, songName):
        if songName:
            # Save the name to a file or database
            self.oot = OutOfTune(self.userName)
            fileName = songName + '.wav'
            self.oot.getSongData(fileName, False, self.oot)
            #self.dbAccess.addSongForUser(songName)
            self.addSong()

    def display_play_page(self, song):
        for widget in self.winfo_children():
            widget.destroy()

        play_frame = tk.Frame(self, bg="#EEEEEE")
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

        img_label = tk.Label(play_frame, image=img, bg="#EEEEEE")
        img_label.image = img
        img_label.pack(pady=20)

        song_title = tk.Label(play_frame, text=song["title"], fg="#B31312", bg="#EEEEEE", font=("Helvetica", 24))
        song_title.pack(pady=10)

        song_artist = tk.Label(play_frame, text=song["artist"], fg="gray", bg="#EEEEEE", font=("Helvetica", 18))
        song_artist.pack(pady=5)

        play_button = tk.Button(play_frame, text="Play", command=lambda: self.startMic(song["title"]), bg="#EEEEEE",
                                fg="#B31312", font=("Helvetica", 14))
        play_button.pack(pady=20)

        history_button = tk.Button(play_frame, text="History", command=lambda: self.showHistoryOfSong(song["title"]),
                                   bg="#EEEEEE", fg="#B31312", font=("Helvetica", 14))
        history_button.pack(pady=20)

        delete_button = tk.Button(play_frame, text="Delete Song", command=lambda: self.deleteSong(song["title"]),
                                   bg="#EEEEEE", fg="#B31312", font=("Helvetica", 14))
        delete_button.pack(pady=20)

    def startMic(self, songName):
        self.oot = OutOfTune(self.userName)
        self.comparedSongsObject = self.oot.read_from_mic(songName)
        print(self.getGrade())
        self.printGraph()

    def deleteSong(self, songName):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this song?"):
            self.dbAccess.deleteSongAndPerformances(songName)


    def getGrade(self):
        if self.comparedSongsObject is None:
            return 0
        return self.comparedSongsObject.score

    def printGraph(self):
        self.comparedSongsObject.hearClips()
        self.comparedSongsObject.showBarGraph()

    def showHistoryOfSong(self, songName):
        songNameWithoutUserName = songName.split('_')[0]
        result = self.dbAccess.fetchPerformancesFromUser(songNameWithoutUserName)
        print(result)

        history = []
        for num, performance in enumerate(result):
            history.append({
                'number': num + 1,
                'id' : performance['_id'],
                'grade': performance['score'],
                'song_name': performance['song_name']
            })
        print(history)

        self.display_history(history)

    def display_history(self, history):
        print("display_history")
        for widget in self.winfo_children():
            widget.destroy()

        history_frame = tk.Frame(self, bg="#EEEEEE")
        history_frame.pack(expand=True, fill="both")

        list_frame = tk.Frame(history_frame)
        list_frame.pack(pady=20)

        for index, entry in enumerate(history):
            item = SongPerformanceEntry(
                list_frame,
                entry['number'],
                # entry['date'],
                entry['grade'],
                lambda idx=entry['id']: self.delete_entry(idx, history, list_frame,entry['song_name']),
                entry['id'],
                lambda idx=entry['id']: self.viewGraph(entry['song_name'], idx)
            )
            item.grid(row=index, column=0, sticky='w')

        back_button = tk.Button(history_frame, text="Back", command=self.create_main_content, bg="#EEEEEE", fg="#B31312",
                                font=("Helvetica", 14))
        back_button.pack(pady=20)

    def delete_entry(self, entry_id, history, list_frame, song_name):
        print(song_name)
        self.dbAccess.deletePerformance(entry_id, song_name)
        history[:] = [entry for entry in history if entry['id'] != entry_id]
        for widget in list_frame.winfo_children():
            widget.destroy()

        for index, entry in enumerate(history):
            item = SongPerformanceEntry(
                list_frame,
                index+1,
                entry['grade'],
                lambda performance_id=entry['id']: self.delete_entry(performance_id, history, list_frame, song_name),
                entry['id'],
                lambda idx=entry['id']: self.viewGraph(entry['song_name'], idx)
            )
            item.grid(row=index, column=0, sticky='w')

    def display_virtual_piano(self):
        for widget in self.winfo_children():
            widget.destroy()

        piano = VirtualPiano(self, width=1600, height=800)
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

        self.comparedSongsObject = ComparedSongs(archivedName, performanceSongName, performanceObject["score"],
                                                 infoDict, x, y, dtw_path)


    def viewGraph(self, songName, index):
        songNameWithoutUserName = songName.split('_')[0]
        result = self.dbAccess.fetchPerformancesFromUser(songNameWithoutUserName)

        resultDict = {}
        for performance in result:
            resultDict[performance['_id']] = performance

        self.compareOldSongsInFront(songNameWithoutUserName, resultDict[index])
        self.printGraph()



























# import tkinter as tk
# from tkinter.messagebox import showinfo
#
# import numpy as np
# from PIL import Image, ImageTk
#
# from compare import ComparedSongs, dtwElementInfo
# from frontend.SongComponent import SongComponent
# from frontend.SongPerformanceEntry import SongPerformanceEntry
# from frontend.VirtualPiano import VirtualPiano
# from frontend.OutOfTune import OutOfTune
# from filesAccess import *
#
#
# class MainContent(tk.Frame):
#     def __init__(self, parent):
#         super().__init__(parent, bg="#121212")
#         self.oot = None
#         self.userName = None
#         self.dbAccess = None
#         self.saveUserName()  #remove this when nadia makes the field
#         self.create_main_content()
#         self.comparedSongsObject = None
#
#
#     def saveUserName(self):
#         self.userName = "Roni"
#         self.dbAccess = DBAccess(self.userName)
#
#     def create_main_content(self):
#         songsDict = printAvailableSongs(self.dbAccess)
#         songsList = list(songsDict.values())
#         self.songs = [{"img": "./images/example.png", "title": str(i), "artist": "Artist 1"} for i in songsList]
#         self.refresh_content()
#
#     def refresh_content(self):
#         for widget in self.winfo_children():
#             widget.destroy()
#         columns_per_row = 3
#         for idx, song in enumerate(self.songs):
#             row = idx // columns_per_row
#             column = idx % columns_per_row
#             song_component = SongComponent(self, song)
#             song_component.grid(row=row, column=column, pady=20, padx=20, sticky="n")
#
#     def display_play_page(self, song):
#         for widget in self.winfo_children():
#             widget.destroy()
#
#         play_frame = tk.Frame(self, bg="#121212")
#         play_frame.pack(expand=True, fill="both")
#
#         try:
#             img = Image.open(song["img"])
#             img = img.resize((200, 200), Image.LANCZOS)
#             img = ImageTk.PhotoImage(img)
#         except FileNotFoundError:
#             showinfo("Error", f"Image file '{song['img']}' not found.")
#             return
#         except Exception as e:
#             showinfo("Error", f"Unable to open image: {e}")
#             return
#
#         img_label = tk.Label(play_frame, image=img, bg="#121212")
#         img_label.image = img
#         img_label.pack(pady=20)
#
#         song_title = tk.Label(play_frame, text=song["title"], fg="white", bg="#121212", font=("Helvetica", 24))
#         song_title.pack(pady=10)
#
#         song_artist = tk.Label(play_frame, text=song["artist"], fg="gray", bg="#121212", font=("Helvetica", 18))
#         song_artist.pack(pady=5)
#
#         play_button = tk.Button(play_frame, text="Play", command=lambda: self.startMic(song["title"]), bg="#1DB954",
#                                 fg="white", font=("Helvetica", 14))
#         play_button.pack(pady=20)
#
#         history_button = tk.Button(play_frame, text="History", command=lambda: self.showHistoryOfSong(song["title"]),
#                                    bg="#1DB954", fg="white", font=("Helvetica", 14))
#         history_button.pack(pady=20)
#
#     def startMic(self, songName):
#         self.oot = OutOfTune(self.userName)
#         self.comparedSongsObject = self.oot.read_from_mic(songName)
#         print(self.getGrade())
#         self.printGraph()
#
#
#     def getGrade(self):
#         if self.comparedSongsObject is None:
#             return 0
#         return self.comparedSongsObject.score
#
#     def printGraph(self):
#         self.comparedSongsObject.showBarGraph()
#         self.comparedSongsObject.hearClips()
#
#     def showHistoryOfSong(self, songName):
#         songNameWithoutUserName = songName.split('_')[0]
#         result = self.dbAccess.fetchPerformancesFromUser(songNameWithoutUserName)
#         print(result)
#
#         history = []
#         for num, performance in enumerate(result):
#             history.append({
#                 'number': num + 1,
#                 'id' : performance['_id'],
#                 'grade': performance['score'],
#                 'song_name': performance['song_name']
#             })
#         print(history)
#
#         self.display_history(history)
#
#     def display_history(self, history):
#         print("display_history")
#         for widget in self.winfo_children():
#             widget.destroy()
#
#         history_frame = tk.Frame(self, bg="#121212")
#         history_frame.pack(expand=True, fill="both")
#
#         list_frame = tk.Frame(history_frame)
#         list_frame.pack(pady=20)
#
#         for index, entry in enumerate(history):
#             item = SongPerformanceEntry(
#                 list_frame,
#                 entry['number'],
#                 # entry['date'],
#                 entry['grade'],
#                 lambda idx=entry['id']: self.delete_entry(idx, history, list_frame, entry['song_name']),
#                 entry['id'],
#                 lambda idx=entry['id']: self.viewGraph(entry['song_name'], idx)
#             )
#             item.grid(row=index, column=0, sticky='w')
#
#         back_button = tk.Button(history_frame, text="Back", command=self.create_main_content, bg="#1DB954", fg="white",
#                                 font=("Helvetica", 14))
#         back_button.pack(pady=20)
#
#     def delete_entry(self, entry_id, history, list_frame, song_name):
#         print(song_name)
#         self.dbAccess.deletePerformance(entry_id, song_name)
#         history[:] = [entry for entry in history if entry['id'] != entry_id]
#         for widget in list_frame.winfo_children():
#             widget.destroy()
#
#         for index, entry in enumerate(history):
#             item = SongPerformanceEntry(
#                 list_frame,
#                 index+1,
#                 entry['grade'],
#                 lambda performance_id=entry['id']: self.delete_entry(performance_id, history, list_frame, song_name),
#                 entry['id'],
#                 lambda idx=entry['id']: self.viewGraph(entry['song_name'], idx)
#             )
#             item.grid(row=index, column=0, sticky='w')
#
#     def display_virtual_piano(self):
#         for widget in self.winfo_children():
#             widget.destroy()
#
#         piano = VirtualPiano(self, width=1600, height=800)
#         piano.pack(fill=tk.BOTH, expand=True)
#         return piano
#
#     def compareOldSongsInFront(self, archivedName, performanceObject):
#         performanceId = performanceObject["_id"]
#         performanceSongName = performanceObject["song_name"] + performanceId
#         songData = getDataFromFile(archivedName)
#
#         origFreqsAndSeconds = songData.notesDict
#         dtw_path_str = performanceObject["dtw_lst"]
#         dtw_path = [(int(x[0]), int(x[1])) for x in dtw_path_str]
#         performanceFreqsAndSeconds = performanceObject["performance_notes_dict"]
#
#         y = np.array([float(x) for x in performanceFreqsAndSeconds.values()])
#         yTime = [float(x) for x in performanceFreqsAndSeconds.keys()]
#         x = np.array([x for x in origFreqsAndSeconds.values()])
#         xTime = [x for x in origFreqsAndSeconds.keys()]
#
#         infoDict = {}
#         for xIdx, yIdx in dtw_path:
#             infoDict[(xIdx, yIdx)] = dtwElementInfo(x[xIdx], y[yIdx], xIdx, yIdx, xTime[xIdx], yTime[yIdx])
#
#         self.comparedSongsObject = ComparedSongs(archivedName, performanceSongName, performanceObject["score"],
#                                                  infoDict, x, y, dtw_path)
#
#
#
#
#     def viewGraph(self, songName, index):
#         songNameWithoutUserName = songName.split('_')[0]
#         result = self.dbAccess.fetchPerformancesFromUser(songNameWithoutUserName)
#
#         resultDict = {}
#         for performance in result:
#             resultDict[performance['_id']] = performance
#
#         self.compareOldSongsInFront(songNameWithoutUserName, resultDict[index])
#         self.printGraph()
#
#
#     # def showHistoryOfSong(self, songName):
#     #     #get grades of older song, and choose one of them
#     #     songNameWithoutUserName = songName.split('_')[0]
#     #     result = self.dbAccess.fetchPerformancesFromUser(songNameWithoutUserName)
#     #
#     #     resultDict = {}
#     #     for num, performance in enumerate(result):
#     #         resultDict[num] = performance
#     #         print(f'{num}){songName}, Score: {performance["score"]}')
#     #
#     #     #performanceChosenIndex = int(input("\nSelect specific Performance: "))
#     #
#     #     performanceChosenIndex = 0  #In here we will put the index of the performance we chose
#     #     self.compareOldSongsInFront(songNameWithoutUserName, resultDict[performanceChosenIndex])
#     #
#     #     self.printGraph()
#     #     #self.oot.hearClips()
