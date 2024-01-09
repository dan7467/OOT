from difflib import SequenceMatcher

import numpy as np
from fastdtw import fastdtw
from matplotlib import pyplot as plt
from dtaidistance import dtw_visualisation as dtwvis, dtw
from dtwParallel import dtw_functions
from dtwalign import dtw as dtwAlignFunc

# from shapedtw.shapedtw import shape_dtw
# from shapedtw.shapeDescriptors import SlopeDescriptor, PAADescriptor, CompoundDescriptor
# from shapedtw.dtwPlot import dtwPlot
from filesAccess import getDataFromFile, FileData
import scipy.spatial.distance as d
from tslearn.preprocessing import TimeSeriesScalerMeanVariance
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


#https://docs.python.org/3/library/difflib.html#:~:text=4%2C%20size%3D0)%5D-,get_opcodes()%C2%B6,-Return%20list%20of
def compareStrings(micString, archivedString):
    # a = "qabxcd"
    # b = "abycdf"
    # s = SequenceMatcher(None, a, b)
    # for tag, i1, i2, j1, j2 in s.get_opcodes():
    #     print('{:7}   a[{}:{}] --> b[{}:{}] {!r:>8} --> {!r}'.format(
    #         tag, i1, i2, j1, j2, a[i1:i2], b[j1:j2]))

    s = SequenceMatcher(None, archivedString, micString)
    #isNum = lambda x: x in {'1', '2', '3', '4', '5', '6', '7', '8', '9'}
    #s = SequenceMatcher(isNum, archivedString, micString) #this is supposed to ignore the numbers, don't work so well
    for tag, i1, i2, j1, j2 in s.get_opcodes():
        print('{:7}   archived[{}:{}] --> mic[{}:{}] {!r:>8} --> {!r}'.format(
            tag, i1, i2, j1, j2, archivedString[i1:i2], micString[j1:j2]))
    return


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


# Slow
# Only return graph
# https://discord.com/channels/1183328278983999579/1184833831686111365/1186586000865108028
def dtwParallelTest(x, y):  # Slow

    # Calculate DTW and get visualization
    result = dtw_functions.dtw(x, y, get_visualization=True)

    print(result)


def printNotesMatches(x, y, path):
    matched0 = [position[0] for position in path]
    notMatched0 = [i for i in range(matched0[-1]) if i not in matched0]

    matched1 = [position[1] for position in path]
    notMatched1 = [i for i in range(matched1[-1]) if i not in matched1]

    print("\nMatched notes\n")

    # print the matches of lcss
    for positions in path:
        print(f'x[{positions[0]}] = {x[positions[0]]} , {y[positions[1]]} = y[{positions[1]}]')

    print("\nUnmatched notes\n")

    [print(f"Note X[{i}]={x[i]} is not matched") for i in notMatched0]
    print("\n")
    [print(f"Note Y[{i}]={y[i]} is not matched") for i in notMatched1]




# LCSS LOOKS GOOD  !!!! , works better than dtw
# https://tslearn.readthedocs.io/en/stable/auto_examples/metrics/plot_lcss.html#sphx-glr-auto-examples-metrics-plot-lcss-py:~:text=Longest%20Common%20Subsequence%C2%B6
def lcssAndDTW(x, y):
    # Do I need to normalize it? yse a scaler like the example from the link?

    # Calculate LCSS path and similarity
    lcss_path, sim_lcss = metrics.lcss_path(x, y)
    # lcss_path, sim_lcss = metrics.lcss_path(x, y, eps=1.5)   #check what is eps

    # Calculate DTW path and similarity
    dtw_path, sim_dtw = metrics.dtw_path(x, y, sakoe_chiba_radius=1)

    # Plotting
    plt.figure(figsize=(8, 8))

    plt.plot(x, "r-", label='First time series')
    plt.plot(y, color='black', linestyle='--', label='Second time series')

    for positions in lcss_path:
        plt.plot([positions[0], positions[1]],
                 [x[positions[0]], y[positions[1]]], color='orange')
    plt.legend()
    plt.title("Time series matching with LCSS")

    plt.figure(figsize=(8, 8))
    plt.plot(x, "r-", label='First time series')
    plt.plot(y, color='black', linestyle='--', label='Second time series')

    for positions in dtw_path:
        plt.plot([positions[0], positions[1]],
                 [x[positions[0]], y[positions[1]]], color='orange')

    print("DTW PATH")
    printNotesMatches(x, y, dtw_path)

    print("LCSS PATH")
    printNotesMatches(x, y, lcss_path)

    plt.legend()
    plt.title("Time series matching with DTW")

    plt.tight_layout()
    plt.show()

    x_path = [i[0] for i in dtw_path]
    y_path = [i[1] for i in dtw_path]

    plt.plot(x[x_path], label="aligned query")
    plt.plot(y[y_path], label="aligned reference")
    plt.title("Matching with DTW, Aligned Graphs")
    plt.show()


#https://htmlpreview.github.io/?https://github.com/statefb/dtwalign/blob/master/example/example.html#:~:text=Utilities-,Basic%20Usage,-%C2%B6
def dtwAlignTest(x, y):
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

    printNotesMatches(x, y, res.path)



def compareDTW(micFreq: FileData, archivedFreq: FileData):
    # I can try different distances (cosine, euclidean, norm1...)

    x = micFreq.getFrequencies()
    y = archivedFreq.getFrequencies()

    x = np.array([float(curr) for curr in x])
    y = np.array([float(curr) for curr in y])

    # fastDTWTest(x, y)
    # dtwvisTest(x, y)
    # dtwParallelTest(x, y)
    lcssAndDTW(x, y)
    #dtwAlignTest(x, y)

    return
