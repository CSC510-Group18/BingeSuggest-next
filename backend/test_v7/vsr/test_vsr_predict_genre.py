import sys
import unittest
import warnings
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))
# pylint: disable=wrong-import-position


from src.prediction_scripts.item_based import recommend_for_new_user_g

# pylint: enable=wrong-import-position
warnings.filterwarnings("ignore")


class Tests(unittest.TestCase):
    """
    Test cases for recommender system
    """

    def test_musicals(self):
        """
        Test case 1
        """
        ts = [
            {"title": "La La Land (2016)", "rating": 5.0},
        ]
        recommendations, _, _ = recommend_for_new_user_g(ts)
        self.assertTrue("Shall We Dance? (1996)" in recommendations)

    def test_horror(self):
        """
        Test case 2
        """
        ts = [
            {"title": "Insidious (2010)", "rating": 5.0},
        ]
        recommendations, _, _ = recommend_for_new_user_g(ts)
        self.assertTrue("The Exorcist (1973)" in recommendations)

    def test_sciFi(self):
        """
        Test case 3
        """
        ts = [
            {"title": "Interstellar (2014)", "rating": 5.0},
        ]
        recommendations, _, _ = recommend_for_new_user_g(ts)
        self.assertTrue(("The Martian (2015)" in recommendations))

    def test_sciFi_action(self):
        """
        Test case 4
        """
        ts = [
            {"title": "Iron Man (2008)", "rating": 5.0},
        ]
        recommendations, _, _ = recommend_for_new_user_g(ts)
        self.assertTrue(("Star Wars (1977)" in recommendations))

    def test_thriller(self):
        """
        Test case 5
        """
        ts = [
            {"title": "Now You See Me (2013)", "rating": 5.0},
            {"title": "Ocean's Eleven (2001)", "rating": 5.0},
        ]
        recommendations, _, _ = recommend_for_new_user_g(ts)
        self.assertTrue(("The Dark Knight (2008)" in recommendations))

    def test_empty_input(self):
        """
        Test case for empty input.
        """
        ts = []
        with self.assertRaises(KeyError):
            recommend_for_new_user_g(ts)

    def test_nonexistent_movie_title(self):
        """
        Test case for a nonexistent movie title.
        """
        ts = [
            {"title": "Invalid Movie Title (9999)", "rating": 5.0},
        ]
        recommendations, _, _ = recommend_for_new_user_g(ts)
        self.assertNotEqual(recommendations, [])

    def test_low_rating(self):
        """
        Test case for a movie with a low rating.
        """
        ts = [
            {"title": "The Godfather (1972)", "rating": 1.0},
        ]
        recommendations, _, _ = recommend_for_new_user_g(ts)
        self.assertNotIn("The Godfather Part II (1974)", recommendations)

    def test_multiple_genres(self):
        """
        Test case for a movie with multiple genres.
        """
        ts = [
            {"title": "The Dark Knight (2008)", "rating": 5.0},
        ]
        recommendations, _, _ = recommend_for_new_user_g(ts)
        self.assertIn("Heat (1995)", recommendations)

    def test_duplicate_movies(self):
        """
        Test case for duplicate movies in the input.
        """
        ts = [
            {"title": "The Matrix (1999)", "rating": 5.0},
            {"title": "The Matrix (1999)", "rating": 5.0},
        ]
        with self.assertRaises(ValueError):
            recommend_for_new_user_g(ts)

    def test_partial_match_title(self):
        """
        Test case for a partial match in the movie title.
        """
        ts = [
            {"title": "Matrix (1999)", "rating": 5.0},
        ]
        recommendations, _, _ = recommend_for_new_user_g(ts)
        self.assertNotEqual(recommendations, [])

    def test_case_insensitivity(self):
        """
        Test case to ensure movie titles are case-insensitive.
        """
        ts = [
            {"title": "the matrix (1999)", "rating": 5.0},
        ]
        recommendations, _, _ = recommend_for_new_user_g(ts)
        self.assertNotIn("The Matrix Reloaded (2003)", recommendations)

    def test_special_characters_in_title(self):
        """
        Test case for a movie title with special characters.
        """
        ts = [
            {"title": "Wall-E (2008)", "rating": 5.0},
        ]
        recommendations, _, _ = recommend_for_new_user_g(ts)
        self.assertIn("Persuasion (1995)", recommendations)

    def test_large_input_list(self):
        """
        Test case for a large input list of movies.
        """
        ts = [{"title": f"Movie {i} (2000)", "rating": 5.0} for i in range(1, 101)]
        recommendations, _, _ = recommend_for_new_user_g(ts)
        self.assertFalse(len(recommendations) <= 10)

    def test_no_recommendations(self):
        """
        Test case where no recommendations are possible (there will always be recomendations).
        """
        ts = [
            {"title": "Unknown Movie (2025)", "rating": 5.0},
        ]
        recommendations, _, _ = recommend_for_new_user_g(ts)
        self.assertNotEqual(recommendations, [])


if __name__ == "__main__":
    unittest.main()
