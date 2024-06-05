from frontend.OutOfTune import OutOfTune
import unittest
from db_persistence_layer import *


# Define class to test the program
class AccountOperationTests(unittest.TestCase):

    def setUp(self):
        self.oot1 = None
        self.userNameToAdd = "TestAccountOperation1"
        self.userNameToDelete = "TestAccountOperation2"
        self.oot2 = OutOfTune(self.userNameToDelete)

    # Create account 1.1
    def test_createAccount(self):
        self.oot1 = OutOfTune(self.userNameToAdd)
        self.assertTrue(does_user_exist(self.oot1.dbAccess.db, self.userNameToAdd))
        self.oot1.dbAccess.deleteUser()

    # Delete account 1.2
    def test_deleteAccount(self):
        self.oot2.dbAccess.deleteUser()
        self.assertFalse(does_user_exist(self.oot2.dbAccess.db, self.userNameToDelete))


if __name__ == '__main__':
    unittest.main()


