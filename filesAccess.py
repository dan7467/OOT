import os


PATH = './songsData/'
DELIMITER = ' ; '
DICT_DELIMITER = '-'
WAV_PATH = './songsWav/'
SAMPLE_COUNTER_INDEX = 0
RECORDING_LEN_SECONDS_INDEX = 1
DURATION_TO_PROCESS_INDEX = 2
SAMPLE_RATE_INDEX = 3
REST_INDEX = 4

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


def checkIfFileExists(path):
    return os.path.isfile(path)

def checkIfSongDataExists(songName):
    path = PATH + songName + '.txt'
    return os.path.isfile(path)


#Save to a specific file named as the songName.
#The format will be : sampleCounter ; recordingLenSeconds ; dictOfTimeToFreq ;
#Example : 500 ; 63.555 ; 05:345 - 543.2 , 05:666 - 622.2 ....
def saveToFile(fileData: FileData):
    path = PATH + fileData.songName + '.txt'
    if checkIfFileExists(path):
        return

    with open(path, 'w') as f:
        f.write(str(fileData.sampleCounter) + DELIMITER)
        f.write(str(fileData.recordingLenSecond) + DELIMITER)
        f.write(str(fileData.durationToProcess) + DELIMITER)
        f.write(str(fileData.sampleRate) + DELIMITER)

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
        sampleCounter = splitData[SAMPLE_COUNTER_INDEX]
        recordingLenSeconds = float(splitData[RECORDING_LEN_SECONDS_INDEX])
        duration_to_process = float(splitData[DURATION_TO_PROCESS_INDEX])
        sampleRate = int(splitData[SAMPLE_RATE_INDEX])
        splitData = splitData[REST_INDEX:]

        for curr in splitData:
            splitKeyValue = curr.split(DICT_DELIMITER)
            if len(splitKeyValue) > 1:
                time = float(splitKeyValue[0])
                freq = splitKeyValue[1]
                freqDict[time] = freq


    fileData = FileData(songName, sampleCounter, recordingLenSeconds, duration_to_process, sampleRate, freqDict)
    return fileData

