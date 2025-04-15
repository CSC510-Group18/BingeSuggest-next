import sys
import unittest
import warnings
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))
# pylint: disable=wrong-import-position


from src.prediction_scripts.item_based import recommend_for_new_user_d

# pylint: enable=wrong-import-position
warnings.filterwarnings("ignore")


class Tests(unittest.TestCase):
    """
    Test cases for recommender system
    """

    def test_christopher_nolan(self):
        """
        Test case 1
        """
        ts = [
            {"title": "Interstellar (2014)", "rating": 5.0},
        ]
        recommendations, _, _ = recommend_for_new_user_d(ts)
        self.assertTrue("Inception (2010)" in recommendations)

    def test_louis(self):
        """
        Test case 2
        """
        ts = [
            {"title": "Now You See Me (2013)", "rating": 5.0},
        ]
        recommendations, _, _ = recommend_for_new_user_d(ts)
        self.assertTrue("Now You See Me 2 (2016)" in recommendations)

    def test_nolan_jon(self):
        """
        Test case 3
        """
        ts = [
            {"title": "Interstellar (2014)", "rating": 5.0},
            {"title": "Iron Man (2008)", "rating": 5.0},
        ]
        recommendations, _, _ = recommend_for_new_user_d(ts)
        self.assertTrue(
            ("The Prestige (2006)" in recommendations)
            and ("Iron Man 2 (2010)" in recommendations)
        )

    def test_marvel(self):
        """
        Test case 4
        """
        ts = [
            {"title": "Captain America: The First Avenger (2011)", "rating": 5.0},
        ]
        recommendations, _, _ = recommend_for_new_user_d(ts)
        self.assertTrue(
            ("Captain America: The Winter Soldier (2014)" in recommendations)
            and ("Captain America: Civil War (2016)" in recommendations)
        )

    def test_francis(self):
        """
        Test case 5
        """
        ts = [
            {"title": "The Godfather (1972)", "rating": 5.0},
        ]
        recommendations, _, _ = recommend_for_new_user_d(ts)
        self.assertTrue(("Apocalypse Now (1979)" in recommendations))

    def test_empty_input(self):
        """
        Test case for empty input.
        """
        ts = []
        with self.assertRaises(KeyError):
            recommend_for_new_user_d(ts)

    def test_invalid_movie_title(self):
        """
        Test case for an invalid movie title (all titles are valid).
        """
        ts = [
            {"title": "Invalid Movie Title (9999)", "rating": 5.0},
        ]
        recommendations, _, _ = recommend_for_new_user_d(ts)
        self.assertNotEqual(recommendations, [])

    def test_low_rating(self):
        """
        Test case for a movie with a low rating.
        """
        ts = [
            {"title": "The Dark Knight (2008)", "rating": 1.0},
        ]
        recommendations, _, _ = recommend_for_new_user_d(ts)
        self.assertIn("Inception (2010)", recommendations)

    def test_multiple_movies_same_director(self):
        """
        Test case for multiple movies by the same director.
        """
        ts = [
            {"title": "The Dark Knight (2008)", "rating": 5.0},
            {"title": "Inception (2010)", "rating": 5.0},
        ]
        recommendations, _, _ = recommend_for_new_user_d(ts)
        self.assertIn("Interstellar (2014)", recommendations)

    def test_case_insensitivity(self):
        """
        Test case to ensure movie titles are case-insensitive.
        """
        ts = [
            {"title": "the dark knight (2008)", "rating": 5.0},
        ]
        recommendations, _, _ = recommend_for_new_user_d(ts)
        self.assertIn("Braveheart (1995)", recommendations)

    def test_special_characters_in_title(self):
        """
        Test case for a movie title with special characters.
        """
        ts = [
            {"title": "Wall-E (2008)", "rating": 5.0},
        ]
        recommendations, _, _ = recommend_for_new_user_d(ts)
        self.assertIn("Casino (1995)", recommendations)

    def test_large_input_list(self):
        """
        Test case for a large input list of movies.
        """
        ts = [{"title": f"Movie {i} (2000)", "rating": 5.0} for i in range(1, 101)]
        recommendations, _, _ = recommend_for_new_user_d(ts)
        self.assertFalse(len(recommendations) <= 10)

    def test_no_recommendations(self):
        """
        Test case where no recommendations are possible (there will always be recomendations).
        """
        ts = [
            {"title": "Unknown Movie (2025)", "rating": 5.0},
        ]
        recommendations, _, _ = recommend_for_new_user_d(ts)
        self.assertNotEqual(recommendations, [])

    def test_partial_match_title(self):
        """
        Test case for a partial match in the movie title.
        """
        ts = [
            {"title": "Dark Knight", "rating": 5.0},
        ]
        recommendations, _, _ = recommend_for_new_user_d(ts)
        self.assertNotEqual(recommendations, [])

    def test_duplicate_movies(self):
        """
        Test case for duplicate movies in the input.
        """
        ts = [
            {"title": "The Matrix (1999)", "rating": 5.0},
            {"title": "The Matrix (1999)", "rating": 5.0},
        ]
        with self.assertRaises(ValueError):
            recommend_for_new_user_d(ts)


if __name__ == "__main__":
    unittest.main()
