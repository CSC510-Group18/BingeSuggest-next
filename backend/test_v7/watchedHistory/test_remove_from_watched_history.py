import sys
import unittest
import warnings
from pathlib import Path
import sqlite3
from dotenv import load_dotenv
from datetime import datetime

sys.path.append(str(Path(__file__).resolve().parents[2]))
from src.recommenderapp.utils import (
    create_account,
    add_to_watched_history,
    remove_from_watched_history_util,
)

warnings.filterwarnings("ignore")


class TestRemoveFromWatchedHistory(unittest.TestCase):
    def setUp(self):
        """
        Set up test database before each test.
        """
        load_dotenv()
        self.db = sqlite3.connect(':memory:')
        cursor = self.db.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS Users (
            idUsers INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS WatchedHistory (
            user_id INTEGER,
            movie_id INTEGER,
            watched_date TEXT,
            FOREIGN KEY(user_id) REFERENCES Users(idUsers),
            FOREIGN KEY(movie_id) REFERENCES Movies(idMovies)
        )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS Movies (
            idMovies INTEGER PRIMARY KEY AUTOINCREMENT,
            imdb_id TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL
        )""")
        cursor.execute("INSERT INTO Movies (imdb_id, title) VALUES (?, ?)", 
                      ("tt0076759", "Star Wars"))
        cursor.execute("INSERT INTO Movies (imdb_id, title) VALUES (?, ?)",
                      ("tt0168629", "Test Movie"))
        self.db.commit()

    def test_remove_movie_success(self):
        """
        Test removing a movie successfully from watched history.
        """
        create_account(self.db, "user1@test.com", "user1", "password123")
        cursor = self.db.cursor()
        cursor.execute("SELECT idUsers FROM Users")
        user_id = cursor.fetchone()[0]
        add_to_watched_history(self.db, user_id, "tt0076759", None)
        result = remove_from_watched_history_util(self.db, user_id, "tt0076759")
        self.assertEqual(result, (True, "Movie removed from watched history"))

    def test_remove_nonexistent_movie(self):
        """
        Test removing a movie that is not in watched history.
        """
        create_account(self.db, "user2@test.com", "user2", "password123")
        cursor = self.db.cursor()
        cursor.execute("SELECT idUsers FROM Users")
        user_id = cursor.fetchone()[0]
        result = remove_from_watched_history_util(self.db, user_id, "tt0266543")
        self.assertEqual(result, (False, "Movie not found"))

    def test_remove_movie_not_in_database(self):
        """
        Test removing a movie that does not exist in the database.
        """
        create_account(self.db, "user3@test.com", "user3", "password123")
        cursor = self.db.cursor()
        cursor.execute("SELECT idUsers FROM Users")
        user_id = cursor.fetchone()[0]
        result = remove_from_watched_history_util(self.db, user_id, "tt0000000")
        self.assertEqual(result, (False, "Movie not found"))

    def test_remove_movie_invalid_user(self):
        """
        Test removing a movie with an invalid user ID.
        """
        create_account(self.db, "user4@test.com", "user4", "password123")
        cursor = self.db.cursor()
        cursor.execute("SELECT idUsers FROM Users")
        user_id = cursor.fetchone()[0]
        add_to_watched_history(self.db, user_id, "tt0076759", None)
        result = remove_from_watched_history_util(self.db, 999, "tt0076759")
        self.assertEqual(result, (False, "Movie not in watched history"))

    def test_remove_movie_no_user_provided(self):
        """
        Test removing a movie without providing a user ID.
        """
        create_account(self.db, "user5@test.com", "user5", "password123")
        cursor = self.db.cursor()
        cursor.execute("SELECT idUsers FROM Users")
        user_id = cursor.fetchone()[0]
        add_to_watched_history(self.db, user_id, "tt0076759", None)
        result = remove_from_watched_history_util(self.db, None, "tt0076759")
        self.assertEqual(result, (False, "Movie not in watched history"))

    def test_remove_movie_empty_imdb_id(self):
        """
        Test removing a movie with an empty IMDb ID.
        """
        create_account(self.db, "user6@test.com", "user6", "password123")
        cursor = self.db.cursor()
        cursor.execute("SELECT idUsers FROM Users")
        user_id = cursor.fetchone()[0]
        result = remove_from_watched_history_util(self.db, user_id, "")
        self.assertEqual(result, (False, "Movie not found"))

    def test_remove_movie_invalid_imdb_id(self):
        """
        Test removing a movie with an invalid IMDb ID.
        """
        create_account(self.db, "user7@test.com", "user7", "password123")
        cursor = self.db.cursor()
        cursor.execute("SELECT idUsers FROM Users")
        user_id = cursor.fetchone()[0]
        result = remove_from_watched_history_util(self.db, user_id, "invalid_id")
        self.assertEqual(result, (False, "Movie not found"))

    def test_remove_movie_not_in_watched_history(self):
        """
        Test removing a movie that the user has not added to their watched history.
        """
        create_account(self.db, "user10@test.com", "user10", "password123")
        cursor = self.db.cursor()
        cursor.execute("SELECT idUsers FROM Users")
        user_id = cursor.fetchone()[0]
        result = remove_from_watched_history_util(self.db, user_id, "tt0266543")
        self.assertEqual(result, (False, "Movie not found"))

    def test_remove_movie_no_timestamp(self):
        """
        Test removing a movie without a timestamp provided.
        """
        create_account(self.db, "user10@test.com", "user10", "password123")
        cursor = self.db.cursor()
        cursor.execute("SELECT idUsers FROM Users")
        user_id = cursor.fetchone()[0]
        add_to_watched_history(self.db, user_id, "tt0168629", None)
        result = remove_from_watched_history_util(self.db, user_id, "tt0168629")
        self.assertEqual(result, (True, "Movie removed from watched history"))

    def test_remove_movie_with_multiple_movies(self):
        """
        Test removing a movie when the user has multiple movies in watched history.
        """
        create_account(self.db, "user11@test.com", "user11", "password123")
        cursor = self.db.cursor()
        cursor.execute("SELECT idUsers FROM Users")
        user_id = cursor.fetchone()[0]
        add_to_watched_history(self.db, user_id, "tt0076759", None)
        add_to_watched_history(self.db, user_id, "tt0168629", None)
        result = remove_from_watched_history_util(self.db, user_id, "tt0076759")
        self.assertEqual(result, (True, "Movie removed from watched history"))

    def test_remove_movie_with_special_characters_in_imdb_id(self):
        """
        Test removing a movie with special characters in the IMDb ID.
        """
        create_account(self.db, "user12@test.com", "user12", "password123")
        cursor = self.db.cursor()
        cursor.execute("SELECT idUsers FROM Users")
        user_id = cursor.fetchone()[0]
        result = remove_from_watched_history_util(self.db, user_id, "tt@#$%^")
        self.assertEqual(result, (False, "Movie not found"))

    def test_remove_movie_with_null_user_id(self):
        """
        Test removing a movie with a null user ID.
        """
        create_account(self.db, "user13@test.com", "user13", "password123")
        result = remove_from_watched_history_util(self.db, None, "tt0076759")
        self.assertEqual(result, (False, "Movie not in watched history"))

    def test_remove_movie_with_null_imdb_id(self):
        """
        Test removing a movie with a null IMDb ID.
        """
        create_account(self.db, "user14@test.com", "user14", "password123")
        cursor = self.db.cursor()
        cursor.execute("SELECT idUsers FROM Users")
        user_id = cursor.fetchone()[0]
        result = remove_from_watched_history_util(self.db, user_id, None)
        self.assertEqual(result, (False, "Movie not found"))

    def test_remove_movie_with_large_imdb_id(self):
        """
        Test removing a movie with a very large IMDb ID.
        """
        create_account(self.db, "user15@test.com", "user15", "password123")
        cursor = self.db.cursor()
        cursor.execute("SELECT idUsers FROM Users")
        user_id = cursor.fetchone()[0]
        result = remove_from_watched_history_util(self.db, user_id, "12345678901234567890")
        self.assertEqual(result, (False, "Movie not found"))

    def test_remove_movie_with_duplicate_entries(self):
        """
        Test removing a movie with duplicate entries in the watched history.
        """
        create_account(self.db, "user16@test.com", "user16", "password123")
        cursor = self.db.cursor()
        cursor.execute("SELECT idUsers FROM Users")
        user_id = cursor.fetchone()[0]
        add_to_watched_history(self.db, user_id, "tt0076759", None)
        add_to_watched_history(self.db, user_id, "tt0076759", None)
        result = remove_from_watched_history_util(self.db, user_id, "tt0076759")
        self.assertEqual(result, (True, "Movie removed from watched history"))

    def test_remove_movie_with_invalid_timestamp_format(self):
        """
        Test removing a movie with an invalid timestamp format in the database.
        """
        create_account(self.db, "user17@test.com", "user17", "password123")
        cursor = self.db.cursor()
        cursor.execute("SELECT idUsers FROM Users")
        user_id = cursor.fetchone()[0]
        add_to_watched_history(self.db, user_id, "tt0076759", "invalid-timestamp")
        result = remove_from_watched_history_util(self.db, user_id, "tt0076759")
        self.assertEqual(result, (True, "Movie removed from watched history"))

    def test_remove_movie_with_empty_database(self):
        """
        Test removing a movie when the database is empty.
        """
        create_account(self.db, "user18@test.com", "user18", "password123")
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM WatchedHistory")
        self.db.commit()
        cursor.execute("SELECT idUsers FROM Users")
        user_id = cursor.fetchone()[0]
        result = remove_from_watched_history_util(self.db, user_id, "tt0076759")
        self.assertEqual(result, (False, "Movie not in watched history"))

    def test_remove_movie_with_sql_injection_attempt(self):
        """
        Test removing a movie with an SQL injection attempt in the IMDb ID.
        """
        create_account(self.db, "user19@test.com", "user19", "password123")
        cursor = self.db.cursor()
        cursor.execute("SELECT idUsers FROM Users")
        user_id = cursor.fetchone()[0]
        result = remove_from_watched_history_util(self.db, user_id, "tt0076759; DROP TABLE WatchedHistory;")
        self.assertEqual(result, (False, "Movie not found"))

    def test_remove_movie_with_case_insensitive_imdb_id(self):
        """
        Test removing a movie with a case-insensitive IMDb ID.
        """
        create_account(self.db, "user20@test.com", "user20", "password123")
        cursor = self.db.cursor()
        cursor.execute("SELECT idUsers FROM Users")
        user_id = cursor.fetchone()[0]
        add_to_watched_history(self.db, user_id, "tt0076759", None)
        result = remove_from_watched_history_util(self.db, user_id, "TT0076759")
        self.assertEqual(result, (False, "Movie not found"))

    def test_remove_movie_with_partial_imdb_id(self):
        """
        Test removing a movie with a partial IMDb ID.
        """
        create_account(self.db, "user21@test.com", "user21", "password123")
        cursor = self.db.cursor()
        cursor.execute("SELECT idUsers FROM Users")
        user_id = cursor.fetchone()[0]
        add_to_watched_history(self.db, user_id, "tt0076759", None)
        result = remove_from_watched_history_util(self.db, user_id, "0076759")
        self.assertEqual(result, (False, "Movie not found"))

if __name__ == "__main__":
    unittest.main()
