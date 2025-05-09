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
    create_colored_tags,
    beautify_feedback_data,
    create_movie_genres,
    send_email_to_user,
)

warnings.filterwarnings("ignore")


class Tests(unittest.TestCase):
    """
    Test cases for sending email realted functions
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
        self.db.commit()

    def test_beautify_feedback_data(self):
        """
        Test case 1
        """
        data = {"Movie 1": "Yet to watch", "Movie 2": "Like", "Movie 3": "Dislike"}
        result = beautify_feedback_data(data)
        expected_result = {
            "Liked": ["Movie 2"],
            "Disliked": ["Movie 3"],
            "Yet to Watch": ["Movie 1"],
        }

        self.assertTrue(result == expected_result)

    def test_create_colored_tags(self):
        """
        Test case 2
        """
        expected_result = '<span style="background-color: #FF1493; color: #FFFFFF; \
            padding: 5px; border-radius: 5px;">Musical</span>'
        result = create_colored_tags(["Musical"])
        self.assertTrue(result == expected_result)

    def test_create_movie_genres(self):
        """
        Test case 3
        """
        expected_result = {
            "Toy Story (1995)": ["Animation", "Comedy", "Family"],
            "Jumanji (1995)": ["Adventure", "Fantasy", "Family"],
        }

        data = [
            [
                "862",
                "Toy Story (1995)",
                "Animation|Comedy|Family",
                "tt0114709",
                " ",
                "/rhIRbceoE9lR4veEXuwCC2wARtG.jpg",
                "81",
            ],
            [
                "8844",
                "Jumanji (1995)",
                "Adventure|Fantasy|Family",
                "tt0113497",
                " ",
                "/vzmL6fP7aPKNKPRTFnZmiUfciyV.jpg",
                "104",
            ],
        ]

        movie_genre_df = pd.DataFrame(
            data,
            columns=[
                "movieId",
                "title",
                "genres",
                "imdb_id",
                "overview",
                "poster_path",
                "runtime",
            ],
        )

        result = create_movie_genres(movie_genre_df)
        self.assertTrue(result == expected_result)

    def test_send_email_to_user(self):
        """
        Test case 4
        """
        data = {
            "Liked": ["Toy Story (1995)"],
            "Disliked": ["Cutthroat Island (1995)"],
            "Yet to Watch": ["Assassins (1995)"],
        }
        with self.assertRaises(Exception):
            send_email_to_user("wrong_email", beautify_feedback_data(data))


if __name__ == "__main__":
    unittest.main()
