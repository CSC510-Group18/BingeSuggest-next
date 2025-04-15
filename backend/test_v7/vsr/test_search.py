"""
Copyright (c) 2023 Aditya Pai, Ananya Mantravadi, Rishi Singhal, Samarth Shetty
This code is licensed under MIT license (see LICENSE for details)

@author: bingesuggest-next

Test suit for search feature
"""

import sys
import unittest
import warnings
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))
# pylint: disable=wrong-import-position
from src.recommenderapp.search import Search

# pylint: enable=wrong-import-position

warnings.filterwarnings("ignore")


class Tests(unittest.TestCase):
    """
    Test cases for search feature
    """

    def test_search_toy(self):
        """
        Test case 1
        """
        search_word = "toy"
        finder = Search()
        filtered_dict = finder.results_top_ten(search_word)
        filtered_dict = [item['title'] for item in filtered_dict]
        expected_resp = [
            "Toy Story (1995)",
            "Toys (1992)",
            "Toy Story 2 (1999)",
            "Toy Soldiers (1991)",
            "Toy Story 3 (2010)",
            "Toys in the Attic (1963)",
            "Toy Story of Terror! (2013)",
            "Toy Story That Time Forgot (2014)",
            "Toys in the Attic (2009)",
            "Toy Soldiers (1984)",
        ]
        self.assertTrue(filtered_dict == expected_resp)

    def test_search_2001(self):
        """
        Test case 4
        """
        search_word = "2001"
        finder = Search()
        filtered_dict = finder.results_top_ten(search_word)
        filtered_dict = [item['title'] for item in filtered_dict]
        expected_resp = [
            "2001: A Space Odyssey (1968)",
            "2001 Maniacs (2005)",
            "2001: A Space Travesty (2000)",
            "Songcatcher (2001)",
            "Antitrust (2001)",
            "Double Take (2001)",
            "Save the Last Dance (2001)",
            "The Pledge (2001)",
            "The Amati Girls (2001)",
            "Sugar & Spice (2001)",
        ]

        self.assertTrue(filtered_dict == expected_resp)

    def test_search_empty_string(self):
        """
        Test case for an empty search string.
        """
        search_word = ""
        finder = Search()
        filtered_dict = finder.results_top_ten(search_word)
        filtered_dict = [item['title'] for item in filtered_dict]
        expected_resp = [
            "Toy Story (1995)",
            "Jumanji (1995)",
            "Grumpier Old Men (1995)",
            "Waiting to Exhale (1995)",
            "Father of the Bride Part II (1995)",
            "Heat (1995)",
            "Sabrina (1995)",
            "Tom and Huck (1995)",
            "Sudden Death (1995)",
            "GoldenEye (1995)",
        ]
        self.assertEqual(filtered_dict, expected_resp)

    def test_search_special_characters(self):
        """
        Test case for a search string with special characters.
        """
        search_word = "@#$%"
        finder = Search()
        filtered_dict = finder.results_top_ten(search_word)
        self.assertEqual(filtered_dict, [])

    def test_search_numeric_string(self):
        """
        Test case for a numeric search string.
        """
        search_word = "12345"
        finder = Search()
        filtered_dict = finder.results_top_ten(search_word)
        self.assertEqual(filtered_dict, [])

    def test_search_case_insensitivity(self):
        """
        Test case to ensure search is case-insensitive.
        """
        search_word = "TOY"
        finder = Search()
        filtered_dict = finder.results_top_ten(search_word)
        filtered_dict = [item['title'] for item in filtered_dict]
        expected_resp = [
            "Toy Story (1995)",
            "Toys (1992)",
            "Toy Story 2 (1999)",
            "Toy Soldiers (1991)",
            "Toy Story 3 (2010)",
            "Toys in the Attic (1963)",
            "Toy Story of Terror! (2013)",
            "Toy Story That Time Forgot (2014)",
            "Toys in the Attic (2009)",
            "Toy Soldiers (1984)",
        ]
        self.assertTrue(filtered_dict == expected_resp)

    def test_search_partial_match(self):
        """
        Test case for a partial match in the search string.
        """
        search_word = "Toy St"
        finder = Search()
        filtered_dict = finder.results_top_ten(search_word)
        filtered_dict = [item['title'] for item in filtered_dict]
        expected_resp = [
            "Toy Story (1995)",
            "Toy Story 2 (1999)",
            "Toy Story 3 (2010)",
            "Toy Story of Terror! (2013)",
            "Toy Story That Time Forgot (2014)",
        ]
        self.assertTrue(filtered_dict == expected_resp)

    def test_search_no_results(self):
        """
        Test case for a search string that yields no results.
        """
        search_word = "NonExistentMovie"
        finder = Search()
        filtered_dict = finder.results_top_ten(search_word)
        self.assertEqual(filtered_dict, [])

    def test_search_long_string(self):
        """
        Test case for a very long search string.
        """
        search_word = "a" * 1000
        finder = Search()
        filtered_dict = finder.results_top_ten(search_word)
        self.assertEqual(filtered_dict, [])

    def test_search_substring_match(self):
        """
        Test case for a substring match in the search string.
        """
        search_word = "Story"
        finder = Search()
        filtered_dict = finder.results_top_ten(search_word)
        filtered_dict = [item['title'] for item in filtered_dict]
        expected_resp = [
            "Storytelling (2001)",
            "Storyville (1992)",
            "Story of Women (1988)",
            "Story of a Love Affair (1950)",
            "Story of a Prostitute (1965)",
            "Story of My Death (2013)",
            "Story of Night (1979)",
            "Toy Story (1995)",
            "The Neverending Story III: Escape from Fantasia (1994)",
            "A Pyromaniac's Love Story (1995)"
        ]
        self.assertEquals(filtered_dict, expected_resp)

    def test_search_prefix_priority(self):
        """
        Test case to ensure prefix matches are prioritized.
        """
        search_word = "Toy"
        finder = Search()
        filtered_dict = finder.results_top_ten(search_word)
        filtered_dict = [item['title'] for item in filtered_dict]
        expected_resp = [
            "Toy Story (1995)",
            "Toys (1992)",
            "Toy Story 2 (1999)",
            "Toy Soldiers (1991)",
            "Toy Story 3 (2010)",
            "Toys in the Attic (1963)",
            "Toy Story of Terror! (2013)",
            "Toy Story That Time Forgot (2014)",
            "Toys in the Attic (2009)",
            "Toy Soldiers (1984)",
        ]
        self.assertTrue(filtered_dict == expected_resp)

    def test_search_numeric_and_text_combination(self):
        """
        Test case for a search string with a combination of numbers and text.
        """
        search_word = "2001 Space"
        finder = Search()
        filtered_dict = finder.results_top_ten(search_word)
        filtered_dict = [item['title'] for item in filtered_dict]
        self.assertEqual(filtered_dict, [])


if __name__ == "__main__":
    unittest.main()
