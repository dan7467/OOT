import unittest
from filesAccess import DBAccess

class AudioComparison(unittest.TestCase):
    userName = "TestDontDelete"
    oot = None
    songName = "Uf Gozal"
    songUserName = songName + '_' + userName


    @classmethod
    def setUpClass(cls):
        cls.dbAccess = DBAccess(cls.userName)


    #Performance Logging 3.1 Store Ratings
    def test_01_getRating(self):
        res = self.dbAccess.fetchPerformancesFromUser(self.songName)
        fetchedName = res[0]['song_name']
        self.assertEqual(fetchedName, self.songUserName)
        self.assertIsNotNone(res[0]['_id'])
        self.assertEqual(res[0]['score'], 88)



    def test_02_getRatingNotExistSong(self):
        res = self.dbAccess.fetchPerformancesFromUser(" ")
        self.assertIsNone(res)



if __name__ == '__main__':
    unittest.main()
