import unittest
from unittest.mock import patch

# Assuming OutOfTune class is defined in the module out_of_tune
from OutOfTune import *


class TestOutOfTune(unittest.TestCase):

    @patch('frontend.OutOfTune.DBAccess')
    def setUp(self, MockDBAccess):
        self.userName = "testUser"
        self.out_of_tune = OutOfTune(self.userName)
        self.mock_db_access = MockDBAccess.return_value

    def test_freqToNote(self):
        self.assertEqual(self.out_of_tune.freqToNote(440.00), 'A4')
        self.assertEqual(self.out_of_tune.freqToNote(0), '0')
        self.assertEqual(self.out_of_tune.freqToNote(261.60), 'C4')


    @patch('frontend.OutOfTune.pyaudio.PyAudio')
    def test_start_timer(self, MockPyAudio):
        mock_pa = MockPyAudio.return_value
        self.out_of_tune.start_timer()
        self.assertTrue(self.out_of_tune.start_flag)
        mock_pa.open.assert_called()


    def test_stop_timer(self):
        with patch('frontend.OutOfTune.pyaudio.PyAudio'):
            self.out_of_tune.start_timer()
        self.out_of_tune.stop_timer()
        self.assertTrue(self.out_of_tune.stop_flag)


    def test_freq_from_autocorr(self):
        # Test with a known signal
        fs = 8000
        t = np.arange(0, 1.0, 1.0/fs)
        f = 440.0
        signal = 0.5 * np.sin(2 * np.pi * f * t)
        signal = np.array(signal * 32767, dtype=np.int16)
        result = self.out_of_tune.freq_from_autocorr(signal, fs)
        self.assertAlmostEqual(result, f, delta=1)


    def test_closest_value_index(self):
        array = np.array([65.41, 69.30, 73.42])
        value = 70.00
        index = self.out_of_tune.closest_value_index(array, value)
        self.assertEqual(index, 1)  # closest value is 69.30





    def test_removeDuplicatesFromDict(self):
        input_dict = {1: 150, 2: 250, 3: 250, 4: 420, 5: 419, 6: 421}
        expected_output = {1.5: 146.8, 2.5: 246.9, 4.5: 415.3}
        result = self.out_of_tune.removeDuplicatesFromDict(list(input_dict.keys()), list(input_dict.values()), False)
        self.assertEqual(result, expected_output)



    def test_removeDuplicatesFromDict_empty(self):
        result = self.out_of_tune.removeDuplicatesFromDict([], [], False)
        self.assertEqual(result, {})



    def test_removeDuplicatesFromDict_no_duplicates(self):
        input_dict = {1: 150, 2: 250, 3: 320, 4: 420}
        expected_output = {1.5: 146.8, 2.5: 246.9, 3.5: 311.1}
        result = self.out_of_tune.removeDuplicatesFromDict(list(input_dict.keys()), list(input_dict.values()), False)
        self.assertEqual(result, expected_output)





    def test_getFirstTimeOfRealNoteFromSecondVar(self):
        input_data = {0: '0', 35: 'C4', 770: 'E2'}
        expected_output = 35
        result = self.out_of_tune.getFirstTimeOfRealNoteFromSecondVar(input_data, 0)
        self.assertEqual(result, expected_output)



    def test_getFirstTimeOfRealNoteFromSecondVarStartingFromZero(self):
        input_data = {0.5: 'C5', 1: '0', 2: '0'}

        expected_output = 0.5
        result = self.out_of_tune.getFirstTimeOfRealNoteFromSecondVar(input_data, 0)
        self.assertEqual(result, expected_output)






    def test_adjustMicTimesAccordingToArchive(self):
        archive = {10: 'C5', 12: '0', 13: '0'}
        mic = {11: 'C5', 21: '0', 22: '0'}
        expected_output = {11: 'C5', 13: '0', 14: '0'}
        self.out_of_tune.adjustMicTimesAccordingToArchive(mic, archive)
        self.assertEqual(self.out_of_tune.dictFromMic, expected_output)



    def test_adjustMicTimesAccordingToArchive_no_adjustment_needed(self):
        archive = {1: 'C5', 2: '0', 3: '0'}
        mic = {1: 'C5', 2: '0', 3: '0'}
        expected_output = {}
        self.out_of_tune.adjustMicTimesAccordingToArchive(mic, archive)
        self.assertEqual(self.out_of_tune.dictFromMic, expected_output)



    def test_adjustMicTimesAccordingToArchive_empty_mic_times(self):
        mic_times = {}
        archive_times = {1: 'C5', 2: '0', 3: '0'}
        expected_output = {}
        self.out_of_tune.adjustMicTimesAccordingToArchive(mic_times, archive_times)
        self.assertEqual(self.out_of_tune.dictFromMic, expected_output)




if __name__ == '__main__':
    unittest.main()
