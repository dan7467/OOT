# apt install libasound2-dev portaudio19-dev libportaudio2 libportaudiocpp0 ffmpeg
# pip install PyAudio
# pip install sounddevice
# pip install moviepy
# pip install keyboard
# pip instlal matplotlib

# https://github.com/Marcuccio/Musical-note-detector/tree/master
import math
import threading
import pyaudio
import numpy as np
from matplotlib import pyplot as plt
from moviepy.audio.io.AudioFileClip import AudioFileClip
from scipy.signal import fftconvolve
from numpy import argmax, diff
import time
import wave
import subprocess
import keyboard

def find(condition):
    res, = np.nonzero(np.ravel(condition))
    return res


def build_default_tuner_range():
    return {65.41: 'C2',
            69.30: 'C#2',
            73.42: 'D2',
            77.78: 'D#2',
            82.41: 'E2',
            87.31: 'F2',
            92.50: 'F#2',
            98.00: 'G2',
            103.80: 'G#2',
            110.00: 'A2',
            116.50: 'Bb2',
            123.50: 'B2',
            130.80: 'C3',
            138.60: 'C#3',
            146.80: 'D3',
            155.60: 'Db3',
            164.80: 'E3',
            174.60: 'F3',
            185.00: 'F#3',
            196.00: 'G3',
            207.70: 'G#3',
            220.00: 'A3',
            233.10: 'Bb3',
            246.90: 'B3',
            261.60: 'C4',
            277.20: 'C#4',
            293.70: 'D4',
            311.10: 'Eb4',
            329.60: 'E4',
            349.20: 'F4',
            370.00: 'F#4',
            392.00: 'G4',
            415.30: 'G#4',
            440.00: 'A4',
            466.20: 'Ab4',
            493.90: 'B4',
            523.30: 'C5',
            554.40: 'C#5',
            587.30: 'D5',
            622.30: 'Eb5',
            659.30: 'E5',
            698.50: 'F5',
            740.00: 'F#5',
            784.00: 'G5',
            830.60: 'G#5',
            880.00: 'A5',
            932.30: 'Bb5',
            987.80: 'B5',
            1047.00: 'C6',
            1109.0: 'C#6',
            1175.0: 'D6',
            1245.0: 'Eb6',
            1319.0: 'E6',
            1397.0: 'F6',
            1480.0: 'F#6',
            1568.0: 'G6',
            1661.0: 'G#6',
            1760.0: 'A6',
            1865.0: 'Bb6',
            1976.0: 'B6',
            2093.0: 'C7'
            }


RATE = 24000
BUFFERSIZE = 3072
FORMAT = pyaudio.paInt16
soundgate = 19
tunerNotes = build_default_tuner_range()
frequencies = np.array(sorted(tunerNotes.keys()))
# newSection1 STARTS HERE --------------------------------------------------------------------------------------------------------
prevNotesLen = 5
prevNotes = [ None for x in range( prevNotesLen ) ]
prevNotePtr =  0
curr_acap = "mary.wav" # will be extended to more than one acapella
# newSection1 ENDS HERE --------------------------------------------------------------------------------------------------------

time_data = []   #for the graph
frequency_data = []

