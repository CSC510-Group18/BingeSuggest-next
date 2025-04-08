"""
Copyright (c) 2023 Aditya Pai, Ananya Mantravadi, Rishi Singhal, Samarth Shetty
This code is licensed under MIT license (see LICENSE for details)

@author: bingesuggest-next
"""

import os
import pandas as pd

app_dir = os.path.dirname(os.path.abspath(__file__))
code_dir = os.path.dirname(app_dir)
project_dir = os.path.dirname(code_dir)

class Search:
    """
    Search feature for landing page
    """

    df = pd.read_csv(project_dir + "/data/movies.csv")
    df['title_lower'] = df['title'].str.lower()

    def __init__(self):
        pass

    def search_movies(self, word):
        """
        Search for movies containing the given word
        Returns top 10 matches, prioritizing prefix matches
        """
        word = word.lower()
        
        # First find prefix matches
        prefix_matches = self.df[self.df['title_lower'].str.startswith(word)][['title', 'imdb_id']]
        
        # Then find substring matches, excluding prefix matches
        if len(prefix_matches) < 10:
            remaining_needed = 10 - len(prefix_matches)
            substring_matches = self.df[
                (~self.df['title'].isin(prefix_matches['title'])) & 
                (self.df['title_lower'].str.contains(word))
            ][['title', 'imdb_id']].head(remaining_needed)
            
            # Combine results
            results = pd.concat([prefix_matches, substring_matches])
        else:
            results = prefix_matches.head(10)
            
        return results.to_dict('records')

    def results_top_ten(self, word):
        """
        Function to get top 10 results
        """
        return self.search_movies(word)
