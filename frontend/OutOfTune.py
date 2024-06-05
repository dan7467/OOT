# apt install libasound2-dev portaudio19-dev libportaudio2 libportaudiocpp0 ffmpeg
# pip install PyAudio
# pip install sounddevice
# pip install moviepy
# pip install keyboard
# pip install matplotlib
# https://github.com/Marcuccio/Musical-note-detector/tree/master
import struct
import threading
from collections import Counter

import crepe
from scipy.io import wavfile
from scipy.signal import fftconvolve
from numpy import argmax, diff
import time
import tkinter as tk

from frontend.VirtualPiano import VirtualPiano

from compare import *
from filesAccess import *


class OutOfTune:
    def __init__(self, userName):
        #
        self.sampleCounter = 0
        self.detectedWavNotesDict = dict()  # key = sample number , value = freq
        self.dictFromMic = dict()

        self.rate_mic = 16000
        self.TIME_TO_PROCESS = 0.1  # time of each sample...
        self.buffer_size = int(self.rate_mic * self.TIME_TO_PROCESS)

        # self.rate_mic = 44000
        # self.buffer_size = 4096  #= CHUNK size
        # self.TIME_TO_PROCESS = self.buffer_size / self.rate_mic

        # if we want to do time_to_process = 0.25s then we need (buffer_size)4096/16,000(RATE) ~ 0.25

        self.MIN_TIME_FOR_BREAK = 3  # if there is distance of more than this between 2 notes, we put 0 between them
        # for example: 5:20 - D , 5:30 - D , 5:44 - D , 7:44 - C  -> 5:20 - D , 6:44 - 0 , 7:44 - C
        self.FORMAT = pyaudio.paInt16
        self.soundGate = 19
        self.tunerNotes = {65.41: 'C2', 69.30: 'C#2', 73.42: 'D2', 77.78: 'D#2',
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
        self.frequencies = np.array(sorted(self.tunerNotes.keys()))
        self.start_time = 0

        # Setting for the timer window
        self.root = None
        self.label = None
        self.start_button = None
        self.stop_button = None
        self.deleteCurrRecording_button = None
        self.setTimerWindowButtons()

        self.start_flag = False
        self.stop_flag = False
        self.recorded_frames_crepe = []
        self.stream = None
        self.pa = None
        self.matchingToSongBool = False
        self.TIME_DIFF = 0
        self.CONFIDENCE_LEVEL = 0.9
        # self.CREPE_STEP_SIZE = 30   #in milliseconds
        self.CREPE_STEP_SIZE = int(
            self.TIME_TO_PROCESS * 1000)  # if the time to process is 0.1 then step size is 100 ms
        # check if it should be hard coded ot dynamic
        self.songName = ""
        self.newMicSOngName = ""
        self.origWAVName = ""
        self.currFileData = None
        self.piano = self.createPiano(self.root)
        self.TIME_UNTIL_FIRST_NOTE_MIC = 6  # This version of the piano, the real notes from mic starts from second 6
        self.errorOccurred = False
        self.aborted = False

        self.dbAccess = DBAccess(userName)
        self.comparedSongs = None

        self.stream_playback = None
        self.p_playback = None

    def createPiano(self, root):
        piano = VirtualPiano(root, width=1600, height=800)  # Adjust width here
        piano.pack(fill=tk.BOTH, expand=True)
        return piano

    def freqToNote(self, freq):
        if freq == 0:
            return '0'
        return self.tunerNotes[freq]

    def start_timer(self):
        # print("Buffer size: ", self.buffer_size)
        # print("Rate: ", self.rate_mic)
        # print("Time of each chunk: ", self.buffer_size / self.rate_mic)
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

        audio_thread = threading.Thread(target=self.play_audio, args=(self.songName,))
        audio_thread.start()

        if self.currFileData is not None:
            # start the notes displayed from here!
            freqDict = self.currFileData.notesDict
            notesDict = self.transformFreqsDictToNotesDict(freqDict)
            notes_sequence = self.piano.transormDictToTuples(notesDict)
            self.piano.display_notes_sequence3(notes_sequence)

    # Define a function to play the WAV file
    def play_audio(self, songName):
        time.sleep(4)    #The notes are starting some time after the start button is pressed, check how much exactly
        path = getSongWavPath(songName) + ".wav"
        if not checkIfFileExists(path):
            print("file not found")
            return
        with wave.open(path, 'r') as wav:
            self.p_playback = pyaudio.PyAudio()
            self.stream_playback = self.p_playback.open(format=self.p_playback.get_format_from_width(wav.getsampwidth()),
                            channels=wav.getnchannels(),
                            rate=wav.getframerate(),
                            output=True)
            try:
                while not self.stop_flag:
                    data = wav.readframes(1024)
                    if data == b'':
                        break

                    sample_width = wav.getsampwidth()
                    data = self.adjust_volumeWAV(data, sample_width, 0.2)

                    # Reduce the volume by 50%
                    self.stream_playback.write(data)
            except:
                print("error in playback")
            # self.stream_playback.stop_stream()
            # self.stream_playback.close()
            # self.p_playback.terminate()

    def adjust_volumeWAV(self, frames, sample_width, volume):
        # Determine the format string based on sample width
        if sample_width == 1:
            fmt = "{}B".format(len(frames))  # Unsigned char
            scale = volume * 128 + 128
        elif sample_width == 2:
            fmt = "{}h".format(len(frames) // 2)  # Short
            scale = volume
        elif sample_width == 4:
            fmt = "{}i".format(len(frames) // 4)  # Int
            scale = volume
        else:
            raise ValueError("Unsupported sample width")

        # Unpack the frames
        samples = struct.unpack(fmt, frames)

        # Adjust volume
        samples = [int(sample * scale) for sample in samples]

        # Pack the samples back into binary data
        return struct.pack(fmt, *samples)

    def transformFreqsDictToNotesDict(self, freqDict):
        newDict = dict()
        for currTime, freq in freqDict.items():
            newDict[currTime] = self.freqToNote(freq)
        return newDict

    def stop_timer(self):
        try:
            self.stream.stop_stream()
            self.stream.close()
            self.pa.terminate()

            self.stream_playback.stop_stream()
            self.stream_playback.close()
            self.p_playback.terminate()

        except:
            print("error")
            self.errorOccurred = True
        finally:
            self.root.quit()
            if self.recorded_frames_crepe:
                self.save_in_wav(self.recorded_frames_crepe)

            self.stop_flag = True  # Set stop flag to True to stop the microphone input loop

    def abortRecordingAndTimer(self):
        self.dictFromMic = {}
        self.recorded_frames_crepe = []
        try:
            self.stream.stop_stream()
            self.stream.close()
            self.pa.terminate()

            self.stream_playback.stop_stream()
            self.stream_playback.close()
            self.p_playback.terminate()

        except:
            print("error")
            self.errorOccurred = True
        finally:
            self.root.quit()
            self.stop_flag = True  # Set stop flag to True to stop the microphone input loop
            self.aborted = True

    # display timer in a different window
    def display_timer(self):
        try:
            while not self.stop_flag:
                elapsed_time = time.time() - self.start_time
                elapsed_minutes = int(elapsed_time // 60)
                elapsed_seconds = int(elapsed_time % 60)
                self.label.config(text=f"Elapsed Time: {elapsed_minutes:02}:{elapsed_seconds:02}")
                time.sleep(1)  # Update every second
        except:
            self.dictFromMic = {}
            self.errorOccurred = True
        finally:
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
        # print(f"{elapsed_time}: {curr_note}")

        # #Trying crepe
        # raw_data_signal = np.frombuffer(in_data, dtype=np.int16)
        # seconds, frequencies, confidence, _ = crepe.predict(raw_data_signal, self.rate_mic, step_size=20, model_capacity='tiny', verbose=0)
        #
        # reliable_indices = confidence >= 0.7
        # #reliable_confidence = confidence[reliable_indices]
        # #reliable_time = seconds[reliable_indices]
        # reliable_frequency = frequencies[reliable_indices]
        #
        # freqs = [self.tunerNotes[self.frequencies[self.closest_value_index(self.frequencies, frequency)]] for frequency in reliable_frequency]
        #
        # count = Counter(freqs)
        # most_common = count.most_common(1)  # Get the most common element and its count as a list of tuples
        # if len(most_common) == 0:
        #     most_commonNum = 0
        # else:
        #     most_commonNum = most_common[0][0]
        #
        # print(f"CREPE: {elapsed_time} : {freqs}, (most common-{most_commonNum})\n")

        self.piano.update_piano(curr_note, self.errorOccurred)

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
        try:
            self.root.mainloop()  # for the timerWindow and main window
        except:
            self.errorOccurred = True

    def read_from_mic(self, songName):
        fileData = self.getSongFileData(songName)
        #fileData = self.getNameOfSongFromInput()
        self.matchingToSongBool = type(fileData) is FileData
        self.songName = "tempMic"
        dictFromArchivedSong = None
        if self.matchingToSongBool:
            print("Comparing to a song!")
            self.currFileData = fileData
            # # ensure the time between each note printed is the same as the archived version!
            # self.rate_mic = int(fileData.sampleRate)
            # self.buffer_size = int(self.rate_mic * fileData.durationToProcess)
#            self.newMicSOngName = fileData.songName + 'Mic'
            self.newMicSOngName = fileData.songName + self.dbAccess.getUserIdStr() + generate_random_id()

            self.songName = fileData.songName
            self.origWAVName = self.newMicSOngName.split('_')[0]
            dictFromArchivedSong = fileData.notesDict
        elif type(fileData) is str:
            # self.songName = fileData + 'Mic'
            self.newMicSOngName = fileData

        # print("Sample Rate: ", self.rate_mic)

        try:
            self.errorOccurred = False
            self.open_timer_thread()
        except:
            self.errorOccurred = True

        # Gets here after the stop button is pushed!
        print("Recording stopped")

        if self.errorOccurred or self.aborted:
            print("Stopped in the middle, canceling")
        else:
            if dictFromArchivedSong is not None:
                self.adjustMicTimesAccordingToArchive(dictFromArchivedSong, self.dictFromMic)

            #print("\n\nFirst version notes")
            #self.removeDuplicatesFromDict(list(self.dictFromMic.keys()), list(self.dictFromMic.values()), False)

            # record_path = getSongWavPath(self.songName) + '.wav'
            record_path = getSongWavPath(self.newMicSOngName) + '.wav'

            # Until here we saved the recorded in a wav file, now we analyze it and save the data!

            # Trim from the wav all the unnecessary start (TIME DIFF)
            if self.TIME_DIFF > 0:
                self.trimStartOfWavFile(record_path)

            if not self.errorOccurred:
                freqsAndTime = self.read_from_wav(record_path, True, False)
                print(f'freq and time: {freqsAndTime}')

                archivedSongName = self.songName
                micSongName = self.newMicSOngName


                self.comparedSongs = compare2Songs(self.getFreqsAndTimeFromSong(archivedSongName), freqsAndTime, self.songName, self.newMicSOngName)
                performanceId = micSongName[-10:]
                songNameWithUserName = micSongName[:-10]

                dtw_lst = list(self.comparedSongs.dtwElements.keys())
                str_dtw_lst = [(str(element[0]), str(element[1])) for element in dtw_lst]
                self.dbAccess.add_performance_for_existing_user_and_song(freqsAndTime, songNameWithUserName,
                                                                         performanceId, str_dtw_lst, self.comparedSongs.score)
                #self.hearClips()
                return self.comparedSongs

    def trimStartOfWavFile(self, filePath):
        try:
            sample_rate, data = wavfile.read(filePath)

            # Calculate the number of samples to skip (4 seconds * sample rate)
            samples_to_skip = int(self.TIME_DIFF * sample_rate)

            # Trim the audio data
            trimmed_data = data[samples_to_skip:]

            # Write the trimmed data to the output WAV file
            wavfile.write(filePath, sample_rate, trimmed_data)
        except:
            self.errorOccurred = True

    def adjustMicTimesAccordingToArchive(self, dictFromArchivedSong, dictFromMic):
        firstArchivedTime = self.getFirstTimeOfRealNoteFromSecondVar(dictFromArchivedSong, 0)
        firstMicTime = self.getFirstTimeOfRealNoteFromSecondVar(dictFromMic, self.TIME_UNTIL_FIRST_NOTE_MIC)
        self.TIME_DIFF = round(firstMicTime - firstArchivedTime, 3)

        newMicDict = dict()
        for sec, freq in dictFromMic.items():
            if sec > self.TIME_UNTIL_FIRST_NOTE_MIC:
                newTime = round(sec - self.TIME_DIFF, 3)
                if newTime > 0:
                    newMicDict[newTime] = freq

        self.dictFromMic = newMicDict

    @staticmethod
    def getFirstTimeOfRealNoteFromSecondVar(dict1, startingFromSecond):
        for sec, freq in dict1.items():
            if freq != 0 and sec > startingFromSecond:
                return sec
        return 0

    def save_in_wav(self, frames):
        # file_path = getSongWavPath(self.songName) + '.wav'
        file_path = getSongWavPath(self.newMicSOngName) + '.wav'
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

    def removeDuplicatesFromDict(self, seconds, freqs, crepeBool):
        result = dict()
        time_for_each_chunk = 0.1  # the time of each chunk (in seconds) (in this time we take the majority pitch)

        # if we decided that the Time_to_process is large enough we don't need to do majority vote
        if self.TIME_TO_PROCESS * 2 > time_for_each_chunk:
            chunk_size = 1
        else:
            if crepeBool:
                chunk_size = int(time_for_each_chunk / (self.CREPE_STEP_SIZE * 0.001))
            else:
                chunk_size = int(time_for_each_chunk / self.TIME_TO_PROCESS)

        # example : step_size = 20 (its in ms) and we want the chunk to hold data of 0.1 seconds,
        # so the size will be  0.1 / 0.001*20 = 5
        lastSecond = 0
        lastFreq = 0
        freqsLen = len(freqs)
        for i in range(0, freqsLen, chunk_size):
            endIndex = min(i + chunk_size, freqsLen - 1)  # so it will not overflow

            chunkFreqs = freqs[i:endIndex]
            chunkFreqs = [self.frequencies[self.closest_value_index(self.frequencies, curr)] for curr in chunkFreqs]

            # Count occurrences of each element in the list
            element_counts = Counter(chunkFreqs)

            # Get the element with the maximum occurrence
            mostCommon = element_counts.most_common(1)
            if len(mostCommon) == 0:
                continue
            currFreq = mostCommon[0][0]
            currSecond = (seconds[i] + seconds[endIndex]) / 2

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

        # plt.plot(result.keys(), result.values())
        # plt.title("After chunk filtering")
        # plt.legend()
        # plt.show()
        # plt.savefig("FilteredGraph")

        return result

    def read_from_wav(self, fileName, printGraph, saveFile):
        try:
            songName = fileName.split('/')[-1].split('.')[0]
            sr, y = wavfile.read(fileName)
            seconds, frequency, confidence, _ = self.runCrepePrediction(y, sr)
            # Filter out frequencies with confidence below 0.5
            reliable_indices = confidence >= self.CONFIDENCE_LEVEL
            reliable_confidence = confidence[reliable_indices]
            reliable_time = seconds[reliable_indices]
            reliable_frequency = frequency[reliable_indices]
            if printGraph:
                self.plotGraphWav(reliable_time, reliable_frequency, reliable_confidence)
            print("\n\nCrepe version notes")
            dict_filtered = self.removeDuplicatesFromDict(reliable_time, reliable_frequency, True)
            if saveFile:
                fileData = FileData(songName, self.sampleCounter, 0, round(self.TIME_TO_PROCESS, 4),
                                self.rate_mic, dict_filtered)
                saveToFile(fileData)  #TODO DELETE THIS WHEN DB IS READY, NOT SURE!!!!!

        except Exception as error:
            # handle the exception
            print("An exception occurred in read_wav:", error)  # An exception occurred: division by zero
            self.errorOccurred = True
            return None
        return dict_filtered




    # @jit(target_backend='cuda')
    def runCrepePrediction(self, y, sr):
        # Call crepe to estimate pitch and confidence
        # , viterbi=True, step_size=10
        print("Starting crepe")
        return crepe.predict(y, sr, model_capacity='large', step_size=self.CREPE_STEP_SIZE, verbose=0)

    def plotGraphWav(self, seconds, freq, confidence):

        # #Graph without confidence
        # plt.plot(seconds, freq, label='Estimated pitch (Hz)', color='blue')
        # plt.xlabel('Tims (s)')
        # plt.ylabel('Frequency (Hz)')
        # plt.title('Estimated Pitch')
        # plt.legend()
        #
        # plt.tight_layout()
        # plt.show()
        # plt.savefig('wavGraph.png')

        # two separate plots for estimated pitch and confidence
        # fig, axs = plt.subplots(2, 1, figsize=(10, 8))
        #
        # # Plot the estimated pitch over time
        # axs[0].plot(seconds, freq, label='Estimated pitch (Hz)', color='blue')
        # axs[0].set_xlabel('Time (s)')
        # axs[0].set_ylabel('Frequency (Hz)')
        # axs[0].set_title('Estimated Pitch')
        # axs[0].legend()

        # # Plot the confidence over time
        # axs[1].plot(seconds, confidence, label='Confidence', color='green')
        # axs[1].set_xlabel('Time (s)')
        # axs[1].set_ylabel('Confidence')
        # axs[1].set_title('Confidence')
        # axs[1].legend()

        # Plot the estimated pitch over time
        #
        # plt.tight_layout()
        # plt.show()

        # fig.savefig('wavGraph.png')

        return

    def setTimerWindowButtons(self):
        self.root = tk.Tk()
        self.root.geometry("1600x900")  # Set window size
        self.label = tk.Label(self.root, text="", font=("Arial", 18))
        self.label.pack(expand=True)

        self.start_button = tk.Button(self.root, text="Start", command=self.start_timer)
        self.start_button.pack(expand=True)

        self.stop_button = tk.Button(self.root, text="Stop", command=self.stop_timer)
        self.stop_button.pack(expand=True)

        self.deleteCurrRecording_button = tk.Button(self.root, text="Abort", command=self.abortRecordingAndTimer)
        self.deleteCurrRecording_button.pack(expand=True)

        def on_closing():
            self.abortRecordingAndTimer()

        self.root.protocol("WM_DELETE_WINDOW", on_closing)


    def getAvailableSongs(self):
        return printAvailableSongs(self.dbAccess)

    def getSongFileData(self, songName):
        songNameWithoutUserName = songName.split('_')[0]
        if songName.lower() == 'none' or songNameWithoutUserName == '':
            return None
        if checkIfSongDataExists(songNameWithoutUserName) and self.dbAccess.checkIfSongDataExists(songName):
            fileData = getDataFromFile(songNameWithoutUserName)
            return fileData
        else:
            print("Song does not exists!")
            return songName



    def getNameOfSongFromInput(self):
        songsDict = printAvailableSongs(self.dbAccess)
        songNumOrStr = input(
            "Write the Number of the song you want to compare to, or write new name for Not comparing: ")
        if songNumOrStr in songsDict.keys():
            songName = songsDict[songNumOrStr]
        else:
            songName = songNumOrStr
        songNameWithoutUserName = songName.split('_')[0]
        if songName.lower() == 'none' or songNameWithoutUserName == '':
            return None
        if checkIfSongDataExists(songNameWithoutUserName) and self.dbAccess.checkIfSongDataExists(songName):
            fileData = getDataFromFile(songNameWithoutUserName)
            return fileData
        else:
            print("Song does not exists!")
            return songName

    def filterNoise(self, reliable_time, reliable_frequency):
        pass

    # def getShortAudioClipFromEntries(self, name, startingIndex, endingIndex, dtwElementsInfo):
    #     startingIndex = int(startingIndex)
    #     endingIndex = int(endingIndex)
    #     if name == 1:
    #         songName = self.newMicSOngName
    #         startingSecond, endingSecond = getClosestElementsWIthIndices(dtwElementsInfo, startingIndex,
    #                                                                      endingIndex, "x")
    #     else:
    #         songName = self.origWAVName
    #         startingSecond, endingSecond = getClosestElementsWIthIndices(dtwElementsInfo, startingIndex,
    #                                                                      endingIndex, "y")
    #
    #     getShortAudioClip(songName, startingSecond, endingSecond)

    # def hearClips(self):
    #     window = tk.Tk()
    #
    #     # file_label = tk.Label(window, text="File Name:")
    #     # file_label.pack()
    #     # file_name_entry = tk.Entry(window)
    #     # file_name_entry.pack()
    #
    #     starting_label = tk.Label(window, text="Starting Second:")
    #     starting_label.pack()
    #     starting_entry = tk.Entry(window)
    #     starting_entry.pack()
    #
    #     ending_label = tk.Label(window, text="Ending Second:")
    #     ending_label.pack()
    #     ending_entry = tk.Entry(window)
    #     ending_entry.pack()
    #
    #     play_button_mic = tk.Button(window, text="Play from original",
    #                                 command=lambda: self.getShortAudioClipFromEntries(2, starting_entry.get(),
    #                                                                                   ending_entry.get(), self.comparedSongs.dtwElements))
    #     play_button_orig = tk.Button(window, text="Play from mic",
    #                                  command=lambda: self.getShortAudioClipFromEntries(1,
    #                                                                                    starting_entry.get(),
    #                                                                                    ending_entry.get(),
    #                                                                                    self.comparedSongs.dtwElements))
    #     play_button_mic.pack()
    #     play_button_orig.pack()
    #
    #     def on_closing():
    #         window.destroy()
    #
    #     window.protocol("WM_DELETE_WINDOW", on_closing)
    #     window.mainloop()


    def fetchAllPerformances(self, songName):
        return self.dbAccess.fetchPerformancesFromUser(songName)

    def fetchAllSongsForUser(self):
        return self.dbAccess.fetchSongsFromUser()

    def compareOldSongs(self, archivedName, performanceObject):
        performanceId = performanceObject["_id"]
        performanceSongName = performanceObject["song_name"] + performanceId
        songData = getDataFromFile(archivedName)

        origFreqsAndSeconds = songData.notesDict
        dtw_path_str = performanceObject["dtw_lst"]
        dtw_path = [(int(x[0]), int(x[1])) for x in dtw_path_str]
        performanceFreqsAndSeconds = performanceObject["performance_notes_dict"]

        y = np.array([float(x) for x in performanceFreqsAndSeconds.values()])
        yTime = [float(x) for x in performanceFreqsAndSeconds.keys()]
        x = np.array([x for x in origFreqsAndSeconds.values()])
        xTime = [x for x in origFreqsAndSeconds.keys()]

        self.origWAVName = archivedName
        self.newMicSOngName = performanceSongName
        #alignedDTWBarPlot(x, y, dtw_path)

        infoDict = {}
        for xIdx, yIdx in dtw_path:
            infoDict[(xIdx, yIdx)] = dtwElementInfo(x[xIdx], y[yIdx], xIdx, yIdx, xTime[xIdx], yTime[yIdx])

        #self.comparedSongs = ComparedSongs(archivedName, performanceSongName, performanceObject["score"], infoDict, x, y, dtw_path)
        #self.hearClips()



    def getFreqsAndTimeFromSong(self, archivedSongName):
        dataFile = getDataFromFile(archivedSongName)
        return dataFile.notesDict


    def getSongData(self, file, printBool, oot1):
        songName = file.split('.')[0]

        # If the song hadn't been analyzed
        #if not oot1.dbAccess.checkIfSongDataExists(songName):
        # if not checkIfSongDataExists(songName):
        #     wavPath = getSongWavPath(file)
        #     oot1.read_from_wav(wavPath, printBool, True)
        #     oot1.dbAccess.addSongForUser(songName)

        wavPath = getSongWavPath(file)
        if not checkIfFileExists(wavPath):
            print("File not exists")
            return
        oot1.read_from_wav(wavPath, printBool, True)
        oot1.dbAccess.addSongForUser(songName + self.dbAccess.getUserIdStr())

        fileData = getDataFromFile(songName)
        print("Got data from file")
        return fileData


def listToString(freqList):
    result = ""
    oot = OutOfTune("Roni")
    for curr in freqList:
        result += " " + str(oot.freqToNote(float(curr)))
    return result


if __name__ == "__main__":

    # list1 = np.array([350, 329.63, 200, 261.63, 329.63, 392.00, 350, 329.63, 200, 261.63, 329.63, 392.00, 350, 329.63, 200, 261.63, 329.63, 392.00])
    # list2 = np.array([200, 329.63, 200, 261.63, 329.63, 392.00, 350, 329.63, 200, 261.63, 329.63, 392.00, 350, 329.63, 200, 261.63, 329.63, 392.00])
    # computeScore(list1, list2)
    oot = OutOfTune("Roni")

    #oot.read_from_mic()

    printGraph = True

    # getShortAudioClip("Viva La Vida 15", -1, 5)

    #getSongData("king of the world.wav", printGraph, oot)

    #dtwElements = oot.compareTest("mary", "maryMic")

    #oot.hearClips(dtwElements)
    # updated version
