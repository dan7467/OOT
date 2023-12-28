import crepe
from matplotlib import pyplot as plt
from scipy.io import wavfile
import crepe
import librosa
import matplotlib.pyplot as plt
import resampy
import tensorflow as tf
from keras import backend as K

# Configure Keras backend to use TensorFlow
# K.set_image_data_format('channels_last')
# K.set_floatx('float32')
# tf.compat.v1.keras.backend.set_session(tf.compat.v1.Session())


CONFIDENCE_LEVEL = 0.95

#GITHUB
#https://github.com/maxrmorrison/torchcrepe

#NEED TO UPGRADE TO PYTHON 3.7.2 !!
def crepePrediction(sr, y):

    # Call crepe to estimate pitch and confidence
    time, frequency, confidence, _ = crepe.predict(y, sr, viterbi=True,
                                                   model_capacity='full', step_size=20)

    # Filter out frequencies with confidence below 0.5
    reliable_indices = confidence >= CONFIDENCE_LEVEL
    reliable_confidence = confidence[reliable_indices]
    reliable_time = time[reliable_indices]
    reliable_frequency = frequency[reliable_indices]


    # Create two separate plots for estimated pitch and confidence
    fig, axs = plt.subplots(2, 1, figsize=(10, 8))

    # Plot the estimated pitch over time
    axs[0].plot(reliable_time, reliable_frequency, label='Estimated pitch (Hz)', color='blue')
    axs[0].set_xlabel('Time (s)')
    axs[0].set_ylabel('Frequency (Hz)')
    axs[0].set_title('Estimated Pitch')
    axs[0].legend()

    # Plot the confidence over time
    axs[1].plot(reliable_time, reliable_confidence, label='Confidence', color='green')
    axs[1].set_xlabel('Time (s)')
    axs[1].set_ylabel('Confidence')
    axs[1].set_title('Confidence')
    axs[1].legend()

    plt.tight_layout()
    plt.show()


def testCrepe(audio_path):
    # Load audio file using librosa
    #audio_path = './songsWav/pink_panther_faulty.wav'

    sr, y = wavfile.read(audio_path)

    crepePrediction(sr, y)
