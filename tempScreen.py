from main import OutOfTune, getSongData
from filesAccess import *

def openMenu(oot1):
    option = input("What do you want to do? \n1) Sing \n2) Manage Songs \n\nAnswer: ")
    if option == '1':
        oot1.read_from_mic()
    elif option == '2':
        manageSongs(oot1)


def analyzeNewSong(oot1):

    dictSongs = printAvailableWavs()

    songName = input("Enter the name of the song you want to add: ")
    nameWithWav = songName + '.wav'
    getSongData(nameWithWav, True, oot1)


def deleteSong(oot1, option):
    print("\n\n")
    dictSongs = printAvailableSongs()

    songName = input("Enter the name of the song you want to remove: ")
    if option == '1':
        deleteSongData(songName)
    elif option == '2':
        deleteSongWavAndData(songName)



def manageSongs(oot1):
    option = input("1) Delete Song Data\n"
                   "2) Delete Song Data and Wav\n"
                   "3) Add data from recording \n\n"
                   "Answer: ")
    if option == '1':
        deleteSong(oot1, '1')
    elif option == '2':
        deleteSong(oot1, '2')
    elif option == '3':
        analyzeNewSong(oot1)




if __name__ == "__main__":
    oot = OutOfTune()
    openMenu(oot)

