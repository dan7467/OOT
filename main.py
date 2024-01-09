# apt install libasound2-dev portaudio19-dev libportaudio2 libportaudiocpp0 ffmpeg
# pip install PyAudio
# pip install sounddevice
# pip install moviepy
# pip install keyboard
# pip install matplotlib
# https://github.com/Marcuccio/Musical-note-detector/tree/master
import math
import threading

import crepe
import numpy as np
from matplotlib import pyplot as plt
from moviepy.audio.io.AudioFileClip import AudioFileClip
from scipy.io import wavfile
from scipy.signal import fftconvolve
from numpy import argmax, diff
import time
import wave
import pyaudio
import tkinter as tk

from compare import compareStrings, compareDTW
from crepeTest import testCrepe, crepePrediction
from filesAccess import saveToFile, getDataFromFile, checkIfSongDataExists, getSongWavPath, FileData


class OutOfTune:
    def __init__(self):
        self.sampleCounter = 0
        self.detectedWavNotesDict = dict()  # key = sample number , value = freq
        self.dictFromMic = dict()
        self.rate_mic = 16000
        self.TIME_TO_PROCESS = 0.1  # time of each sample...
        self.MIN_TIME_FOR_BREAK = 1.5  # if there is distance of more than this between 2 notes, we put 0 between them
        # for example: 5:20 - D , 5:30 - D , 5:44 - D , 7:44 - C  -> 5:20 - D , 6:44 - 0 , 7:44 - C
        self.buffer_size = int(self.rate_mic * self.TIME_TO_PROCESS)
        self.FORMAT = pyaudio.paInt16
        self.soundGate = 19
        self.tunerNotes = {65.41: 'C2', 69.30: 'C#2', 73.42: 'D2', 77.78: 'D#2',
                           82.41: 'E2', 87.31: 'F2', 92.50: 'F#2', 98.00: 'G2',
                           103.80: 'G#2', 110.00: 'A2', 116.50: 'Bb2', 123.50: 'B2',
                           130.80: 'C3', 138.60: 'C#3', 146.80: 'D3', 155.60: 'Db3',
                           164.80: 'E3', 174.60: 'F3', 185.00: 'F#3', 196.00: 'G3',
                           207.70: 'G#3', 220.00: 'A3', 233.10: 'Bb3', 246.90: 'B3',
                           261.60: 'C4', 277.20: 'C#4', 293.70: 'D4', 311.10: 'Eb4',
                           329.60: 'E4', 349.20: 'F4', 370.00: 'F#4', 392.00: 'G4',
                           415.30: 'G#4', 440.00: 'A4', 466.20: 'Ab4', 493.90: 'B4',
                           523.30: 'C5', 554.40: 'C#5', 587.30: 'D5', 622.30: 'Eb5',
                           659.30: 'E5', 698.50: 'F5', 740.00: 'F#5', 784.00: 'G5',
                           830.60: 'G#5', 880.00: 'A5', 932.30: 'Bb5', 987.80: 'B5',
                           1047.00: 'C6', 1109.0: 'C#6', 1175.0: 'D6', 1245.0: 'Eb6',
                           1319.0: 'E6', 1397.0: 'F6', 1480.0: 'F#6', 1568.0: 'G6',
                           1661.0: 'G#6', 1760.0: 'A6', 1865.0: 'Bb6', 1976.0: 'B6',
                           2093.0: 'C7'}
        self.frequencies = np.array(sorted(self.tunerNotes.keys()))
        self.start_time = 0

        # Setting for the timer window
        self.root = None
        self.label = None
        self.start_button = None
        self.stop_button = None
        self.setTimerWindowButtons()

        self.start_flag = False
        self.stop_flag = False
        self.recorded_frames_crepe = []
        self.stream = None
        self.pa = None
        self.matchingToSongBool = False
        self.CONFIDENCE_LEVEL = 0.9
        self.songName = ""

    def freqToNote(self, freq):
        if freq == 0:
            return '0'
        return self.tunerNotes[freq]

    def start_timer(self):
        print("Buffer size: ", self.buffer_size)
        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(
            format=self.FORMAT,
            channels=1,
            rate=self.rate_mic,
            output=False,
            input=True,
            frames_per_buffer=self.buffer_size,
            stream_callback=lambda in_data, frame_count, time_info, status_flags:
            self.callback_mic(in_data, frame_count, time_info, status_flags,
                              self.matchingToSongBool, self.rate_mic))

        self.stream.start_stream()
        print("Timer is starting")
        self.start_flag = True
        self.start_time = time.time()
        timer_thread = threading.Thread(target=self.display_timer)
        timer_thread.start()

    def stop_timer(self):
        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()
        self.root.quit()

        if self.recorded_frames_crepe:
            self.save_in_wav(self.recorded_frames_crepe)

        self.stop_flag = True  # Set stop flag to True to stop the microphone input loop

    # display timer in a different window
    def display_timer(self):
        while not self.stop_flag:
            elapsed_time = time.time() - self.start_time
            elapsed_minutes = int(elapsed_time // 60)
            elapsed_seconds = int(elapsed_time % 60)
            self.label.config(text=f"Elapsed Time: {elapsed_minutes:02}:{elapsed_seconds:02}")
            time.sleep(1)  # Update every second

        self.root.quit()

    def find(self, condition):
        res, = np.nonzero(np.ravel(condition))
        return res

    def calcTime(self):
        # Calculate the elapsed time since recording started
        elapsed_time = time.time() - self.start_time
        return round(elapsed_time, 3)

    # callback with timestamp (mic)
    def callback_mic(self, in_data, frame_count, time_info, status_flags, compareBool, sampleRate):

        self.recorded_frames_crepe.append(in_data)  # for crepe

        # raw_data_signal = np.fromstring( in_data,dtype= np.int16 )
        raw_data_signal = np.frombuffer(in_data, dtype=np.int16)

        if not self.start_flag:  # if the timer hadn't been started
            return raw_data_signal, pyaudio.paContinue

        signal_level = round(abs(self.loudness(raw_data_signal)), 2)  #### find the volume from the audio
        try:
            frameRate = sampleRate
            inputnote = round(self.freq_from_autocorr(raw_data_signal, frameRate), 2)  #### find the freq from the audio

        except:
            inputnote = 0
        if inputnote > self.frequencies[len(self.tunerNotes) - 1]:
            return raw_data_signal, pyaudio.paContinue
        if inputnote < self.frequencies[0]:
            return raw_data_signal, pyaudio.paContinue
        if signal_level > self.soundGate:
            return raw_data_signal, pyaudio.paContinue

        # inputnote = inputnote / 2    #TEMP REMOVE THIS!!!!!

        targetNote = self.closest_value_index(self.frequencies, round(inputnote, 2))

        elapsed_time = self.calcTime()

        curr_note = self.tunerNotes[self.frequencies[targetNote]]
        self.dictFromMic[elapsed_time] = self.frequencies[targetNote]

        # Print the note with the elapsed time and error percentage
        print(f"{elapsed_time}: {curr_note}")

        return in_data, pyaudio.paContinue

    # callback with timestamp (wav)
    def callback_wav(self, in_data, frame_count, time_info, status_flags, sampleRate):
        # raw_data_signal = np.fromstring( in_data,dtype= np.int16 )
        raw_data_signal = np.frombuffer(in_data, dtype=np.int16)
        signal_level = round(abs(self.loudness(raw_data_signal)), 2)  #### find the volume from the audio

        self.sampleCounter += 1
        # Some samples may fail. so we need to count the samples from here and only save in the dict the valid samples

        try:
            # inputnote = round(self.freq_from_autocorr(raw_data_signal, self.RATE), 2) # find the freq from the audio
            frameRate = sampleRate  # frameRate changes can lead to different notes
            inputnote = round(self.freq_from_autocorr(raw_data_signal, frameRate), 2)  # find the freq from the audio
        except:
            inputnote = 0
        if inputnote > self.frequencies[len(self.tunerNotes) - 1]:
            return raw_data_signal, pyaudio.paContinue
        if inputnote < self.frequencies[0]:
            return raw_data_signal, pyaudio.paContinue
        if signal_level > self.soundGate:
            return raw_data_signal, pyaudio.paContinue

        targetnote = self.closest_value_index(self.frequencies, round(inputnote, 2))

        # Save the note sample with the index of the sample. After all the samples are taken, we will calculate the time
        # of the sample according to the index.
        self.detectedWavNotesDict[self.sampleCounter] = self.frequencies[targetnote]

        return in_data, pyaudio.paContinue

    def open_timer_thread(self):
        self.root.mainloop()  # for the timerWindow and main window

    def read_from_mic(self):

        fileData = oot.getNameOfSongFromInput()
        self.matchingToSongBool = type(fileData) is FileData
        self.songName = "tempMic"
        if self.matchingToSongBool:
            print("Comparing to a song!")
            # ensure the time between each note printed is the same as the archived version!
            self.rate_mic = int(fileData.sampleRate)
            self.buffer_size = int(self.rate_mic * fileData.durationToProcess)
            self.songName = fileData.songName + 'Mic'
        elif type(fileData) is str:
            self.songName = fileData + 'Mic'

        print("Sample Rate: ", self.rate_mic)

        oot.open_timer_thread()

        # Gets here after the stop button is pushed!
        print("Recording stopped")

        print("\n\nFirst version notes")
        self.removeDuplicatesFromDict(list(self.dictFromMic.keys()), list(self.dictFromMic.values()))

        record_path = getSongWavPath(self.songName) + '.wav'

        # Until here we saved the recorded in a wav file, now we analyze it and save the data!

        self.read_from_wav(record_path, True)

    def save_in_wav(self, frames):
        file_path = getSongWavPath(self.songName) + '.wav'

        wf = wave.open(file_path, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.pa.get_sample_size(pyaudio.paInt16))
        wf.setframerate(self.rate_mic)
        wf.writeframes(b''.join(frames))
        wf.close()

    # See https://github.com/endolith/waveform-analyzer/blob/master/frequency_estimator.py
    def freq_from_autocorr(self, raw_data_signal, fs):
        corr = fftconvolve(raw_data_signal, raw_data_signal[::-1], mode='full')
        corr = corr[len(corr) // 2:]
        d = diff(corr)
        start = self.find(d > 0)[0]
        peak = argmax(corr[start:]) + start
        px, py = self.parabolic(corr, peak)
        return fs / px

    # See https://github.com/endolith/waveform-analyzer/blob/master/frequency_estimator.py
    def parabolic(self, f, x):
        xv = 1 / 2. * (f[x - 1] - f[x + 1]) / (f[x - 1] - 2 * f[x] + f[x + 1]) + x
        yv = f[x] - 1 / 4. * (f[x - 1] - f[x + 1]) * (xv - x)

        return (xv, yv)

    # def loudness(chunk):
    #     data = np.array(chunk, dtype=float) / 32768.0
    #     ms = math.sqrt(np.sum(data ** 2.0) / len(data))
    #     if ms < 10e-8: ms = 10e-8
    #
    #     return 10.0 * math.log(ms, 10.0)

    # ChatGPT Added!!
    def loudness(self, chunk):
        data = np.array(chunk, dtype=float) / 32768.0
        denominator = len(data)

        if denominator <= 0:
            # Handle the case where the denominator is zero or negative
            return float('-inf')  # Or any other appropriate value

        ms = math.sqrt(np.sum(data ** 2.0) / denominator)
        if ms < 10e-8:
            ms = 10e-8

        return 10.0 * math.log(ms, 10.0)

    def find_nearest(self, array, value):
        index = (np.abs(array - value)).argmin()
        return array[index]

    def closest_value_index(self, array, guessValue):
        # Find the closest element in the array, value wise
        closestValue = self.find_nearest(array, guessValue)
        # Find indices of closestValue
        indexArray = np.where(array == closestValue)
        # numpy 'where' returns a 2D array with the element index as the value

        return indexArray[0][0]

    def removeDuplicatesFromDict(self, seconds, freqs):
        result = dict()

        lastSecond = 0
        lastFreq = 0
        for currSecond, currFreq in zip(seconds, freqs):

            # chunk_size = 10
            # for i in range(0, len(array), chunk_size):
            #     chunk = array[i:i + chunk_size]
            #     print("Chunk", i // chunk_size + 1, ":", chunk)

            # This will take the following 10 elements
            # For them we need to round them with closest value of freq, and then choose the majority between them
            # after that we need to update the currSeconds and currFreq to be the majority Vote and the
            # time to be his time. And after this we just continue with the rest of the function

            currFreq = self.frequencies[self.closest_value_index(self.frequencies, currFreq)]
            currSecond = round(currSecond, 3)
            if currSecond - lastSecond > self.MIN_TIME_FOR_BREAK:  # silence in original song
                result[lastSecond + self.MIN_TIME_FOR_BREAK / 2] = 0
                result[currSecond] = currFreq
                lastFreq = currFreq
            elif currFreq != lastFreq:  # the note had changed
                result[currSecond] = currFreq
                lastFreq = currFreq
            # if currFreq = lastFreq we don't need to save it, because before is the same
            lastSecond = currSecond

        # print the result for debug
        print("Notes after filtering:\n")
        for second, freq in result.items():
            currNote = self.freqToNote(freq)
            print(f"{second}: {currNote}")

        return result

    def read_from_wav(self, fileName, printGraph):

        songName = fileName.split('/')[-1].split('.')[0]
        sr, y = wavfile.read(fileName)

        #save the data to file and image of the graph
        #crepe.process_file(fileName, viterbi=True, model_capacity='full', step_size=10,
        #                   save_plot=True, plot_voicing=True, save_activation=True)

        # Call crepe to estimate pitch and confidence
        seconds, frequency, confidence, _ = crepe.predict(y, sr, viterbi=True, model_capacity='full', step_size=10)

        # Filter out frequencies with confidence below 0.5
        reliable_indices = confidence >= self.CONFIDENCE_LEVEL
        reliable_confidence = confidence[reliable_indices]
        reliable_time = seconds[reliable_indices]
        reliable_frequency = frequency[reliable_indices]

        if printGraph:
            self.plotGraphWav(reliable_time, reliable_frequency, reliable_confidence)

        print("\n\nCrepe version notes")
        dict_filtered = self.removeDuplicatesFromDict(reliable_time, reliable_frequency)

        fileData = FileData(songName, self.sampleCounter, 0, self.TIME_TO_PROCESS,
                            self.rate_mic, dict_filtered)

        saveToFile(fileData)




    def plotGraphWav(self, seconds, freq, confidence):

        # Create two separate plots for estimated pitch and confidence
        fig, axs = plt.subplots(2, 1, figsize=(10, 8))

        # Plot the estimated pitch over time
        axs[0].plot(seconds, freq, label='Estimated pitch (Hz)', color='blue')
        axs[0].set_xlabel('Time (s)')
        axs[0].set_ylabel('Frequency (Hz)')
        axs[0].set_title('Estimated Pitch')
        axs[0].legend()

        # Plot the confidence over time
        axs[1].plot(seconds, confidence, label='Confidence', color='green')
        axs[1].set_xlabel('Time (s)')
        axs[1].set_ylabel('Confidence')
        axs[1].set_title('Confidence')
        axs[1].legend()

        plt.tight_layout()
        plt.show()

        fig.savefig('wavGraph.png')

        return

    def setTimerWindowButtons(self):
        self.root = tk.Tk()
        self.root.geometry("200x100")  # Set window size
        self.label = tk.Label(self.root, text="", font=("Arial", 18))
        self.label.pack(expand=True)
        self.start_button = tk.Button(self.root, text="Start", command=self.start_timer)
        self.start_button.pack(expand=True)
        self.stop_button = tk.Button(self.root, text="Stop", command=self.stop_timer)
        self.stop_button.pack(expand=True)

    def getNameOfSongFromInput(self):
        songName = input("Write the name of the song you want to compare to, or None to just use mic: ")
        if songName.lower() == 'none':
            return None
        if checkIfSongDataExists(songName):
            fileData = getSongData(songName, False)
            return fileData
        else:
            print("Song does not exists!")
            return songName

    def filterNoise(self, reliable_time, reliable_frequency):
        pass


def getSongData(file, printBool):
    songName = file.split('.')[0]

    # If the song hadn't been analyzed
    if not checkIfSongDataExists(songName):
        wavPath = getSongWavPath(file)
        oot.read_from_wav(wavPath, printBool)

    fileData = getDataFromFile(songName)
    print("Got data from file")
    return fileData


def listToString(freqList):
    result = ""
    oot = OutOfTune()
    for curr in freqList:
        result += " " + str(oot.freqToNote(float(curr)))
    return result


def compareTest():
    archivedSongData = getDataFromFile("mary")

    micSongData = getDataFromFile("maryMic")

    compareDTW(micSongData, archivedSongData)

    #micString = listToString(micSongData.getFrequencies())
    #archivedString = listToString(archivedSongData.getFrequencies())
    #compareStrings(micString, archivedString)


if __name__ == "__main__":
    oot = OutOfTune()
    #oot.read_from_mic()

    printGraph = True

    getSongData("mary.wav", printGraph)

    #compareTest()

    # audio_path = './songsWav/mary.wav'
    # audio_path = './recorded_mary.wav'
    # testCrepe(audio_path)
