import unittest

from db_persistence_layer import *
from frontend.OutOfTune import OutOfTune


class ProfileManagement(unittest.TestCase):
    userName = "TestProfileManagement"
    oot = None
    songName = "mary"
    songUserName = songName + '_' + userName

    @classmethod
    def setUpClass(cls):
        cls.oot = OutOfTune(cls.userName)


    @classmethod
    def tearDownClass(cls):
        cls.oot.dbAccess.deleteUser()


    # Add Song  3.1.1
    def test_01_addSong(self):

        nameWithWav = self.songName + '.wav'

        self.oot.getSongData(nameWithWav, False, self.oot)
        allSongs = self.oot.dbAccess.getSongsNameList()
        self.assertTrue(self.songUserName in allSongs)

    def test_02_addSongWrongName(self):
        name = "NotExist.wav"
        self.oot.getSongData(name, False, self.oot)
        allSongs = self.oot.dbAccess.getSongsNameList()
        self.assertFalse(name in allSongs)

    def test_03_addSongNotCaseSensitive(self):
        name = "MARY"
        wavName = name + '.wav'
        self.oot.getSongData(wavName, False, self.oot)
        allSongs = self.oot.dbAccess.getSongsNameList()
        songUserName = name + '_' + self.userName
        self.assertTrue(songUserName in allSongs)

    # Remove Song  3.1.2
    def test_04_removeSong(self):

        self.oot.dbAccess.deleteSongAndPerformances(self.songName)
        allSongs = self.oot.dbAccess.getSongsNameList()
        self.assertFalse(self.songUserName in allSongs)

    def test_05_removeSongNotExisting(self):

        self.oot.dbAccess.deleteSongAndPerformances("Not exists")
        allSongs = self.oot.dbAccess.getSongsNameList()
        self.assertFalse(self.songUserName in allSongs)

    def test_06_removeSongAlreadyRemoved(self):

        allSongs = self.oot.dbAccess.getSongsNameList()
        self.assertFalse(self.songUserName in allSongs)


if __name__ == '__main__':
    unittest.main()