def calcTime():
    if not hasattr(callback, 'start_time'):
        # Initialize the start time on the first callback
        callback.start_time = time.time()

    # Calculate the elapsed time since recording started
    elapsed_time = time.time() - callback.start_time

    time_data.append(elapsed_time)

    # Convert the elapsed time to a formatted string
    elapsed_seconds = int(elapsed_time % 60)
    elapsed_milliseconds = int((elapsed_time - elapsed_seconds) * 1000)
    elapsed_minutes = int(elapsed_time // 60)
    return f"{elapsed_minutes}:{elapsed_seconds:02}:{elapsed_milliseconds:03}"



# callback with timestamp
def callback(in_data, frame_count, time_info, status):
    # raw_data_signal = np.fromstring( in_data,dtype= np.int16 )
    raw_data_signal = np.frombuffer(in_data, dtype=np.int16)
    signal_level = round(abs(loudness(raw_data_signal)), 2)  #### find the volume from the audio
    try:
        inputnote = round(freq_from_autocorr(raw_data_signal, RATE), 2)  #### find the freq from the audio
    except:
        inputnote = 0

    if inputnote > frequencies[len(tunerNotes) - 1]:
        return (raw_data_signal, pyaudio.paContinue)
    if inputnote < frequencies[0]:
        return (raw_data_signal, pyaudio.paContinue)
    if signal_level > soundgate:
        return (raw_data_signal, pyaudio.paContinue)
    targetnote = closest_value_index(frequencies, round(inputnote, 2))

    # diff = calculate_Diff_Percentage_From_Original(inputnote, timestamp)
    # print('diff =   %',diff)

    frequency_data.append(inputnote)

    elapsed_time_str = calcTime()

    # newSection2 STARTS HERE --------------------------------------------------------------------------------------------------------

    # 1. Update previous notes array
    prevNotes[prevNotePtr] = tunerNotes[frequencies[targetnote]]
    prevNotePtr = (prevNotePtr + 1) % prevNotesLen

    # 2. Check if all prevNotes are the same as the singed (by user) note, to make sure it is singed long enough
    if (compareToPrevNotes(tunerNotes[frequencies[targetnote]])):
    
        # 3a. Get singer frequency from acapella ${curr_acap} at the exact moment ${elapsed_time_str}
        singer_note = getSingedNote(elapsed_time_str)
        
        # 3b. compare to find the mistake in percentage
        err_percentage = calculate_Diff_Percentage_From_Original(tunerNotes[frequencies[targetnote]], elapsed_time_str)

    # newSection2 ENDS HERE --------------------------------------------------------------------------------------------------------

    # Print the note with the elapsed time and error percentage
    print(f"{elapsed_time_str}: {tunerNotes[frequencies[targetnote]]}")

    return (in_data, pyaudio.paContinue)


# newSection3 STARTS HERE --------------------------------------------------------------------------------------------------------
def compareToPrevNotes(note):
    for i in range(prevNotesLen):
        if prevNotes[i] != note:
            return False
    return True

def getSingedNote(timestr):
    return 0 # TO-DO: Implement this function

def calculate_Diff_Percentage_From_Original(inputnote, timestr):
    return 0 # TO-DO: Implement this function
# newSection3 ENDS HERE --------------------------------------------------------------------------------------------------------

def read_from_mic():
    pa = pyaudio.PyAudio()
    # p.get_default_input_device_info()
    # pyaudio.pa.__file__
    stream = pa.open(
        format=FORMAT,
        channels=1,
        rate=RATE,
        output=False,
        input=True,
        frames_per_buffer=BUFFERSIZE,
        stream_callback=callback)


    stream.start_stream()

    #callback.elapsed_time = 0

    # Create a thread to handle the graph display
    graph_thread = threading.Thread(target=check_space_key)
    graph_thread.start()

    stop_streaming = False

    while not stop_streaming:
        time.sleep(0.1)

    stream.stop_stream()
    stream.close()
    pa.terminate()


# Function to stop the streaming and display the graph
def stop_and_display_graph():
    global stop_streaming
    stop_streaming = True
    plt.figure(figsize=(12, 6))
    plt.plot(time_data, frequency_data)
    plt.xlabel('Time (seconds)')
    plt.ylabel('Frequency (Hz)')
    plt.title('Time vs. Frequency')
    plt.grid(True)
    plt.show()

# Function to check for space key press
def check_space_key():
    while True:
        if keyboard.is_pressed('space'):
            stop_and_display_graph()
            break
        time.sleep(0.1)



# See https://github.com/endolith/waveform-analyzer/blob/master/frequency_estimator.py
def freq_from_autocorr(raw_data_signal, fs):
    corr = fftconvolve(raw_data_signal, raw_data_signal[::-1], mode='full')
    corr = corr[len(corr) // 2:]
    d = diff(corr)
    start = find(d > 0)[0]
    peak = argmax(corr[start:]) + start
    px, py = parabolic(corr, peak)
    return fs / px


# See https://github.com/endolith/waveform-analyzer/blob/master/frequency_estimator.py
def parabolic(f, x):
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
def loudness(chunk):
    data = np.array(chunk, dtype=float) / 32768.0
    denominator = len(data)

    if denominator <= 0:
        # Handle the case where the denominator is zero or negative
        return float('-inf')  # Or any other appropriate value

    ms = math.sqrt(np.sum(data ** 2.0) / denominator)
    if ms < 10e-8:
        ms = 10e-8

    return 10.0 * math.log(ms, 10.0)


def find_nearest(array, value):
    index = (np.abs(array - value)).argmin()
    return array[index]


def closest_value_index(array, guessValue):
    # Find the closest element in the array, value wise
    closestValue = find_nearest(array, guessValue)
    # Find indices of closestValue
    indexArray = np.where(array == closestValue)
    # numpy 'where' returns a 2D array with the element index as the value

    return indexArray[0][0]


def read_from_wav(file):
    CHUNK = 1024
    wf = wave.open(file, 'rb')
    data = wf.readframes(CHUNK)
    while data != b'':
        data = wf.readframes(CHUNK)
        callback(data, 0, 0, 0)


def convertMp3ToWav(input_file):
    inputName = input_file[:-4]
    output_file = "C:/Fun projects/testingMusicalProject/" + inputName + ".wav"

    # # convert mp3 file to wav file
    inputWithPath = "C:/Fun projects/testingMusicalProject/" + input_file
    # sound = AudioSegment.from_mp3(inputWithPath)
    # sound.export(output_file, format="wav")

    #subprocess.call(['ffmpeg', '-i', input_file, output_file])


def convertMp3ToWav2(input_mp3):

    # Output WAV file path
    output_wav = input_mp3[:-4] + ".wav"

    # Load the MP3 file as a video clip (audio only)
    clip = AudioFileClip(input_mp3)

    # Write the audio to a WAV file
    clip.write_audiofile(output_wav)



if __name__ == "__main__":

    #convertMp3ToWav2("Vincent.mp3") 

    # read_from_wav("mary.wav")
    read_from_mic()
