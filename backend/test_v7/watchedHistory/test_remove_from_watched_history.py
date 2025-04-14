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


if __name__ == "__main__":
    unittest.main()
