import math
from typing import List
import numpy as np
from matplotlib import pyplot as plt
import tkinter as tk

from filesAccess import *

#import sklearn
import tslearn
from tslearn import *
from tslearn import metrics
#from sklearn.metrics import r2_score

from tslearn.backend import instantiate_backend             #TODO Dont delete this!!
from tslearn.backend.numpy_backend import  NumPyBackend     #TODO Dont delete this!!
from sklearn.metrics.pairwise import euclidean_distances    #TODO Dont delete this!!
from sklearn.metrics.pairwise import pairwise_distances     #TODO Dont delete this!!

class dtwElementInfo:
    def __init__(self, x, y, xIndex, yIndex, xTime, yTime):
        self.xFreq = x
        self.yFreq = y
        self.xDTWIndex = xIndex
        self.yDTWIndex = yIndex
        self.xTime = xTime
        self.yTime = yTime

class ComparedSongs:
    def __init__(self, songName, performanceName, grade, dtwElements, x, y, dtw_path):
        self.songName = songName
        self.performanceName = performanceName
        self.score = grade
        self.dtwElements = dtwElements
        self.x = x
        self.y = y
        self.dtw_path = dtw_path


    def showBarGraph(self):
        alignedDTWBarPlot(self.x, self.y, self.dtw_path)



    def hearClips(self):
        window = tk.Tk()

        # file_label = tk.Label(window, text="File Name:")
        # file_label.pack()
        # file_name_entry = tk.Entry(window)
        # file_name_entry.pack()

        starting_label = tk.Label(window, text="Starting Second:")
        starting_label.pack()
        starting_entry = tk.Entry(window)
        starting_entry.pack()

        ending_label = tk.Label(window, text="Ending Second:")
        ending_label.pack()
        ending_entry = tk.Entry(window)
        ending_entry.pack()

        play_button_mic = tk.Button(window, text="Play from original",
                                    command=lambda: self.getShortAudioClipFromEntries(2, starting_entry.get(),
                                                                                      ending_entry.get(), self.dtwElements))
        play_button_orig = tk.Button(window, text="Play from mic",
                                     command=lambda: self.getShortAudioClipFromEntries(1,
                                                                                       starting_entry.get(),
                                                                                       ending_entry.get(),
                                                                                       self.dtwElements))
        play_button_mic.pack()
        play_button_orig.pack()

        def on_closing():
            window.destroy()

        window.protocol("WM_DELETE_WINDOW", on_closing)
        window.mainloop()


    def getShortAudioClipFromEntries(self, name, startingIndex, endingIndex, dtwElementsInfo):
        startingIndex = int(startingIndex)
        endingIndex = int(endingIndex)
        if name == 1:
            songName = self.performanceName
            startingSecond, endingSecond = getClosestElementsWIthIndices(dtwElementsInfo, startingIndex,
                                                                         endingIndex, "x")
        else:
            songName = self.songName
            startingSecond, endingSecond = getClosestElementsWIthIndices(dtwElementsInfo, startingIndex,
                                                                         endingIndex, "y")

        getShortAudioClip(songName, startingSecond, endingSecond)



TUNER_NOTES = {65.41: 'C2', 69.30: 'C#2', 73.42: 'D2', 77.78: 'D#2',
                   82.41: 'E2', 87.31: 'F2', 92.50: 'F#2', 98.00: 'G2',
                   103.80: 'G#2', 110.00: 'A2', 116.50: 'B#2', 123.50: 'B2',
                   130.80: 'C3', 138.60: 'C#3', 146.80: 'D3', 155.60: 'D#3',
                   164.80: 'E3', 174.60: 'F3', 185.00: 'F#3', 196.00: 'G3',
                   207.70: 'G#3', 220.00: 'A3', 233.10: 'B#3', 246.90: 'B3',
                   261.60: 'C4', 277.20: 'C#4', 293.70: 'D4', 311.10: 'D#4',
                   329.60: 'E4', 349.20: 'F4', 370.00: 'F#4', 392.00: 'G4',
                   415.30: 'G#4', 440.00: 'A4', 466.20: 'B#4', 493.90: 'B4',
                   523.30: 'C5', 554.40: 'C#5', 587.30: 'D5', 622.30: 'D#5',
                   659.30: 'E5', 698.50: 'F5', 740.00: 'F#5', 784.00: 'G5',
                   830.60: 'G#5', 880.00: 'A5', 932.30: 'B#5', 987.80: 'B5',
                   1047.00: 'C6', 1109.0: 'C#6', 1175.0: 'D6', 1245.0: 'D#6',
                   1319.0: 'E6', 1397.0: 'F6', 1480.0: 'F#6', 1568.0: 'G6',
                   1661.0: 'G#6', 1760.0: 'A6', 1865.0: 'B#6', 1976.0: 'B6',
                   2093.0: 'C7'}


