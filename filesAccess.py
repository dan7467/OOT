import os
import wave

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


#Save to a specific file named as the songName.
#The format will be : sampleCounter ; recordingLenSeconds ; dictOfTimeToFreq ;
#Example : 500 ; 63.555 ; 05:345 - 543.2 , 05:666 - 622.2 ....
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
    #now read the data from the file and return sampleCounter ; recordingLenSeconds ; dictOfTimeToFreq ;
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

    #return frames, sample_width, frame_rate


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


#TODO DAN
def saveInDB(x, y, dtw_path, xTime, yTime, score):
    # x is the notes list from mic
    # xTIme is the second list from mic

    # y is the notes list from original
    # yTIme is the second list from original

    # dtw_path is the indices from each list that is matching
    xIndices = [element[0] for element in dtw_path]
    yIndices = [element[1] for element in dtw_path]

    # I think tou can save the dtw_path complete without breaking it to x indices and y indices.
    pass



#TODO DAN
def getPassedSongScoresFromDB(songName):
    # get all the performances scores

    return None


#TODO DAN
def getPassedSongDTWPath(songName, performanceId):
    # get dtwPath from this performance and song

    return None

#TODO DAN
def getPassedSongFreqsAndSeconds(songName, performanceId):
    # return 2 lists of freqs and seconds
    freqs = []
    seconds = []

    return freqs, seconds



