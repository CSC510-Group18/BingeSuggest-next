import sys
import unittest
import warnings
from pathlib import Path
import sqlite3
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).resolve().parents[2]))
# pylint: disable=wrong-import-position
from src.recommenderapp.utils import add_to_watchlist, create_account

# pylint: enable=wrong-import-position
warnings.filterwarnings("ignore")


class Tests(unittest.TestCase):
    """
    Test cases for actor based recommender system
    """

    def setUp(self):
        print("\nrunning setup method")
        load_dotenv()
        self.db = sqlite3.connect(':memory:')
        cursor = self.db.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS Users (
            idUsers INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS Ratings (
            user_id INTEGER,
            movie_id INTEGER,
            score INTEGER,
            review TEXT,
            time TEXT,
            FOREIGN KEY(user_id) REFERENCES Users(idUsers)
        )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS Friends (
            user_id INTEGER,
            friend_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES Users(idUsers),
            FOREIGN KEY(friend_id) REFERENCES Users(idUsers)
        )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS Watchlist (
            user_id INTEGER,
            movie_id INTEGER,
            timestamp TEXT,
            FOREIGN KEY(user_id) REFERENCES Users(idUsers)
        )""")
        self.db.commit()

    def test_add_function1(self):
        """
        Test case 1
        """
        create_account(self.db, "abc@test.com", "someUser", "Pass")
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM Users")
        db_result = cursor.fetchall()
        user_id = db_result[0][0]
        self.assertTrue(add_to_watchlist(self.db, user_id, "11"))

    def test_add_function2(self):
        """
        Test case 2
        """
        create_account(self.db, "abc@test.com", "someUser", "Pass")
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM Users")
        db_result = cursor.fetchall()
        user_id = db_result[0][0]
        add_to_watchlist(self.db, user_id, "11")
        self.assertFalse(add_to_watchlist(self.db, user_id, "11"))


if __name__ == "__main__":
    unittest.main()