def freqToNote(freq):
    if freq == 0:
        return '0'
    return TUNER_NOTES[freq]


def are_the_same_note(frequency1, frequency2):
    return abs(frequency1 - frequency2) < 1
def are_neighbors(frequency1, frequency2):
    res1 = abs(frequency1 * math.pow(2, 1/12) - frequency2)
    res2 = abs(frequency2 * math.pow(2, 1/12) - frequency1)
    return res1 < 1 or res2 < 1



# # https://discord.com/channels/1183328278983999579/1184833831686111365/1186322859036000437
# def fastDTWTest(x, y):
#     # distance, path = fastdtw(x, y, dist=d.euclidean)
#     distance, path = fastdtw(x, y, dist=d.cosine)
#     print(f"Distance: {distance}")
#     print(f"Path: {path}")
#
#     for (i, j) in path:
#         print(f"{i}: {x[i]}, {j}: {y[j]}")


# # https://discord.com/channels/1183328278983999579/1184833831686111365/1186323274964148295
# def dtwvisTest(x, y):
#     fig, ax = plt.subplots(2, 1, figsize=(1280 / 96, 720 / 96))
#
#     # path = dtw.warping_path(x, y)
#     path = dtw.warping_path(x, y, window=1)
#
#     # Print matched points along the DTW alignment path
#     print("Matched Points:")
#     for point in path:
#         mic_idx, arc_idx = point
#         print(f"Microphone[{mic_idx}]={x[mic_idx]} - {y[arc_idx]}=Archive[{arc_idx}]")
#
#     dtwvis.plot_warping(x, y, path, fig=fig, axs=ax)
#     ax[0].set_title('Microphone Version')
#     ax[1].set_title('Archived Version')
#     fig.tight_layout()
#     plt.show()


def printNotesMatches(x, y, path, xTime, yTime):
    matched0 = [position[0] for position in path]
    notMatched0 = [i for i in range(matched0[-1]) if i not in matched0]

    matched1 = [position[1] for position in path]
    notMatched1 = [i for i in range(matched1[-1]) if i not in matched1]

    print("\nMatched notes\n")

    # print the matches of lcss
    for positions in path:
        xIndex = positions[0]
        yIndex = positions[1]
        print(f'x[{xIndex}] = {x[xIndex]} , {y[yIndex]} = y[{yIndex}].      Times: {xTime[xIndex]} - {yTime[yIndex]}')

    print("\nUnmatched notes\n")

    [print(f"Note X[{i}]={x[i]} is not matched") for i in notMatched0]
    print("\n")
    [print(f"Note Y[{i}]={y[i]} is not matched") for i in notMatched1]



# def firstDTWGraph(x, y, dtw_path):
#     plt.figure(figsize=(8, 8))
#     plt.plot(x, "r-", label='First time series')
#     plt.plot(y, color='black', linestyle='--', label='Second time series')
#
#     for positions in dtw_path:
#         plt.plot([positions[0], positions[1]],
#                  [x[positions[0]], y[positions[1]]], color='orange')
#     plt.legend()
#     plt.title("Time series matching with DTW")
#
#     plt.tight_layout()
#     plt.show()


def alignedDTWGraph(x, y, dtw_path):

    x_path = [i[0] for i in dtw_path]
    y_path = [i[1] for i in dtw_path]


    plt.plot(x[x_path], label="mic (x)")
    plt.plot(y[y_path], label="original (y)")
    plt.legend()
    plt.title("Matching with DTW, Aligned Graphs")
    plt.show()
    plt.savefig("Aligned Graphs.png")


