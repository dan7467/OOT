import os
import wave
import random
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

import pyaudio

from db_persistence_layer import *

#PATH = '../songsData/'       #TODO WHen running from MainContent
#WAV_PATH = '../songsWav/'    #TODO WHen running from MainContent
PATH = './songsData/'       #TODO WHen running from tempScreen and mainTest
WAV_PATH = './songsWav/'    #TODO WHen running from tempScreen and mainTest
DELIMITER = ' ; '
DICT_DELIMITER = '-'
# SAMPLE_COUNTER_INDEX = 0
# RECORDING_LEN_SECONDS_INDEX = 1
# DURATION_TO_PROCESS_INDEX = 2
# SAMPLE_RATE_INDEX = 3
REST_INDEX = 0


class FileData:
    def __init__(self, songName, sampleCounter, recordingLenSeconds, durationToProcess, sampleRate, dict1):
        self.songName = songName
        self.sampleCounter = sampleCounter
        self.recordingLenSecond = recordingLenSeconds
        self.durationToProcess = durationToProcess
        self.sampleRate = sampleRate
        self.notesDict = dict1

    def getFrequencies(self):
        return list(self.notesDict.values())

    def getSecondsList(self):
        return list(self.notesDict.keys())


def getSongWavPath(songName):
    return WAV_PATH + songName


def getSongDataPath(songName):
    return PATH + songName + '.txt'


def printAvailableSongs(db):
    print("All the available songs:")
    dictSongs = dict()
    filesInFolder = [name[:-4] for name in os.listdir(PATH) if name.endswith('.txt')]
    filesInDb = db.getSongsNameList()
    #resultList = list(set(filesInFolder) & set(filesInDb))
    #for number, file_name in enumerate(os.listdir(PATH)):
    for number, file_name in enumerate(filesInDb):

        songStr = file_name
        print(f'{number}) {songStr}')
        dictSongs[str(number)] = songStr


    return dictSongs


def printAvailableWavs():
    print("All the available WAVs:")
    dictSongs = dict()
    for number, file_name in enumerate(os.listdir(WAV_PATH)):
        if file_name.endswith('.wav'):
            songStr = file_name[:-4]
            print(f'{number}) {songStr}')
            dictSongs[str(number)] = songStr

    return dictSongs


def checkIfFileExists(path):
    return os.path.isfile(path)


def checkIfSongDataExists(songName):
    path = getSongDataPath(songName)
    return os.path.isfile(path)


# Save to a specific file named as the songName.
# The format will be : sampleCounter ; recordingLenSeconds ; dictOfTimeToFreq ;
# Example : 500 ; 63.555 ; 05:345 - 543.2 , 05:666 - 622.2 ....
def saveToFile(fileData: FileData):
    path = PATH + fileData.songName + '.txt'
    # if checkIfFileExists(path):
    #     return

    with open(path, 'w') as f:
        # f.write(str(fileData.sampleCounter) + DELIMITER)
        # f.write(str(fileData.recordingLenSecond) + DELIMITER)
        # f.write(str(fileData.durationToProcess) + DELIMITER)
        # f.write(str(fileData.sampleRate) + DELIMITER)

        for currSecond, currFreq in zip(fileData.getSecondsList(), fileData.getFrequencies()):
            f.write(str(currSecond) + DICT_DELIMITER)
            f.write(str(currFreq) + DELIMITER)

    print('Done')


def getDataFromFile(songName):
    path = PATH + songName + '.txt'

    if not checkIfFileExists(path):
        return None

    freqDict = dict()
    # now read the data from the file and return sampleCounter ; recordingLenSeconds ; dictOfTimeToFreq ;
    with open(path, 'r') as f:
        lines = f.readlines()
        splitData = lines[0].split(DELIMITER)
        # sampleCounter = splitData[SAMPLE_COUNTER_INDEX]
        # recordingLenSeconds = float(splitData[RECORDING_LEN_SECONDS_INDEX])
        # duration_to_process = float(splitData[DURATION_TO_PROCESS_INDEX])
        # sampleRate = int(splitData[SAMPLE_RATE_INDEX])
        sampleCounter = 0
        recordingLenSeconds = 0
        duration_to_process = 0
        sampleRate = 16000
        splitData = splitData[REST_INDEX:]

        for curr in splitData:
            splitKeyValue = curr.split(DICT_DELIMITER)
            if len(splitKeyValue) > 1:
                time = float(splitKeyValue[0])
                freq = splitKeyValue[1]
                freqDict[time] = float(freq)

    fileData = FileData(songName, sampleCounter, recordingLenSeconds, duration_to_process, sampleRate, freqDict)
    return fileData


