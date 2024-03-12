import math
from difflib import SequenceMatcher

import mplcursors as mplcursors
import numpy as np
from fastdtw import fastdtw
from matplotlib import pyplot as plt
from dtaidistance import dtw_visualisation as dtwvis, dtw
from dtwalign import dtw as dtwAlignFunc

from filesAccess import getDataFromFile, FileData
import scipy.spatial.distance as d
from tslearn import metrics

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

def compareDicts(originalDict, recordDict):
    if originalDict is None or recordDict is None:
        return -1
    if len(originalDict) == 0 or len(recordDict) == 0:
        return -1

    lastIndexComparedInOriginal = 0  # the last index I compared and got identical notes
    windowSize = 5  # to check in a window of +-n from the actual note
    timeWindow = 0.5  # I will forgive for a n seconds delay from the actual position it should be in
    delay = 0  # The delay could be because I started the song earlier/later from where I should have started
    freqDiff = 10  # We forgive if the detected note is close enough to the original one. abs(orig - detected) < n

    first = next(iter(originalDict))  # gets the first key
    second = next(iter(recordDict))  # gets the first key
    third = first - second
    delay = abs(third)

    origKeyList = list(originalDict.keys())
    origNumOfNotes = len(origKeyList)

    print("Compare here...")
    # for recordTime, recordFreq in recordDict.items():
    #     print(f'{recordTime} : {recordFreq}')
    #     originalTime = origKeyList[lastIndexComparedInOriginal]
    #     originalFreq = originalDict[originalTime]
    #     print(f'{originalTime} : {originalFreq}')
    #
    #     if abs(recordFreq - originalFreq) < freqDiff:                   #if the freq is close enough
    #         if abs(recordTime - originalTime - delay) < timeWindow:     #if the time is also close
    #             lastIndexComparedInOriginal += 1
    #     else:
    #         #check in the window for a match?
    #         1 == 1      #placeholder
    #
    #
    #     if lastIndexComparedInOriginal >= origNumOfNotes:
    #         break



# https://discord.com/channels/1183328278983999579/1184833831686111365/1186322859036000437
def fastDTWTest(x, y):
    # distance, path = fastdtw(x, y, dist=d.euclidean)
    distance, path = fastdtw(x, y, dist=d.cosine)
    print(f"Distance: {distance}")
    print(f"Path: {path}")

    for (i, j) in path:
        print(f"{i}: {x[i]}, {j}: {y[j]}")


# https://discord.com/channels/1183328278983999579/1184833831686111365/1186323274964148295
def dtwvisTest(x, y):
    fig, ax = plt.subplots(2, 1, figsize=(1280 / 96, 720 / 96))

    # path = dtw.warping_path(x, y)
    path = dtw.warping_path(x, y, window=1)

    # Print matched points along the DTW alignment path
    print("Matched Points:")
    for point in path:
        mic_idx, arc_idx = point
        print(f"Microphone[{mic_idx}]={x[mic_idx]} - {y[arc_idx]}=Archive[{arc_idx}]")

    dtwvis.plot_warping(x, y, path, fig=fig, axs=ax)
    ax[0].set_title('Microphone Version')
    ax[1].set_title('Archived Version')
    fig.tight_layout()
    plt.show()


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


def firstDTWGraph(x, y, dtw_path):
    plt.figure(figsize=(8, 8))
    plt.plot(x, "r-", label='First time series')
    plt.plot(y, color='black', linestyle='--', label='Second time series')

    for positions in dtw_path:
        plt.plot([positions[0], positions[1]],
                 [x[positions[0]], y[positions[1]]], color='orange')
    plt.legend()
    plt.title("Time series matching with DTW")

    plt.tight_layout()
    plt.show()


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

    plt.show()
    plt.savefig("Aligned Graphs.png")

#Remove duplicate indices from the mic version, so there will be only NUM to NUM match, not NUMS to NUM!
def removeDuplicatesFromXPath(x, y, dtw_path):
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

    # Update the DTW path with the selected y indices
    dtw_path = [(x_idx, x_to_y_mapping[x_idx]) for x_idx in x_to_y_mapping]

    # # Update x and y sequences based on the updated DTW path
    # x = [x[i] for i, _ in dtw_path]
    # y = [y[j] for _, j in dtw_path]


    return np.array(x), np.array(y), dtw_path



# LCSS LOOKS GOOD  !!!! , works better than dtw
# https://tslearn.readthedocs.io/en/stable/auto_examples/metrics/plot_lcss.html#sphx-glr-auto-examples-metrics-plot-lcss-py:~:text=Longest%20Common%20Subsequence%C2%B6
def lcssAndDTW(x, y, xTime, yTime):
    # Do I need to normalize it? yse a scaler like the example from the link?

    # Calculate DTW path and similarity
    dtw_path, sim_dtw = metrics.dtw_path(x, y, sakoe_chiba_radius=1)

    # Plotting
    #plt.figure(figsize=(8, 8))
    #lcssPlot(x, y, xTime, yTime)

    #firstDTWGraph(x, y, dtw_path)


    print("DTW PATH")
    printNotesMatches(x, y, dtw_path, xTime, yTime)

    #alignedDTWGraph(x, y, dtw_path)

    x, y, dtw_path = removeDuplicatesFromXPath(x, y, dtw_path)

    alignedDTWBarPlot(x, y, dtw_path)



def lcssPlot(x, y, xTime, yTime):
    # Calculate LCSS path and similarity
    lcss_path, sim_lcss = metrics.lcss_path(x, y)
    #This is with times
    # plt.plot(xTime, x, "r-", label='First time series')
    # plt.plot(yTime, y, color='black', linestyle='--', label='Second time series')
    # for positions in lcss_path:
    #     plt.plot([xTime[positions[0]], yTime[positions[1]]],
    #              [x[positions[0]], y[positions[1]]], color='orange')

    plt.plot(x, "r-", label='First time series')
    plt.plot(y, color='black', linestyle='--', label='Second time series')
    for positions in lcss_path:
        plt.plot([positions[0], positions[1]],
                 [x[positions[0]], y[positions[1]]], color='orange')

    plt.legend()
    plt.title("Time series matching with LCSS")

    print("LCSS PATH")
    printNotesMatches(x, y, lcss_path, xTime, yTime)


#https://htmlpreview.github.io/?https://github.com/statefb/dtwalign/blob/master/example/example.html#:~:text=Utilities-,Basic%20Usage,-%C2%B6
def dtwAlignTest(x, y, xTime, yTime):
    res = dtwAlignFunc(x, y)
    print("dtw distance: {}".format(res.distance))
    print("dtw normalized distance: {}".format(res.normalized_distance))

    #res.plot_path()

    # warp both x and y by alignment path
    x_path = res.path[:, 0]
    y_path = res.path[:, 1]
    plt.plot(x[x_path], label="aligned query")
    plt.plot(y[y_path], label="aligned reference")
    plt.legend()
    plt.show()

    printNotesMatches(x, y, res.path, xTime, yTime)



def compareDTW(micFreq: FileData, archivedFreq: FileData):
    # I can try different distances (cosine, euclidean, norm1...)

    x = micFreq.getFrequencies()
    xTime = micFreq.getSecondsList()
    y = archivedFreq.getFrequencies()
    yTime = archivedFreq.getSecondsList()

    x = np.array([float(curr) for curr in x])
    y = np.array([float(curr) for curr in y])

    #fastDTWTest(x, y)
    #dtwvisTest(x, y)            #prints graph
    lcssAndDTW(x, y, xTime, yTime)
    #dtwAlignTest(x, y, xTime, yTime)

    return