def alignedDTWBarPlot(x, y, dtw_path):
    x_path = [i[0] for i in dtw_path]
    y_path = [i[1] for i in dtw_path]

    # Create a bar plot
    fig, ax = plt.subplots(figsize=(16, 8))
    width = 0.35  # Width of the bars

    # Plot the x data as bars
    x_bar = ax.bar(x_path, x[x_path], width, label="mic (x)")

    # Plot the y data as bars
    y_bar = ax.bar([i + width for i in x_path], y[y_path], width, label="original (y)")

    # Add labels and title
    ax.set_xlabel('Index')
    ax.set_ylabel('Freq')
    ax.set_title('Matching with DTW, Aligned Graphs')
    ax.legend()

    for barX, x_idx, barY, y_idx in zip(x_bar, x_path, y_bar, y_path):

        freq1 = x[x_idx]
        freq2 = y[y_idx]
        label_color = ''
        if are_the_same_note(freq1, freq2):
            label_color = 'green'
        elif are_neighbors(freq1, freq2):
            label_color = '#FFD700'   #yellow
        else:
            label_color = 'red'

        noteX = freqToNote(x[x_idx])
        noteY = freqToNote(y[y_idx])
        if noteY == noteX:
            ax.annotate(noteX,
                        xy=(barX.get_x() + barX.get_width(), barX.get_height()),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', rotation=90, color=label_color)  # Rotate the label vertically
        else:
            ax.annotate(noteX,
                        xy=(barX.get_x() + barX.get_width() / 2, barX.get_height()),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', rotation=90, color=label_color)  # Rotate the label vertically
            ax.annotate(noteY,
                        xy=(barY.get_x() + barY.get_width() / 2, barY.get_height()),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', rotation=90, color=label_color)  # Rotate the label vertically



    # # Add note labels manually
    # for bar, x_idx in zip(x_bar, x_path):
    #     note = freqToNote(x[x_idx])
    #     ax.annotate(note,
    #                 xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
    #                 xytext=(0, 3),
    #                 textcoords="offset points",
    #                 ha='center', va='bottom')
    #
    # for bar, y_idx in zip(y_bar, y_path):
    #     note = freqToNote(y[y_idx])
    #     ax.annotate(note,
    #                 xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
    #                 xytext=(0, 3),
    #                 textcoords="offset points",
    #                 ha='center', va='bottom')

    # Show the plot
    plt.tight_layout()

    plt.savefig("Bar Plot.png")
    plt.show()

#Remove duplicate indices from the mic version, so there will be only NUM to NUM match, not NUMS to NUM!
def removeDuplicatesFromXPath(x, y, dtw_path, xTime, yTime):

    # Create a dictionary to store the mapping of x indices to y indices
    x_to_y_mapping = {}

    # Iterate through the DTW path
    for x_idx, y_idx in dtw_path:

        # Check if x index is already mapped to a y index
        if x_idx not in x_to_y_mapping:
            x_to_y_mapping[x_idx] = y_idx
        else:
            # If x index is already mapped, check if the current y index is closer to x index
            if abs(y[y_idx] - x[x_idx]) < abs(y[x_to_y_mapping[x_idx]] - x[x_idx]):
                x_to_y_mapping[x_idx] = y_idx


    #infoList.append(dtwElementInfo(x[xIndex], y[yIndex], xIndex, yIndex, xTime, yTime))

    # Update the DTW path with the selected y indices
    dtw_path = [(x_idx, x_to_y_mapping[x_idx]) for x_idx in x_to_y_mapping]

    # # Update x and y sequences based on the updated DTW path
    # x = [x[i] for i, _ in dtw_path]
    # y = [y[j] for _, j in dtw_path]

    infoDict = {}
    for xIdx, yIdx in dtw_path:
        infoDict[(xIdx, yIdx)] = dtwElementInfo(x[xIdx], y[yIdx], xIdx, yIdx, xTime[xIdx], yTime[yIdx])

    return np.array(x), np.array(y), dtw_path, infoDict


def computeScore(micFreqs, origFreqs):
    # Calculate L2 distance
    l2_distance = np.sqrt(np.sum((micFreqs - origFreqs) ** 2))

    # Calculate maximum possible L2 distance
    n = len(micFreqs)
    min_val, max_val = 65, 2100  # Range of possible frequencies in Hz (C2 to C7)
    max_distance = np.sqrt(n) * (max_val - min_val)

    # Calculate similarity score
    score = int((1 - (l2_distance / max_distance)) * 100)
    print(f'Score: {score}')


    normalized_distance = l2_distance / max_distance
    alpha = 8                                               #larging the alpha will lower results more
    # Apply exponential decay to the normalized distance
    similarity = int(np.exp(-alpha * normalized_distance) * 100)
    print(f'Score normalized 2: {similarity}')
    #TODO decide which score to use!!
    return similarity


def lcssAndDTW(x, y, xTime, yTime, songName, newMicSOngName):
    # Do I need to normalize it? yse a scaler like the example from the link?

    # Calculate DTW path and similarity
    dtw_path, sim_dtw = tslearn.metrics.dtw_path(x, y, sakoe_chiba_radius=1)

    # Plotting
    #plt.figure(figsize=(8, 8))
    #lcssPlot(x, y, xTime, yTime)

    #firstDTWGraph(x, y, dtw_path)


    print("DTW PATH")
    printNotesMatches(x, y, dtw_path, xTime, yTime)

    #alignedDTWGraph(x, y, dtw_path)

    x, y, dtw_path, dtwElementsDict = removeDuplicatesFromXPath(x, y, dtw_path, xTime, yTime)


    micFreqs = np.array([element.xFreq for element in dtwElementsDict.values()])
    origFreqs = np.array([element.yFreq for element in dtwElementsDict.values()])

    score = computeScore(micFreqs, origFreqs)

    #add_dtw_for_performance()

    #WITH THIS WE CAN SEE THE GRAPH
    #alignedDTWBarPlot(x, y, dtw_path)

    comparedSongs = ComparedSongs(songName, newMicSOngName, score, dtwElementsDict, x, y, dtw_path)
    # return dtwElementsDict, score
    return comparedSongs

#
# def lcssPlot(x, y, xTime, yTime):
#     # Calculate LCSS path and similarity
#     lcss_path, sim_lcss = metrics.lcss_path(x, y)
#     #This is with times
#     # plt.plot(xTime, x, "r-", label='First time series')
#     # plt.plot(yTime, y, color='black', linestyle='--', label='Second time series')
#     # for positions in lcss_path:
#     #     plt.plot([xTime[positions[0]], yTime[positions[1]]],
#     #              [x[positions[0]], y[positions[1]]], color='orange')
#
#     plt.plot(x, "r-", label='First time series')
#     plt.plot(y, color='black', linestyle='--', label='Second time series')
#     for positions in lcss_path:
#         plt.plot([positions[0], positions[1]],
#                  [x[positions[0]], y[positions[1]]], color='orange')
#
#     plt.legend()
#     plt.title("Time series matching with LCSS")
#
#     print("LCSS PATH")
#     printNotesMatches(x, y, lcss_path, xTime, yTime)

#
# #https://htmlpreview.github.io/?https://github.com/statefb/dtwalign/blob/master/example/example.html#:~:text=Utilities-,Basic%20Usage,-%C2%B6
# def dtwAlignTest(x, y, xTime, yTime):
#     res = dtwAlignFunc(x, y)
#     print("dtw distance: {}".format(res.distance))
#     print("dtw normalized distance: {}".format(res.normalized_distance))
#
#     #res.plot_path()
#
#     # warp both x and y by alignment path
#     x_path = res.path[:, 0]
#     y_path = res.path[:, 1]
#     plt.plot(x[x_path], label="aligned query")
#     plt.plot(y[y_path], label="aligned reference")
#     plt.legend()
#     plt.show()
#
#     printNotesMatches(x, y, res.path, xTime, yTime)



# def compareDTW(micFreq: FileData, archivedFreq: FileData):
#     # I can try different distances (cosine, euclidean, norm1...)
#
#     x = micFreq.getFrequencies()
#     xTime = micFreq.getSecondsList()
#     y = archivedFreq.getFrequencies()
#     yTime = archivedFreq.getSecondsList()
#
#     x = np.array([float(curr) for curr in x])
#     y = np.array([float(curr) for curr in y])
#
#     #fastDTWTest(x, y)
#     #dtwvisTest(x, y)            #prints graph
#     return lcssAndDTW(x, y, xTime, yTime)


def compare2Songs(origSongAndTime, performanceFreqAndTime,  songName, newMicSOngName):
    xTime = list(origSongAndTime.keys())
    x = origSongAndTime.values()
    yTime = list(performanceFreqAndTime.keys())
    y = performanceFreqAndTime.values()

    x = np.array([float(curr) for curr in x])
    y = np.array([float(curr) for curr in y])

    return lcssAndDTW(x, y, xTime, yTime, songName, newMicSOngName)



def getClosestElementsWIthIndices(dtwElementsInfo, startingIndex, endingIndex, xOrY):
    if xOrY == "x":
        idx = 0
    else:
        idx = 1
    startingSec = 0
    endingSec = 0
    if xOrY is "x":
        for element, value in dtwElementsInfo.items():
            if element[idx] >= startingIndex:
                startingSec = value.xTime
                break
        for element, value in dtwElementsInfo.items():
            if element[idx] >= endingIndex:
                endingSec = value.xTime
                break
    else:
        for element, value in dtwElementsInfo.items():
            if element[idx] >= startingIndex:
                startingSec = value.yTime
                break
        for element, value in dtwElementsInfo.items():
            if element[idx] >= endingIndex:
                endingSec = value.yTime
                break

    return startingSec, endingSec



def showGraphFromOldPerformance(songName, performanceId):
    origData: FileData = getDataFromFile(songName)
    oringFreqs = origData.getFrequencies()
    origSecs = origData.getSecondsList()
    # performanceFreqs, performanceSecs = getPassedSongFreqsAndSeconds(songName, performanceId)
    # dtwPath = getPassedSongDTWPath(songName, performanceId)
    # alignedDTWBarPlot(performanceFreqs, oringFreqs, dtwPath)




