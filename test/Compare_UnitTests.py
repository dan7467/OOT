import unittest
from unittest.mock import patch, MagicMock, call
from compare import *
import numpy as np

class TestComparedSongs(unittest.TestCase):

    def setUp(self):
        # Set up a mock for dtwElements
        self.dtwElements = {
            (0, 0): dtwElementInfo(440.0, 440.0, 0, 0, 0.0, 0.0),
            (1, 1): dtwElementInfo(660.0, 660.0, 1, 1, 1.0, 1.0),
        }
        self.x = [440.0, 660.0]
        self.y = [440.0, 660.0]
        self.dtw_path = [(0, 0), (1, 1)]
        self.compared_songs = ComparedSongs("songName", "performanceName", 90, self.dtwElements, self.x, self.y,
                                            self.dtw_path)

    @patch('compare.alignedDTWBarPlot')
    def test_showBarGraph(self, mock_alignedDTWBarPlot):
        self.compared_songs.showBarGraph()
        mock_alignedDTWBarPlot.assert_called_once_with(self.x, self.y, self.dtw_path)

    @patch('compare.tk.Tk')
    def test_hearClips(self, mock_Tk):
        mock_window = MagicMock()
        mock_Tk.return_value = mock_window

        self.compared_songs.hearClips()

        self.assertTrue(mock_window.mainloop.called)
        self.assertTrue(mock_window.protocol.called)
        self.assertEqual(mock_window.protocol.call_args[0][0], "WM_DELETE_WINDOW")

    @patch('compare.getShortAudioClip')
    def test_getShortAudioClipFromEntries(self, mock_getShortAudioClip):
        with patch('compare.getClosestElementsWIthIndices',
                   return_value=(0, 1)) as mock_getClosestElementsWIthIndices:
            self.compared_songs.getShortAudioClipFromEntries(1, "0", "1", self.dtwElements)
            mock_getClosestElementsWIthIndices.assert_called_once_with(self.dtwElements, 0, 1, "x")
            mock_getShortAudioClip.assert_called_once_with("performanceName", 0, 1)

            self.compared_songs.getShortAudioClipFromEntries(2, "0", "1", self.dtwElements)
            mock_getClosestElementsWIthIndices.assert_called_with(self.dtwElements, 0, 1, "y")
            mock_getShortAudioClip.assert_called_with("songName", 0, 1)

    def test_initialization(self):
        self.assertEqual(self.compared_songs.songName, "songName")
        self.assertEqual(self.compared_songs.performanceName, "performanceName")
        self.assertEqual(self.compared_songs.score, 90)
        self.assertEqual(self.compared_songs.dtwElements, self.dtwElements)
        self.assertEqual(self.compared_songs.x, self.x)
        self.assertEqual(self.compared_songs.y, self.y)
        self.assertEqual(self.compared_songs.dtw_path, self.dtw_path)




class TestDTWFunctions(unittest.TestCase):

    def test_getClosestElementsWIthIndices(self):
        dtwElementsInfo = {
            (0, 0): dtwElementInfo(440, 440, 0, 0, 0.0, 0.0),
            (1, 1): dtwElementInfo(450, 450, 1, 1, 1.0, 1.0),
            (2, 2): dtwElementInfo(460, 460, 2, 2, 2.0, 2.0),
            (3, 3): dtwElementInfo(470, 470, 3, 3, 3.0, 3.0),
            (4, 4): dtwElementInfo(480, 480, 4, 4, 4.0, 4.0)
        }
        self.assertEqual(getClosestElementsWIthIndices(dtwElementsInfo, 1, 3, "x"), (1.0, 3.0))
        self.assertEqual(getClosestElementsWIthIndices(dtwElementsInfo, 2, 4, "y"), (2.0, 4.0))



    def test_computeScore(self):
        micFreqs = np.array([440, 450, 460])
        origFreqs = np.array([440, 450, 460])
        score = computeScore(micFreqs, origFreqs)
        self.assertEqual(score, 100)

        micFreqs = np.array([440, 450, 470])
        origFreqs = np.array([440, 450, 460])
        score = computeScore(micFreqs, origFreqs)
        self.assertLess(score, 100)



    def test_removeDuplicatesFromXPath(self):
        x = np.array([440, 450, 460, 470, 480])
        y = np.array([440, 450, 460, 470, 480])
        xTime = [0.0, 1.0, 2.0, 3.0, 4.0]
        yTime = [0.0, 1.0, 2.0, 3.0, 4.0]
        dtw_path = [(0, 0), (1, 1), (1, 2), (1, 3), (3, 2), (4, 4)]

        x, y, dtw_path, dtwElementsDict = removeDuplicatesFromXPath(x, y, dtw_path, xTime, yTime)
        self.assertEqual(dtw_path, [(0, 0), (1, 1), (3, 2), (4, 4)])
        self.assertEqual(len(dtwElementsDict), 4)

        dtw_path = [(0, 0), (1, 1), (2, 2), (3, 3), (4, 2)]

        x, y, dtw_path, dtwElementsDict = removeDuplicatesFromXPath(x, y, dtw_path, xTime, yTime)
        self.assertEqual(dtw_path, [(0, 0), (1, 1), (2, 2), (3, 3), (4, 2)])
        self.assertEqual(len(dtwElementsDict), 5)




    def test_fasDtTW(self):
        x = np.array([440, 450, 460, 470, 480])
        y = np.array([440, 450, 460, 470, 480])
        xTime = [0.0, 1.0, 2.0, 3.0, 4.0]
        yTime = [0.0, 1.0, 2.0, 3.0, 4.0]
        songName = "test_song"
        newMicSOngName = "test_mic_song"

        result = dtwAlgo(x, y, xTime, yTime, songName, newMicSOngName)
        self.assertIsInstance(result, ComparedSongs)
        self.assertEqual(result.songName, songName)
        self.assertEqual(result.performanceName, newMicSOngName)
        self.assertEqual(result.score, 100)
        self.assertEqual(len(result.dtwElements), 5)



    def test_fasDtTW2(self):
        x = np.array([440, 450, 460, 470, 480])
        y = np.array([440, 450, 460, 470])
        xTime = [0.0, 1.0, 2.0, 3.0, 4.0]
        yTime = [0.0, 1.0, 2.0, 3.0, 4.0]
        songName = "test_song"
        newMicSOngName = "test_mic_song"

        result = dtwAlgo(x, y, xTime, yTime, songName, newMicSOngName)
        self.assertIsInstance(result, ComparedSongs)
        self.assertEqual(result.songName, songName)
        self.assertEqual(result.performanceName, newMicSOngName)
        self.assertLess(result.score, 100)
        self.assertEqual(len(result.dtwElements), 5)



if __name__ == '__main__':
    unittest.main()