def getShortAudioClip(songName, startingSecond, endingSecond):
    path = getSongWavPath(songName) + ".wav"
    if not checkIfFileExists(path):
        print("file not found")
        return
    with wave.open(path, 'rb') as wav_file:
        # Get the sample width (in bytes)
        sample_width = wav_file.getsampwidth()

        # Get the frame rate (number of frames per second)
        frame_rate = wav_file.getframerate()
        try:
            # Calculate the starting and ending frames
            starting_frame = int(startingSecond * frame_rate)
            ending_frame = int(endingSecond * frame_rate)

            # Set the file position to the starting frame
            wav_file.setpos(starting_frame)

            # Read the frames for the desired section
            frames = wav_file.readframes(ending_frame - starting_frame)
        except:
            print("Seconds not valid")
            return

    # Play the extracted audio
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(sample_width),
                    channels=wav_file.getnchannels(),
                    rate=frame_rate,
                    output=True)
    stream.write(frames)
    stream.stop_stream()
    stream.close()
    p.terminate()

    # return frames, sample_width, frame_rate


def removeFIle(path):
    try:
        os.remove(path)
        print(f"The file '{path}' has been deleted successfully.")
    except FileNotFoundError:
        print(f"The file '{path}' does not exist.")
    except PermissionError:
        print(f"You do not have permission to delete the file '{path}'.")
    except Exception as e:
        print(f"An error occurred while deleting the file: {e}")


def deleteSongWavAndData(songName):
    deleteSongWav(songName)

    dataPath = getSongDataPath(songName)
    removeFIle(dataPath)

def deleteSongWav(songName):
    nameWithWav = songName + '.wav'
    wavPath = getSongWavPath(nameWithWav)
    removeFIle(wavPath)


def deleteSongData(songName):
    dataPath = getSongDataPath(songName)
    removeFIle(dataPath)


###########################################################################
## new DB
class DBAccess:
    def __init__(self, userId):
        self.userId = userId
        self.db = connect_to_db()

        db_create_user(self.db, self.userId)

    def addSongForUser(self, songName):
        try:
            db_add_new_song_for_existing_user(self.db, self.userId, songName)
        except:
            print("Already in db")

    def fetchSongsFromUser(self):
        return fetch_every_song_sang_by_user(self.db, self.userId)
        #return fetch_user_from_db(self.db, self.userId)


    def checkIfSongDataExists(self, songName):
        return fetch_song_of_user(self.db, songName) is not None


    def getSongsNameList(self):
        allSongs = fetch_every_song_sang_by_user(self.db, self.userId)
        songsNames = [element['_id'] for element in allSongs]
        return songsNames


    def add_performance_for_existing_user_and_song(self, secondsFreqsDict, songName, performanceId, dtw_lst, score):

        performance_dtw_id = songName
        freqsAndTimeStr = self.convertDictToStr(secondsFreqsDict)
        db_add_performance_for_existing_user_and_song(self.db, performance_dtw_id, performanceId, songName,
                                                      freqsAndTimeStr, dtw_lst, score)


    def getUserIdStr(self):
        return '_' + self.userId

    def convertDictToStr(self, secondsFreqsDict):
        result = {}
        for key, value in secondsFreqsDict.items():
            result[str(key)] = str(value)
        return result

    def fetchPerformancesFromUser(self, songName):
        result = fetch_every_user_performance(self.db, songName, self.userId)
        result = [x for x in result if x is not None]
        return result

    def deletePerformance(self, performanceId, songName):
        #songUserName = songName + self.getUserIdStr()
        songUserName = songName

        db_remove_performance(self.db, performanceId, songUserName)
        self.removePerformanceLocal(performanceId, songUserName)

    def deleteSongAndPerformances(self, songName):
        songName = songName + self.getUserIdStr()
        self.removeFromLocal(songName)

        db_deep_remove_song_of_user(self.db, songName, self.userId)


    def removeFromLocal(self, songName):
        performancesIds = self.getPerformanceIdsOfSong(songName)
        for performanceId in performancesIds:
            self.removePerformanceLocal(performanceId, songName)

        #deleteSongWavAndData(songName) #I don't think its necessary

    def deleteUser(self):

        songList = self.getSongsNameList()
        for songName in songList:
            self.removeFromLocal(songName)

        db_deep_remove_user(self.db, self.userId)


    def getPerformanceIdsOfSong(self, songName):
        songs_of_user = fetch_song_of_user(self.db, songName)
        if songs_of_user is not None and len(songs_of_user['user_performances_id_list']) > 0:
            return songs_of_user['user_performances_id_list']
        return []

    def removePerformanceLocal(self, performanceId, songName):
        wavSongName = songName + str(performanceId)
        deleteSongWav(wavSongName)
