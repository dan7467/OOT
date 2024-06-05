import unittest
import os
from unittest.mock import patch, mock_open, MagicMock
from filesAccess import *


class FileAccessUnitTests(unittest.TestCase):

    def setUp(self):
        self.songName = "testSong"
        self.notesDict = {0.0: 440.0, 1.0: 450.0}
        self.fileData = FileData(self.songName, 0, 0, 0, 16000, self.notesDict)



    @patch('os.path.isfile')
    def test_getDataFromFile(self, mock_isfile):
        mock_isfile.return_value = True
        data = '0.0-440.0 ; 1.0-450.0 ; '
        with patch('builtins.open', mock_open(read_data=data)):
            file_data = getDataFromFile(self.songName)
            self.assertEqual(file_data.notesDict[0.0], 440.0)
            self.assertEqual(file_data.notesDict[1.0], 450.0)

    @patch('os.path.isfile')
    def test_getDataFromFile_fileNotFound(self, mock_isfile):
        mock_isfile.return_value = False
        file_data = getDataFromFile(self.songName)
        self.assertIsNone(file_data)

    @patch('os.path.isfile')
    def test_checkIfSongDataExists(self, mock_isfile):
        mock_isfile.return_value = True
        result = checkIfSongDataExists(self.songName)
        self.assertTrue(result)

    @patch('os.path.isfile')
    def test_checkIfSongDataExists_notFound(self, mock_isfile):
        mock_isfile.return_value = False
        result = checkIfSongDataExists(self.songName)
        self.assertFalse(result)

    @patch('os.listdir')
    def test_getAvailableSongs(self, mock_listdir):
        mock_listdir.return_value = ['song1.txt', 'song2.txt']
        db = MagicMock()
        db.getSongsNameList.return_value = ['song1', 'song2']
        result = printAvailableSongs(db)
        self.assertEqual('song1', result['0'])
        self.assertEqual('song2', result['1'])

    @patch('os.listdir')
    def test_getAvailableWavs(self, mock_listdir):
        mock_listdir.return_value = ['song1.wav', 'song2.wav']
        result = printAvailableWavs()
        self.assertEqual('song1', result['0'])
        self.assertEqual('song2', result['1'])


    @patch('os.remove')
    def test_removeFIle(self, mock_remove):
        path = PATH + 'testFile.txt'
        removeFIle(path)
        mock_remove.assert_called_once_with(path)

    @patch('os.remove')
    def test_removeFIle_notFound(self, mock_remove):
        mock_remove.side_effect = FileNotFoundError
        path = PATH + 'testFile.txt'
        removeFIle(path)
        mock_remove.assert_called_once_with(path)

    @patch('os.remove')
    def test_removeFIle_permissionError(self, mock_remove):
        mock_remove.side_effect = PermissionError
        path = PATH + 'testFile.txt'
        removeFIle(path)
        mock_remove.assert_called_once_with(path)

    @patch('os.remove')
    def test_removeFIle_generalException(self, mock_remove):
        mock_remove.side_effect = Exception('An error occurred')
        path = PATH + 'testFile.txt'
        removeFIle(path)
        mock_remove.assert_called_once_with(path)



if __name__ == '__main__':
    unittest.main()
