"""
Copyright (c) 2023 Aditya Pai, Ananya Mantravadi, Rishi Singhal, Samarth Shetty
This code is licensed under MIT license (see LICENSE for details)

@author: bingesuggest-next
"""
import pandas as pd
import os
import numpy as np

APP_DIR = os.path.dirname(os.path.abspath(__file__))
CODE_DIR = os.path.dirname(APP_DIR)
PROJECT_DIR = os.path.dirname(CODE_DIR)
MOVIES_CSV_PATH = os.path.join(PROJECT_DIR, "data", "movies.csv")

_MOVIES_DF = None
_MOVIES_GENRE_MATRIX = None

def load_and_preprocess_data():
    """
    Loads and preprocesses movie data. Should only be called once.
    Stores results in global variables _MOVIES_DF and _MOVIES_GENRE_MATRIX.
    """
    # The global keyword is used to ensure we modify the global variables and don't create new local variables to the function
    global _MOVIES_DF, _MOVIES_GENRE_MATRIX

    movies = pd.read_csv(MOVIES_CSV_PATH)

    movies_genre_filled = movies.copy(deep=True)
    all_genres = set()
    split_genres = []

    for genres_str in movies['genres']:
        if pd.isna(genres_str):
            split_genres.append([])
            continue
        current_genres = genres_str.split('|')
        split_genres.append(current_genres)
        all_genres.update(current_genres)

    for genre in all_genres:
        movies_genre_filled[genre] = 0

    for idx, genre_list in enumerate(split_genres):
        for genre in genre_list:
            movies_genre_filled.loc[idx, genre] = 1

    genre_columns = list(all_genres)
    movies_genre_matrix = movies_genre_filled[['movieId'] + genre_columns].copy()
    movies_genre_matrix.set_index('movieId', inplace=True)

    processed_movies = movies.copy(deep=True)

    # Clean and normalize IMDb ratings
    processed_movies["imdb_ratings"] = processed_movies["imdb_ratings"].replace({"Error": np.nan, "No Rating Found": np.nan})
    processed_movies["imdb_ratings"] = pd.to_numeric(processed_movies["imdb_ratings"], errors='coerce').fillna(1.0)

    max_rating = processed_movies["imdb_ratings"].max()
    max_rating = max_rating if max_rating > 0 else 10.0

    processed_movies["normalized_imdb_rating"] = processed_movies["imdb_ratings"] / max_rating

    # Pre-split directors and actors into sets for faster intersection later
    processed_movies['director_set'] = processed_movies['director'].apply(
        lambda x: set(d.strip() for d in x.split(',')) if pd.notna(x) else set()
    )
    processed_movies['actors_set'] = processed_movies['actors'].apply(
        lambda x: set(a.strip() for a in x.split(',')) if pd.notna(x) else set()
    )

    # movieId as index for easier lookups
    processed_movies.set_index('movieId', inplace=True)

    _MOVIES_DF = processed_movies
    _MOVIES_GENRE_MATRIX = movies_genre_matrix


def recommend_for_new_user(user_rating, gw, dw, aw):
    """
    Generates a list of recommended movie titles for a new user based on their ratings.
    Uses pre-calculated movie data and genre matrix for efficiency.
    """
    if _MOVIES_DF is None or _MOVIES_GENRE_MATRIX is None:
        load_and_preprocess_data()

    movies_df = _MOVIES_DF
    movies_genre_matrix = _MOVIES_GENRE_MATRIX

    user = pd.DataFrame(user_rating)

    # Create a df of all the movies that appear in the system DB and the users list of movies, and of those only keep the movieId and title
    user_movie_ids_df = movies_df.reset_index()[movies_df.reset_index()["title"].isin(user["title"])][['movieId', 'title']]

    user_ratings = pd.merge(user_movie_ids_df, user, on="title", how="inner")

    user_ratings.set_index('movieId', inplace=True)

    common_movie_ids = movies_genre_matrix.index.intersection(user_ratings.index)

    user_genre = movies_genre_matrix.loc[common_movie_ids]
    user_ratings = user_ratings.loc[common_movie_ids]

    user_profile = user_genre.T.dot(user_ratings.rating.astype(float))

    recommendations = (movies_genre_matrix.dot(user_profile)) / user_profile.sum()

    top_recommendations = movies_df.copy()
    top_recommendations['recommended'] = recommendations

    user_rated_movies_details = movies_df.loc[user_ratings.index] # Get details using index lookup
    user_directors = set().union(*user_rated_movies_details['director_set'])
    user_actors = set().union(*user_rated_movies_details['actors_set'])

    top_recommendations["director_match_score"] = top_recommendations["director_set"].apply(
        lambda movie_directors: len(movie_directors.intersection(user_directors))
    )
    top_recommendations["actor_match_score"] = top_recommendations["actors_set"].apply(
        lambda movie_actors: len(movie_actors.intersection(user_actors))
    )

    # Increase weights for director, actor scores, and IMDb rating in the final recommendation score
    top_recommendations["final_score"] = (
        gw * top_recommendations["recommended"]
        + dw * top_recommendations["director_match_score"]
        + aw * top_recommendations["actor_match_score"]
        + 0.4 * top_recommendations["normalized_imdb_rating"]
    )

    # Filter out movies the user has already rated
    rated_titles = set(user["title"])
    candidates = top_recommendations[~top_recommendations["title"].isin(rated_titles)]

    final_recommendations = candidates.nlargest(201, 'final_score')

    return (
        list(final_recommendations["title"]),
        list(final_recommendations["genres"]),
        list(final_recommendations["imdb_id"]),
    )


def recommend_for_new_user_g(user_rating):
    return recommend_for_new_user(user_rating, 1, 0, 0)


def recommend_for_new_user_d(user_rating):
    return recommend_for_new_user(user_rating, 0.1, 1, 0.1)


def recommend_for_new_user_a(user_rating):
    return recommend_for_new_user(user_rating, 0.1, 0.1, 1)


def recommend_for_new_user_all(user_rating):
    return recommend_for_new_user(user_rating, 0.5, 0.3, 0.3)
