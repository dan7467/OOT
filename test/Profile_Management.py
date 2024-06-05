import unittest

from db_persistence_layer import *
from frontend.OutOfTune import OutOfTune


class ProfileManagement(unittest.TestCase):

    userName = "ProfileManagement"

    @classmethod
    def setUpClass(cls):
        cls.oot = OutOfTune(cls.userName)

    @classmethod
    def tearDownClass(cls):
        # Optionally, add cleanup code here if needed, like deleting the test user account
        pass

    def test_1(self):
        # Check if the user exists in the database after creation
        # self.assertTrue(does_user_exist(self.oot.dbAccess.db, self.userName),
        #                 "Account creation failed, user does not exist")


if __name__ == '__main__':
    unittest.main()
