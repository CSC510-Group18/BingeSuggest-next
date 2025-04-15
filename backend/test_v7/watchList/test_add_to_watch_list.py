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


class TestAddToWatchList(unittest.TestCase):
    """
    Test cases for adding movies to watched history.
    """

    def setUp(self):
        """
        Set up test database before each test.
        """
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
        cursor.execute("""CREATE TABLE IF NOT EXISTS Watchlist (
            user_id INTEGER,
            movie_id TEXT,
            timestamp TEXT,
            FOREIGN KEY(user_id) REFERENCES Users(idUsers)
        )""")
        self.db.commit()

    def test_add_movie_success_different_movie(self):
        """
        Test adding a different movie successfully.
        """
        create_account(self.db, "user4@test.com", "user4", "password123")
        cursor = self.db.cursor()
        cursor.execute("SELECT idUsers FROM Users")
        user_id = cursor.fetchone()[0]
        result = add_to_watchlist(self.db, user_id, "0266543")
        self.assertTrue(result)

    def test_add_movie_already_exists_different_movie(self):
        """
        Test adding a movie that already exists in watched history with a different movie.
        """
        create_account(self.db, "user5@test.com", "user5", "password123")
        cursor = self.db.cursor()
        cursor.execute("SELECT idUsers FROM Users")
        user_id = cursor.fetchone()[0]
        add_to_watchlist(self.db, user_id, "0266543")
        result = add_to_watchlist(self.db, user_id, "0266543")
        self.assertFalse(result)

    def test_add_movie_not_in_database_different_movie(self):
        """
        Test adding a movie that is not in the database with a different movie.
        """
        create_account(self.db, "user6@test.com", "user6", "password123")
        cursor = self.db.cursor()
        cursor.execute("SELECT idUsers FROM Users")
        user_id = cursor.fetchone()[0]
        result = add_to_watchlist(self.db, user_id, "0000000", None)
        self.assertTrue(result)

    def test_add_multiple_movies_success(self):
        """
        Test adding multiple movies successfully.
        """
        create_account(self.db, "user7@test.com", "user7", "password123")
        cursor = self.db.cursor()
        cursor.execute("SELECT idUsers FROM Users")
        user_id = cursor.fetchone()[0]
        movies = ["0109830", "0169547"]
        for movie in movies:
            result = add_to_watchlist(self.db, user_id, movie)
            self.assertTrue(result)

    def test_add_movie_with_provided_timestamp(self):
        """
        Test adding a movie with a provided timestamp.
        """
        create_account(self.db, "user8@test.com", "user8", "password123")
        cursor = self.db.cursor()
        cursor.execute("SELECT idUsers FROM Users")
        user_id = cursor.fetchone()[0]
        result = add_to_watchlist(self.db, user_id, "0033467", "2024-11-23 12:00:00")
        self.assertTrue(result)

    def test_add_movie_no_timestamp(self):
        """
        Test adding a movie without a timestamp.
        """
        create_account(self.db, "user9@test.com", "user9", "password123")
        cursor = self.db.cursor()
        cursor.execute("SELECT idUsers FROM Users")
        user_id = cursor.fetchone()[0]
        result = add_to_watchlist(self.db, user_id, "0168629", None)
        self.assertTrue(result)

    def test_add_movie_to_watchlist_duplicate_user(self):
        """
        Test adding a movie to watchlist for the same user multiple times.
        """
        create_account(self.db, "user10@test.com", "user10", "password123")
        cursor = self.db.cursor()
        cursor.execute("SELECT idUsers FROM Users")
        user_id = cursor.fetchone()[0]
        add_to_watchlist(self.db, user_id, "0168629", None)
        result = add_to_watchlist(self.db, user_id, "0168629", None)
        self.assertFalse(result)

    def test_add_movie_to_watchlist_invalid_user(self):
        """
        Test adding a movie to watchlist with an invalid user ID.
        """
        result = add_to_watchlist(self.db, 999, "0168629", None)
        self.assertTrue(result)

    def test_add_movie_not_found_in_watchlist(self):
        """
        Test trying to add a movie that doesn't exist in the database.
        """
        create_account(self.db, "user11@test.com", "user11", "password123")
        cursor = self.db.cursor()
        cursor.execute("SELECT idUsers FROM Users")
        user_id = cursor.fetchone()[0]
        result = add_to_watchlist(self.db, user_id, "9999999", None)
        self.assertTrue(result)

    def test_add_movie_different_movies(self):
        """
        Test adding multiple different movies to the watchlist for the same user.
        """
        create_account(self.db, "user12@test.com", "user12", "password123")
        cursor = self.db.cursor()
        cursor.execute("SELECT idUsers FROM Users")
        user_id = cursor.fetchone()[0]
        movies = ["0109830", "0113101", "0094675"]
        for movie in movies:
            result = add_to_watchlist(self.db, user_id, movie, None)
            self.assertTrue(result)

    def test_add_movie_with_null_user_id(self):
        """
        Test adding a movie with a null user ID.
        """
        with self.assertRaises(TypeError):
            add_to_watchlist(self.db, None, "0109830", None)

    def test_add_movie_with_null_movie_id(self):
        """
        Test adding a movie with a null movie ID.
        """
        create_account(self.db, "user13@test.com", "user13", "password123")
        cursor = self.db.cursor()
        cursor.execute("SELECT idUsers FROM Users")
        user_id = cursor.fetchone()[0]
        with self.assertRaises(TypeError):
            add_to_watchlist(self.db, user_id, None, None)

    def test_add_movie_with_empty_movie_id(self):
        """
        Test adding a movie with an empty movie ID.
        """
        create_account(self.db, "user14@test.com", "user14", "password123")
        cursor = self.db.cursor()
        cursor.execute("SELECT idUsers FROM Users")
        user_id = cursor.fetchone()[0]
        with self.assertRaises(ValueError):
            add_to_watchlist(self.db, user_id, "", None)

    def test_add_movie_with_special_characters_in_movie_id(self):
        """
        Test adding a movie with special characters in the movie ID.
        """
        create_account(self.db, "user15@test.com", "user15", "password123")
        cursor = self.db.cursor()
        cursor.execute("SELECT idUsers FROM Users")
        user_id = cursor.fetchone()[0]
        with self.assertRaises(ValueError):
            add_to_watchlist(self.db, user_id, "tt@#$%^", None)

    def test_add_movie_with_large_movie_id(self):
        """
        Test adding a movie with a very large movie ID.
        """
        create_account(self.db, "user16@test.com", "user16", "password123")
        cursor = self.db.cursor()
        cursor.execute("SELECT idUsers FROM Users")
        user_id = cursor.fetchone()[0]
        with self.assertRaises(OverflowError):
            add_to_watchlist(self.db, user_id, "12345678901234567890", None)

    def test_add_movie_with_invalid_timestamp_format(self):
        """
        Test adding a movie with an invalid timestamp format.
        """
        create_account(self.db, "user17@test.com", "user17", "password123")
        cursor = self.db.cursor()
        cursor.execute("SELECT idUsers FROM Users")
        user_id = cursor.fetchone()[0]
        result = add_to_watchlist(self.db, user_id, "0109830", "invalid-timestamp")
        self.assertTrue(result)

    def test_add_movie_with_duplicate_entries(self):
        """
        Test adding a movie with duplicate entries in the watchlist.
        """
        create_account(self.db, "user18@test.com", "user18", "password123")
        cursor = self.db.cursor()
        cursor.execute("SELECT idUsers FROM Users")
        user_id = cursor.fetchone()[0]
        add_to_watchlist(self.db, user_id, "0109830", None)
        result = add_to_watchlist(self.db, user_id, "0109830", None)
        self.assertFalse(result)

    def test_add_movie_with_sql_injection_attempt(self):
        """
        Test adding a movie with an SQL injection attempt in the movie ID.
        """
        create_account(self.db, "user19@test.com", "user19", "password123")
        cursor = self.db.cursor()
        cursor.execute("SELECT idUsers FROM Users")
        user_id = cursor.fetchone()[0]
        with self.assertRaises(ValueError):
            add_to_watchlist(self.db, user_id, "1234567; DROP TABLE Watchlist;", None)

    def test_add_movie_with_empty_database(self):
        """
        Test adding a movie when the database is empty.
        """
        create_account(self.db, "user20@test.com", "user20", "password123")
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM Watchlist")
        self.db.commit()
        cursor.execute("SELECT idUsers FROM Users")
        user_id = cursor.fetchone()[0]
        result = add_to_watchlist(self.db, user_id, "0109830", None)
        self.assertTrue(result)

    def test_add_movie_with_nonexistent_user(self):
        """
        Test adding a movie with a user ID that does not exist in the database.
        """
        result = add_to_watchlist(self.db, 9999, "0109830", None)
        self.assertTrue(result)

if __name__ == "__main__":
    unittest.main()
