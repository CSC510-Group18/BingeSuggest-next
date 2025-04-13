"""
Copyright (c) 2023 Aditya Pai, Ananya Mantravadi, Rishi Singhal, Samarth Shetty
This code is licensed under MIT license (see LICENSE for details)

@author: bingesuggest-next
"""

import sys
import unittest
import warnings
import os
import bcrypt
import flask
from dotenv import load_dotenv
from pathlib import Path
import sqlite3
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.recommenderapp.utils import (
    create_account,
    login_to_account,
    get_wall_posts,
    get_username,
    get_recent_movies,
    add_friend,
    get_friends,
    submit_review,
    get_recent_friend_movies,
)

warnings.filterwarnings("ignore")


class Tests(unittest.TestCase):
    """
    Test cases for DB
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
        cursor.execute("""CREATE TABLE IF NOT EXISTS Movies (
            idMovies INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            imdb_id TEXT NOT NULL
        )""")
        # Insert test movie data for all test cases
        test_movies = [
            (2, 'Movie 2', 'tt000002'),
            (3, 'Movie 3', 'tt000003'),
            (5, 'Movie 5', 'tt000005'),
            (6, 'Movie 6', 'tt000006'),
            (11, 'Star Wars (1977)', 'tt0076759'),
            (12, 'Movie 12', 'tt000012'),
            (13, 'Forrest Gump (1994)', 'tt0109830')
        ]
        cursor.executemany("INSERT INTO Movies (idMovies, name, imdb_id) VALUES (?, ?, ?)", test_movies)
        self.db.commit()

    def test_accounts(self):
        """
        Test case 1
        """
        create_account(self.db, "abc@test.com", "someUser", "Pass")
        expected_username = "someUser"
        expected_email = "abc@test.com"
        expected_password = "Pass"
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM Users;")
        db_result = cursor.fetchall()
        actual_password = db_result[0][3]  # Password is stored as bytes from bcrypt
        self.assertTrue(len(db_result) > 0)
        self.assertEqual(expected_username, db_result[0][1])
        self.assertEqual(expected_email, db_result[0][2])
        self.assertTrue(bcrypt.checkpw(expected_password.encode('utf-8'), actual_password))
        fail = login_to_account(self.db, "someUser", "wrong")
        self.assertIsNone(fail)

    def test_get_wall_posts(self):
        """
        Test case 2
        """
        create_account(self.db, "abc@test.com", "someUser", "Pass")
        cursor = self.db.cursor()
        cursor.execute("SELECT idUsers FROM Users WHERE username='someUser'")
        db_result = cursor.fetchall()
        user = db_result[0][0]
        cursor.execute(
            "INSERT INTO Ratings(user_id, movie_id, score, review, time) VALUES (?, ?, ?, ?, ?)",
            (int(user), int(11), int(4), "this is a great movie", "2024-10-11")
        )
        self.db.commit()
        app = flask.Flask(__name__)
        a = ""
        with app.test_request_context("/"):
            a = get_wall_posts(self.db)
        self.assertEqual(a.json[0]["imdb_id"], "tt0076759")
        self.assertEqual(a.json[0]["name"], "Star Wars (1977)")
        self.assertEqual(a.json[0]["review"], "this is a great movie")
        self.assertEqual(a.json[0]["score"], 4)

    def test_get_username(self):
        """
        Test case 3
        """
        create_account(self.db, "abc@test.com", "someUser", "Pass")
        user = login_to_account(self.db, "someUser", "Pass")
        app = flask.Flask(__name__)
        username = ""
        with app.test_request_context("/"):
            username = get_username(self.db, user).json
        self.assertEqual("someUser", username)

    def test_get_recent_movies(self):
        """
        Test case 4
        """
        create_account(self.db, "abc@test.com", "someUser", "Pass")
        user = login_to_account(self.db, "someUser", "Pass")

        movies_to_review = [
            (2, 3, "2024-10-06"),
            (3, 4, "2024-10-05"),
            (5, 5, "2024-10-04"),
            (6, 2, "2024-10-03"),
            (11, 1, "2024-10-02"),
            (12, 3, "2024-10-01"),
        ]
        cursor = self.db.cursor()
        for movie in movies_to_review:
            cursor.execute(
                "INSERT INTO Ratings(user_id, movie_id, score, review, time) VALUES (?, ?, ?, ?, ?)",
                (int(user), int(movie[0]), int(movie[1]), "this is a great movie", movie[2])
            )
        self.db.commit()
        app = flask.Flask(__name__)
        recent_movies = []
        with app.test_request_context("/"):
            recent_movies = get_recent_movies(self.db, user)
        self.assertEqual(5, len(recent_movies.json))
        for i, movie in enumerate(recent_movies.json):
            self.assertEqual(movie["score"], movies_to_review[i][1])

    def test_friends(self):
        """
        Test case 5
        """
        create_account(self.db, "abc@test.com", "someUser", "Pass")
        user = login_to_account(self.db, "someUser", "Pass")
        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO Users(username, email, password) VALUES (?, ?, ?)",
            ("someFriend", "xyz@test.com", "Pass")
        )
        cursor.execute(
            "INSERT INTO Users(username, email, password) VALUES (?, ?, ?)",
            ("otherFriend", "pqr@test.com", "Pass")
        )
        app = flask.Flask(__name__)

        result = ""
        with app.test_request_context("/"):
            add_friend(self.db, "someFriend", user)
            add_friend(self.db, "otherFriend", user)
            self.db.commit()

            result = get_friends(self.db, user)

        friends = []
        friends.append(result.json[0][0])
        friends.append(result.json[1][0])
        self.assertIn("someFriend", friends)
        self.assertIn("otherFriend", friends)

        cursor.execute("SELECT idUsers FROM Users WHERE username = 'someFriend'")
        friend = cursor.fetchall()[0][0]
        movies_to_review = [
            (2, 3, "2024-06-06"),
            (3, 4, "2024-06-05"),
            (5, 5, "2024-06-04"),
            (6, 2, "2024-06-03"),
            (11, 1, "2024-06-02"),
            (12, 3, "2024-06-01"),
        ]
        for movie in movies_to_review:
            cursor.execute(
                "INSERT INTO Ratings(user_id, movie_id, score, review, time) VALUES (?, ?, ?, ?, ?)",
                (int(friend), int(movie[0]), int(movie[1]), "this is an excellent movie", movie[2])
            )
        self.db.commit()
        app = flask.Flask(__name__)
        result = []
        with app.test_request_context("/"):
            result = get_recent_friend_movies(self.db, "someFriend")
        self.assertEqual(5, len(result.json))
        for i, movie in enumerate(result.json):
            self.assertEqual(movie["score"], movies_to_review[i][1])

    def test_submit_review(self):
        """
        Test case 6
        """
        create_account(self.db, "abc@test.com", "someUser", "Pass")
        user = login_to_account(self.db, "someUser", "Pass")
        app = flask.Flask(__name__)

        result = ""
        with app.test_request_context("/"):
            submit_review(
                self.db, user, "Forrest Gump (1994)", 9, "One of the best there is!!"
            )
            self.db.commit()

            cursor = self.db.cursor()
            cursor.execute("SELECT score FROM Ratings WHERE movie_id = 13")
            result = cursor.fetchall()[0][0]
            self.assertEqual(9, int(result))


if __name__ == "__main__":
    unittest.main()
