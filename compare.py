from difflib import SequenceMatcher

import numpy as np
from fastdtw import fastdtw
from matplotlib import pyplot as plt
from dtaidistance import dtw_visualisation as dtwvis, dtw
from dtwParallel import dtw_functions
from dtwalign import dtw as dtwAlignFunc

from filesAccess import getDataFromFile, FileData
import scipy.spatial.distance as d
from tslearn import metrics


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




# LCSS LOOKS GOOD  !!!! , works better than dtw
# https://tslearn.readthedocs.io/en/stable/auto_examples/metrics/plot_lcss.html#sphx-glr-auto-examples-metrics-plot-lcss-py:~:text=Longest%20Common%20Subsequence%C2%B6
def lcssAndDTW(x, y, xTime, yTime):
    # Do I need to normalize it? yse a scaler like the example from the link?

    # Calculate DTW path and similarity
    dtw_path, sim_dtw = metrics.dtw_path(x, y, sakoe_chiba_radius=1)

    # Plotting
    #plt.figure(figsize=(8, 8))

    #lcssPlot(x, y, xTime, yTime)

    plt.figure(figsize=(8, 8))
    plt.plot(x, "r-", label='First time series')
    plt.plot(y, color='black', linestyle='--', label='Second time series')

    for positions in dtw_path:
        plt.plot([positions[0], positions[1]],
                 [x[positions[0]], y[positions[1]]], color='orange')

    print("DTW PATH")
    printNotesMatches(x, y, dtw_path, xTime, yTime)

    plt.legend()
    plt.title("Time series matching with DTW")

    plt.tight_layout()
    plt.show()

    x_path = [i[0] for i in dtw_path]
    y_path = [i[1] for i in dtw_path]


    plt.plot(x[x_path], label="mic (x)")
    plt.plot(y[y_path], label="original (y)")
    plt.legend()
    plt.title("Matching with DTW, Aligned Graphs")
    plt.show()


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
