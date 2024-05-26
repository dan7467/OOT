import os
import wave
import random
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

import pyaudio

PATH = './songsData/'
DELIMITER = ' ; '
DICT_DELIMITER = '-'
WAV_PATH = './songsWav/'
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


def printAvailableSongs():
    print("All the available songs:")
    dictSongs = dict()
    for number, file_name in enumerate(os.listdir(PATH)):
        if file_name.endswith('.txt'):
            songStr = file_name[:-4]
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
    nameWithWav = songName + '.wav'
    wavPath = getSongWavPath(nameWithWav)
    removeFIle(wavPath)

    dataPath = getSongDataPath(songName)
    removeFIle(dataPath)


def deleteSongData(songName):
    dataPath = getSongDataPath(songName)
    removeFIle(dataPath)


# TODO DAN
def add_performance_for_existing_user_and_song(seconds, freqs, songName, performanceName):
    # x is the notes list from mic
    # xTIme is the second list from mic

    # y is the notes list from original
    # yTIme is the second list from original


    pass


def add_dtw_for_performance(dtw_path, songId, performanceId):
    # dtw_path is the indices from each list that is matching
    xIndices = [element[0] for element in dtw_path]
    yIndices = [element[1] for element in dtw_path]

    pass

def add_new_song_for_existing_user(songName):
    pass


# TODO DAN
def getPassedSongScoresFromDB(songName):
    # get all the performances scores

    return None


# TODO DAN
def getPassedSongDTWPath(songName, performanceId):
    # get dtwPath from this performance and song

    return None


# TODO DAN
def getPassedSongFreqsAndSeconds(songName, performanceId):
    # return 2 lists of freqs and seconds
    freqs = []
    seconds = []

    return freqs, seconds


###########################################################################
## MONGODB

def connect_to_db():
    uri = "mongodb+srv://ootUser:RA6IdLBdYVb9eBvh@cluster1outoftune.suznj28.mongodb.net/?retryWrites=true&w=majority&appName=cluster1outOfTune&ssl=true&tls=true&tlsAllowInvalidCertificates=true"
    # Dan: here we create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))
    # Dan: here we send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("\n### CONNECTED: Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
    return client.oot_database


def db_create_user(db, user_id):
    # Dan: this object is for the users-table (which is inside the OOT_database, which is inside the OOT_Cluster, which is inside MongoDB)
    users = db.users
    print('\n### UPLOADING: starting upload to users ...')
    users.insert_one({'_id': user_id, "user_songs": []})
    print('\n### CREATED: succesfuly created ', user_id, 'in mongoDB!')


def db_add_new_song_for_existing_user(db, user_id, user_song_id):
    # Dan: this object is for the users-table (which is inside the OOT_database, which is inside the OOT_Cluster, which is inside MongoDB)
    users = db.users
    # Dan: this object is for the songs_of_user-table
    songs_of_user = db.songs_of_user
    # Dan: here we update a new song which the user sang, in db -
    print('\n### UPDATING: starting update to users ...')
    users.update_one({'_id': user_id}, {"$set": {"user_songs": [user_song_id]}})
    print('\n### UPDATED: succesfuly updated ', user_id, ' with ', user_song_id, 'in mongoDB!')
    print('\n### UPLOADING: starting upload to songs-of-user ...')
    songs_of_user.insert_one({'_id': user_song_id, "user_performances_id_list": []})
    print('\n### CREATED: succesfuly created song', user_song_id, 'in mongoDB!')


def db_add_performance_for_existing_user_and_song(db, performance_dtw_id, performance_id, song_name,
                                                  times_and_freqs_dict):
    user_performances = db.user_performances
    songs_of_user = db.songs_of_user
    print('\n### UPDATING: starting update to users ...')
    songs_of_user.update_one({'_id': performance_dtw_id},
                             {"$push": {"user_performances_id_list": {"$each": [performance_id]}}})
    # print('\n### UPDATED: succesfuly updated ', user_id, ' with ', user_song_id, 'with id:', performance_id,
    #      'in mongoDB!')
    # Dan: this object is for the user-performances-table
    print('\n### UPLOADING: starting upload to user_performances ...')
    user_performances_dtw_assigned_ID_in_db = user_performances.insert_one(
        {'_id': performance_id, 'song_name': song_name, "performance_notes_dict": times_and_freqs_dict})
    print('\n### CREATED: succesfuly created ', performance_dtw_id, 'in mongoDB!')


def generate_random_id(length=10):
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    rnd_str = ''.join(random.choice(chars) for _ in range(length))
    return rnd_str


def fetch_user_from_db(db, user_id):
    # Dan: this object is for the users-table (which is inside the OOT_database, which is inside the OOT_Cluster, which is inside MongoDB)
    users = db.users
    # Dan: here we fetch a user from the 'users' collection
    print('\n### FETCHING: Fetching ID #', user_id, ' from table users ...')
    fetched_data = users.find_one({"_id": user_id})
    print('\n### FETCHED: successfuly fetched the following - ', fetched_data)
    return fetched_data


def fetch_song_of_user(db, user_song_id):
    # Dan: this object is for the songs_of_user-table
    songs_of_user = db.songs_of_user
    # Dan: here we fetch a user_performance from the 'user_performances' collection
    print('\n### FETCHING: Fetching', user_song_id, 'from  table songs_of_user ...')
    fetched_data = songs_of_user.find_one({"_id": user_song_id})
    print('\n### FETCHED: successfuly fetched the following - ', fetched_data)
    return fetched_data


def fetch_user_performance(db, performance_id):
    # Dan: this object is for the user-performances-table (which is inside the OOT_database, which is inside the OOT_Cluster, which is inside MongoDB)
    user_performances = db.user_performances
    # Dan: here we fetch a user_performance from the 'user_performances' collection
    print('\n### FETCHING: Fetching ID #', performance_id, ' from  table user_performances ...')
    fetched_data = user_performances.find_one({"_id": performance_id})
    print('\n### FETCHED: successfuly fetched the following - ', fetched_data)
    return fetched_data


def fetch_every_song_sang_by_user(db, user_id):
    songs_of_user = db.songs_of_user
    print('\n### FETCHING: Fetching every song sang by', user_id, '...')
    fetched_data = list(songs_of_user.find({"_id": {"$regex": user_id}}))
    print('\n### FETCHED: successfuly fetched every song which was sang by', user_id, ':\n', fetched_data)
    return fetched_data


def fetch_every_user_performance(db, song_name, user_id):
    user_performances = db.user_performances
    fetch_id = song_name + '_' + user_id
    songs_of_user = fetch_song_of_user(db, fetch_id)
    performances_ids = songs_of_user['user_performances_id_list']
    fetched_data = []
    print('\n### FETCHING: Fetching every performance of', song_name, 'sang by', user_id, '...')
    for performance_id in performances_ids:
        fetched_data.append(user_performances.find_one({"_id": performance_id}))
    print('\n### FETCHED: successfuly fetched every performance for', song_name, 'sang by', user_id, ':\n',
          fetched_data)
    return fetched_data


def getSongID(songName):
    return 1

