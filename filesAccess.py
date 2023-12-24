import os


PATH = './songsData/'
DELIMITER = ' ; '
DICT_DELIMITER = '-'
WAV_PATH = './songsWav/'
SAMPLE_COUNTER = 0
RECORDING_LEN_SECONDS = 1
DURATION_TO_PROCESS = 2


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
def saveToFile(songName, secondsList, freqList, sampleCounter, recordingLenSeconds, duration_to_process):
    path = PATH + songName + '.txt'
    if checkIfFileExists(path):
        return

    with open(path, 'w') as f:
        f.write(str(sampleCounter) + DELIMITER)
        f.write(str(recordingLenSeconds) + DELIMITER)
        f.write(str(duration_to_process) + DELIMITER)

        for currSecond, currFreq in zip(secondsList, freqList):
            f.write(str(currSecond) + DICT_DELIMITER)
            f.write(str(currFreq) + DELIMITER)

    print('Done')



def getDataFromFile(songName):
    path = PATH + songName + '.txt'
    if not checkIfFileExists(path):
        return None, None, None

    freqDict = dict()
    #now read the data from the file and return sampleCounter ; recordingLenSeconds ; dictOfTimeToFreq ;
    with open(path, 'r') as f:
        lines = f.readlines()
        splitData = lines[0].split(DELIMITER)
        sampleCounter = splitData[SAMPLE_COUNTER]
        recordingLenSeconds = float(splitData[RECORDING_LEN_SECONDS])
        duration_to_process = float(splitData[DURATION_TO_PROCESS])
        splitData = splitData[3:]

        for curr in splitData:
            splitKeyValue = curr.split(DICT_DELIMITER)
            if len(splitKeyValue) > 1:
                time = float(splitKeyValue[0])
                freq = splitKeyValue[1]
                freqDict[time] = freq

    return sampleCounter, recordingLenSeconds, freqDict, duration_to_process

