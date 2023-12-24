# apt install libasound2-dev portaudio19-dev libportaudio2 libportaudiocpp0 ffmpeg
# pip install PyAudio
# pip install sounddevice
# pip install moviepy
# pip install keyboard
# pip install matplotlib
# https://github.com/Marcuccio/Musical-note-detector/tree/master
import math
import threading
import numpy as np
from matplotlib import pyplot as plt
from moviepy.audio.io.AudioFileClip import AudioFileClip
from scipy.signal import fftconvolve
from numpy import argmax, diff
import time
import wave
import pyaudio
import keyboard
import tkinter as tk

from filesAccess import saveToFile, getDataFromFile, checkIfSongDataExists, getSongWavPath
from compare import compareDicts

class OutOfTune:
    def __init__(self):
        self.sampleCounter = 0
        self.detectedWavNotesDict = dict() # key = sample number , value = freq
        self.dictFromMic = dict()
        self.RATE_MIC = 48000
        self.time_to_proccess = 0.2       #time of each sample...
        self.BUFFERSIZE = int(self.RATE_MIC * self.time_to_proccess)
        self.FORMAT = pyaudio.paInt16
        self.soundgate = 19
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
        self.time_data = []  # for the graph
        self.frequency_data = []
        self.start_time = 0  # time.time()
        self.pn_len = 3
        self.pn_arr = [None for x in range(self.pn_len)]
        self.pn_single = 'C1'
        self.pn_ptr = 0
        self.curr_acap = "mary.wav"  # will be extended to more than one acapella

        # Setting for the timer window
        self.root = None
        self.label = None
        self.start_button = None
        self.stop_button = None
        self.setTimerWindowButtons()

        self.start_flag = False
        self.stop_flag = False

    def stop_timer(self):
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
        self.time_data.append(elapsed_time)
        return round(elapsed_time, 3)

        #lines below for a pretty print
        # Convert the elapsed time to a formatted string
        #elapsed_seconds = int(elapsed_time % 60)
        #elapsed_milliseconds = int((elapsed_time - elapsed_seconds) * 1000)
        #elapsed_minutes = int(elapsed_time // 60)
        #return f"{elapsed_minutes}:{elapsed_seconds:02}:{elapsed_milliseconds:03}"

    # callback with timestamp (mic)
    def callback_mic(self, in_data, frame_count, time_info, status_flags, compareBool, notesDict, recordingLenSeconds,
                     user_settings):
        # time_info - to access the timing information
        # Check status_flags for any errors or termination conditions
        # raw_data_signal = np.fromstring( in_data,dtype= np.int16 )
        raw_data_signal = np.frombuffer(in_data, dtype=np.int16)

        if not self.start_flag:     #if the timer hadn't been started
            return raw_data_signal, pyaudio.paContinue

        signal_level = round(abs(self.loudness(raw_data_signal)), 2)  #### find the volume from the audio
        try:
            frameRate = self.RATE_MIC
            inputnote = round(self.freq_from_autocorr(raw_data_signal, frameRate), 2)  #### find the freq from the audio

        except:
            inputnote = 0
        if inputnote > self.frequencies[len(self.tunerNotes) - 1]:
            return raw_data_signal, pyaudio.paContinue
        if inputnote < self.frequencies[0]:
            return raw_data_signal, pyaudio.paContinue
        if signal_level > self.soundgate:
            return raw_data_signal, pyaudio.paContinue
        targetNote = self.closest_value_index(self.frequencies, round(inputnote, 2))

        # diff = calculate_Diff_Percentage_From_Original(inputNote, timestamp)
        # print('diff =   %',diff)
        self.frequency_data.append(inputnote)
        elapsed_time = self.calcTime()

        # 1. Update previous notes array
        curr_note = self.tunerNotes[self.frequencies[targetNote]]
        self.pn_arr[self.pn_ptr] = curr_note
        self.pn_ptr = (self.pn_ptr + 1) % self.pn_len


        self.dictFromMic[elapsed_time] = self.frequencies[targetNote]

        # 2. Check if all pn_arr are the same as the singed (by user) note, to make sure it is singed long enough
        if self.sameAsPrevNote(curr_note):

            # 3a. If needed- announce Note Change
            if self.pn_single != curr_note:
                #print('\t\t\t', self.pn_single, '   - >   ', curr_note)
                self.pn_single = curr_note

            # 3b. Get singer frequency from acapella ${curr_acap} at the exact moment ${elapsed_time_str}
            # singer_note = getSingerNote(elapsed_time_str)

            # 3c. compare to find the mistake in percentage
            # err_percentage = self.calculate_Diff_Percentage_From_Original(curr_note, elapsed_time_str)

        # Print the note with the elapsed time and error percentage
        print(f"{elapsed_time}: {curr_note}")

        return in_data, pyaudio.paContinue

    # callback with timestamp (wav)
    def callback_wav(self, in_data, frame_count, time_info, status_flags, user_settings):
        # time_info - to access the timing information
        # Check status_flags for any errors or termination conditions
        # raw_data_signal = np.fromstring( in_data,dtype= np.int16 )
        raw_data_signal = np.frombuffer(in_data, dtype=np.int16)
        signal_level = round(abs(self.loudness(raw_data_signal)), 2)  #### find the volume from the audio

        self.sampleCounter += 1
        # Some samples may fail. so we need to count the samples from here and only save in the dict the valid samples

        try:
            # inputnote = round(self.freq_from_autocorr(raw_data_signal, self.RATE), 2) # find the freq from the audio
            frameRate = user_settings['sample_rate']  # frameRate changes can lead to different notes
            inputnote = round(self.freq_from_autocorr(raw_data_signal, frameRate), 2)  # find the freq from the audio
        except:
            inputnote = 0
        if inputnote > self.frequencies[len(self.tunerNotes) - 1]:
            return raw_data_signal, pyaudio.paContinue
        if inputnote < self.frequencies[0]:
            return raw_data_signal, pyaudio.paContinue
        if signal_level > self.soundgate:
            return raw_data_signal, pyaudio.paContinue

        targetnote = self.closest_value_index(self.frequencies, round(inputnote, 2))
        self.frequency_data.append(inputnote)

        # Save the note sample with the index of the sample. After all the samples are taken, we will calculate the time
        # of the sample according to the index.
        self.detectedWavNotesDict[self.sampleCounter] = self.frequencies[targetnote]

        return in_data, pyaudio.paContinue

    def sameAsPrevNote(self, note):
        for i in range(self.pn_len):
            if self.pn_arr[i] != note:
                return False
        return True

    def getSingerNote(self, timestr):
        return 0  # TO-DO: Implement this function (Can be done once WAVs can be scanned with no time errors)

    def calculate_Diff_Percentage_From_Original(self, inputnote, timestr):
        return 0  # TO-DO: Implement this function (Can be done once getSingedNote is finished)

    def open_timer_thread(self):
        self.root.mainloop()  # for the timerWindow and main window

    def start_timer(self):
        print("Timer is starting")
        self.start_flag = True
        self.start_time = time.time()
        timer_thread = threading.Thread(target=self.display_timer)
        timer_thread.start()

    def read_from_mic(self):

        compareBool, notesDict, recordingLenSeconds, duration_to_process = oot.getNameOfSongFromInput()

        bufferSize = self.BUFFERSIZE
        if compareBool:
            print("Comparing to a song!")
            # ensure the time between each note printed is the same as the archived version!
            bufferSize = int(self.RATE_MIC * duration_to_process)


        pa = pyaudio.PyAudio()
        stream = pa.open(
            format=self.FORMAT,
            channels=1,
            rate=self.RATE_MIC,
            output=False,
            input=True,
            frames_per_buffer=bufferSize,
            stream_callback=lambda in_data, frame_count, time_info, status_flags:
            self.callback_mic(in_data, frame_count, time_info, status_flags,
                              compareBool, notesDict, recordingLenSeconds, user_settings=None))  # Modify this line
        # stream_callback=self.callback_mic)

        stream.start_stream()

        oot.open_timer_thread()

        # # I don't think this lines work... it is not useful
        # while not self.stop_flag:
        #     if self.stop_flag:
        #         break  # Break out of the loop if the stop flag is set
        #     time.sleep(0.1)

        #Gets here after the stop button is pushed!
        print("Recording stopped")

        print("From here we need to compare the 2 dicts")
        compareDicts(notesDict, self.dictFromMic)


        stream.stop_stream()
        stream.close()
        pa.terminate()

    # Function to stop the streaming and display the graph
    def stop_and_display_graph(self):
        global stop_streaming
        stop_streaming = True
        plt.figure(figsize=(12, 6))
        plt.plot(self.time_data, self.frequency_data)
        plt.xlabel('Time (seconds)')
        plt.ylabel('Frequency (Hz)')
        plt.title('Time vs. Frequency')
        plt.grid(True)
        plt.show()

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

    def check_space_key(self):
        while True:
            if keyboard.is_pressed('space'):
                self.stop_timer()
                break
            time.sleep(0.1)

    def read_from_wav(self, file, printGraph):
        # Increase the CHUNK is lowering the sampling rate
        # CHUNK = 4096  # if its 4096 it works good for mary and not for retroGame. If its 512 it works for both, but
        # for mary.wav it's a lot of samples. in 512 it's not working for vincent. Why?

        wf = wave.open(file, 'rb')

        # CHUNK represents the number of frames read at a time from the audio file
        # wf.getframerate() is number of frames per second.
        CHUNK = int(wf.getframerate() * self.time_to_proccess)

        data = wf.readframes(CHUNK)
        while data != b'':
            data = wf.readframes(CHUNK)  # it should be at the end of the while?
            settings = {'sample_rate': wf.getframerate()}
            self.callback_wav(data, 256, 0, 0,
                              settings)  # if some note-recognizing problems occur set the 2nd param to 512 or 1024
            # or 2048 or ...

        songName = file.split('/')[-1].split('.')[0]

        secondsList, freqList, recordingLenSeconds = self.calcNotesWithTime(wf)
        #Commented only to debug faster, remove comment...
        #saveToFile(songName, secondsList, freqList, self.sampleCounter, recordingLenSeconds, self.time_to_proccess)

        if printGraph:
            self.plotGraphWav(secondsList, freqList)

    def calcNotesWithTime(self, wf):
        # Calculate samples taken and convert to time:
        samplesCounter = self.sampleCounter
        recordingLenSeconds = wf.getnframes() / wf.getframerate()
        timeOfEachSample = recordingLenSeconds / samplesCounter

        # ADDED print(f"wf.getnframes() : {wf.getnframes()},  wf.getframerate(): {wf.getframerate()}")  #From where
        # are those numbers?
        print(f"Num of Samples: my calc: {samplesCounter}")
        print("Time of recording: ", recordingLenSeconds)
        print(f"Time of each samples: {timeOfEachSample}")

        # ADDED
        for currTime in self.detectedWavNotesDict:
            elapsed_time_str = self.calcTimeForWav(currTime * timeOfEachSample)
            freq = self.detectedWavNotesDict[currTime]
            currNote = self.tunerNotes[freq]
            print(f"{elapsed_time_str}: {currNote}")

        # ADDED
        # Remove from comment when the samples rate is Smaller
        secondsList = [round(key * timeOfEachSample, 3) for key in self.detectedWavNotesDict]

        return secondsList, self.detectedWavNotesDict.values(), recordingLenSeconds


    def plotGraphWav(self, xTime, yFreq):
        fig = plt.figure(figsize=(18, 6))
        ax = fig.add_subplot(111)
        ax.plot(xTime, yFreq)

        plt.xlabel('Time (s)')
        plt.ylabel('Frequency (Hz)')
        plt.title('Time vs. Frequency')
        plt.grid(True)
        yAxis = list(yFreq)
        plt.yticks(yAxis)
        ax.set_yticklabels([self.tunerNotes[y] + f" ({str(y)}Hz) " for y in yAxis])
        plt.show()

    def calcTimeForWav(self, elapsed_time):
        elapsed_seconds = int(elapsed_time % 60)
        elapsed_minutes = int(elapsed_time // 60)
        elapsed_milliseconds = int(((elapsed_time - elapsed_seconds) % 60) * 1000)
        return f"{elapsed_minutes}:{elapsed_seconds:02}:{elapsed_milliseconds:03}"


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
            return False, None, 0
        if checkIfSongDataExists(songName.lower()):
            recordingLenSeconds, freqDict, duration_to_process = getSongData(songName, False)
            return True, freqDict, recordingLenSeconds, duration_to_process
        else:
            print("Song does not exists!")
            return False, None, 0, -1


def getSongData(file, printBool):
    songName = file.split('.')[0]


    # If the song hadn't been analyzed
    if not checkIfSongDataExists(songName):
        wavPath = getSongWavPath(file)
        oot.read_from_wav(wavPath, printBool)

    sampleCounter, recordingLenSeconds, freqDict, duration_to_process = getDataFromFile(songName)
    print("Got data from file")
    return recordingLenSeconds, freqDict, duration_to_process


if __name__ == "__main__":
    oot = OutOfTune()
    oot.read_from_mic()

    printGraph = False

    #getSongData("Lewis Capaldi - Someone You Loved  ! v=HbVf4eaT9eg.wav", printGraph)
    #getSongData("mary.wav", printGraph)
    #getSongData("ed sheeran perfect !.wav", printGraph)

















    # def convertMp3ToWav(self, input_file):
    #     inputName = input_file[:-4]
    #     output_file = "C:/Fun projects/testingMusicalProject/" + inputName + ".wav"
    #
    #     # # convert mp3 file to wav file
    #     inputWithPath = "C:/Fun projects/testingMusicalProject/" + input_file
    #     # sound = AudioSegment.from_mp3(inputWithPath)
    #     # sound.export(output_file, format="wav")
    #
    #     # subprocess.call(['ffmpeg', '-i', input_file, output_file])
    #
    # def convertMp3ToWav2(self, input_mp3):
    #
    #     # Output WAV file path
    #     output_wav = input_mp3[:-4] + ".wav"
    #
    #     # Load the MP3 file as a video clip (audio only)
    #     clip = AudioFileClip(input_mp3)
    #
    #     # Write the audio to a WAV file
    #     clip.write_audiofile(output_wav)

