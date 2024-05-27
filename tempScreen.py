from main import OutOfTune
from filesAccess import *


def getHistory(oot1):
    allSongs = oot1.fetchAllSongsForUser()
    songsDict = {}
    for num, song in enumerate(allSongs):
        songsDict[num] = song
        print(f'{num}) {songsDict[num]["_id"]}')

    songNum = int(input("Enter the number of the song you want to see: "))
    songName = songsDict[songNum]["_id"].split('_')[0]
    result = oot1.fetchAllPerformances(songName)
    resultDict = {}
    for num, performance in enumerate(result):
        resultDict[num] = performance
        print(f'{num}){songName}, Score: {performance["score"]}')
        #print(f'{num}) Score: {performance["song_name"]}')
    performanceChosenIndex = int(input("\nSelect specific Performance: "))

    oot1.compareOldSongs(songName, resultDict[performanceChosenIndex])


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
    oot1.getSongData(nameWithWav, True, oot1)


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

