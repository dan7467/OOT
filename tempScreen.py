from main import OutOfTune, getSongData
from filesAccess import *


def getHistory(oot1):
    songName = input("Enter the name of the song you want to add: ")
    oot1.compareOldSongs(songName, songName + 'Mic')


def openMenu(oot1):
    option = input("What do you want to do? \n1) Sing \n2) Manage Songs \n3)View history \n\nAnswer: ")
    if option == '1':
        oot1.read_from_mic()
    elif option == '2':
        manageSongs(oot1)
    elif option == '3':
        getHistory(oot1)

#Return -1 if song does not exist
def printSongsWAVMenuAndReturnName():
    dictSongs = printAvailableWavs()

    songNum = input("Enter the number of the song: ")
    if songNum not in dictSongs.keys():
        print("Error")
        return "-1"
    else:
        return dictSongs[songNum]

def analyzeNewSong(oot1):

    res = printSongsWAVMenuAndReturnName()
    if res == "-1":
        return

    nameWithWav = res + '.wav'
    getSongData(nameWithWav, True, oot1)


def deleteSong(oot1, option):
    print("\n\n")

    songName = printSongsWAVMenuAndReturnName()
    if songName == "-1":
        return

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

