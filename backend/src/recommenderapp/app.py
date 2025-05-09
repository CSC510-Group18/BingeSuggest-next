"""
Copyright (c) 2023 Nathan Kohen, Nicholas Foster, Brandon Walia, Robert Kenney
This code is licensed under MIT license (see LICENSE for details)

@author: bingesuggest-next
"""

# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
# pylint: disable=import-error
import json
import sys
import os
from flask import Flask, jsonify, render_template, request, g, send_from_directory
from flask_cors import CORS
import requests
from dotenv import load_dotenv
import sqlite3
import openai  # NEW: Import OpenAI
import requests
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger

sys.path.append("../../")
from src.recommenderapp.utils import (
    beautify_feedback_data,
    format_trakt_movies_to_html,
    send_email,
    send_email_to_user,
    create_account,
    login_to_account,
    submit_review,
    get_wall_posts,
    get_recent_movies,
    get_username,
    add_friend,
    get_friends,
    get_recent_friend_movies,
    add_to_watchlist,
    get_imdb_id_by_name,
    add_to_watched_history,
    remove_from_watched_history_util,
    create_or_update_discussion,
    get_discussion,
    get_username_data,
    remove_from_watchlist,
    init_db,
    download_thumbnails
)
from src.recommenderapp.search import Search
from datetime import datetime
from src.prediction_scripts.item_based import (
    recommend_for_new_user_g,
    recommend_for_new_user_d,
    recommend_for_new_user_a,
    recommend_for_new_user_all,
)

sys.path.remove("../../")

app = Flask(__name__)
app.secret_key = "secret key"

cors = CORS(app, resources={r"/*": {"origins": "*"}})
user = {1: None}
comments: []

# Load environment variables early so that OpenAI API key is available.
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")  # NEW: Set the OpenAI API key

def get_recent_movies_from_trakt():
    """Fetch top 10 new movies from the past month using Trakt API"""
    try:

        TRAKT_CLIENT_ID = os.getenv("TRAKT_CLIENT_ID")
        TRAKT_CLIENT_SECRET = os.getenv("TRAKT_CLIENT_SECRET")
        URL = "https://api.trakt.tv/movies/trending"

        # Headers for the API request
        headers = {
            "Content-Type": "application/json",
            "trakt-api-version": "2",
            "trakt-api-key": TRAKT_CLIENT_ID,
            "trakt-api-secret": TRAKT_CLIENT_SECRET
        }

        # Make the API request
        response = requests.get(URL, headers=headers)
        movies = response.json()

        return [{
            "title": movie['movie']["title"],
            "imdb_id": movie['movie']["ids"]["imdb"]
        } for movie in movies[:10]]

    except Exception as e:
        app.logger.error(f"Error fetching movies from Trakt: {str(e)}")
        return []


def send_weekly_recommendations():
    """Sends weekly recommendations to all users"""
    with app.app_context():
        try:
            recent_movies = format_trakt_movies_to_html(get_recent_movies_from_trakt())
            if not recent_movies:
                app.logger.error("No movies found from Trakt API")
                return

            # Get all users with emails
            before_request()
            cursor = g.db.cursor()
            cursor.execute("SELECT email FROM Users WHERE email IS NOT NULL;")
            users = cursor.fetchall()
            print('users', users)

            # Send emails to all users
            print('starting email sending')
            for (email_address,) in users:
                try:
                    email = MIMEMultipart("alternative")
                    email["To"] = email_address
                    email["Subject"] = "Newly Released Movies for You"
                    email.attach(MIMEText(recent_movies, "html"))

                    send_email(email, email_address)

                    app.logger.info(f"Sent recommendations to {email_address}")
                except Exception as e:
                    app.logger.error(f"Error sending email to {email_address}: {str(e)}")

        except Exception as e:
            app.logger.error(f"Error in weekly recommendations: {str(e)}")


# Run every Monday at 9 AM
scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(
    send_weekly_recommendations,
    # This was left for testing the send_weekly_recommendations function.
    # trigger=DateTrigger(run_date=datetime.now() + timedelta(seconds=5)),
    trigger=CronTrigger(
        day_of_week="mon",
        hour=9,
        minute=0,
        timezone="UTC",
        week="*/4"  # Send updates once a month
    ),
    name="Weekly Recommendations"
)
scheduler.start()


@app.route("/")
def login_page():
    """
    Renders the login page.
    """
    return render_template("login.html")


@app.route("/profile")
def profile_page():
    """
    Renders the login page.
    """
    if user[1] is not None:
        return render_template("profile.html")
    return render_template("login.html")


@app.route("/wall")
def wall_page():
    """
    Renders the wall page.
    """
    if user[1] is not None or user[1] == "guest":
        return render_template("wall.html")
    return render_template("login.html")


@app.route("/review")
def review_page():
    """
    Renders the review page.
    """
    if user[1] is not None or user[1] == "guest":
        return render_template("review.html")
    return render_template("login.html")


@app.route("/landing")
def landing_page():
    """
    Renders the landing page.
    """
    if user[1] is not None or user[1] == "guest":
        return render_template("landing_page.html")
    return render_template("login.html")


@app.route("/search_page")
def search_page():
    """
    Renders the search page.
    """
    if user[1] is not None or user[1] == "guest":
        return render_template("search_page.html")
    return render_template("login.html")


@app.route("/genreBased", methods=["POST"])
def predict_g():
    """
    Predicts movie recommendations based on user ratings.
    """
    data = json.loads(request.data)
    data1 = data["movie_list"]
    training_data = []
    for movie in data1:
        movie_with_rating = {"title": movie, "rating": 5.0}
        if movie_with_rating not in training_data:
            training_data.append(movie_with_rating)
    recommendations, genres, imdb_id = recommend_for_new_user_g(training_data)
    recommendations, genres, imdb_id = recommendations[:10], genres[:10], imdb_id[:10]
    resp = {"recommendations": recommendations, "genres": genres, "imdb_id": imdb_id}
    print(resp)
    return resp


@app.route("/dirBased", methods=["POST"])
def predict_d():
    """
    Predicts movie recommendations based on user ratings.
    """
    data = json.loads(request.data)
    data1 = data["movie_list"]
    training_data = []
    for movie in data1:
        movie_with_rating = {"title": movie, "rating": 5.0}
        if movie_with_rating not in training_data:
            training_data.append(movie_with_rating)
    recommendations, genres, imdb_id = recommend_for_new_user_d(training_data)
    recommendations, genres, imdb_id = recommendations[:10], genres[:10], imdb_id[:10]
    resp = {"recommendations": recommendations, "genres": genres, "imdb_id": imdb_id}
    return resp


@app.route("/actorBased", methods=["POST"])
def predict_a():
    """
    Predicts movie recommendations based on user ratings.
    """
    data = json.loads(request.data)
    data1 = data["movie_list"]
    training_data = []
    for movie in data1:
        movie_with_rating = {"title": movie, "rating": 5.0}
        if movie_with_rating not in training_data:
            training_data.append(movie_with_rating)
    recommendations, genres, imdb_id = recommend_for_new_user_a(training_data)
    recommendations, genres, imdb_id = recommendations[:10], genres[:10], imdb_id[:10]
    resp = {"recommendations": recommendations, "genres": genres, "imdb_id": imdb_id}
    return resp


@app.route("/all", methods=["POST"])
def predict_all():
    """
    Predicts movie recommendations based on user ratings.
    """
    data = json.loads(request.data)
    data1 = data["movie_list"]
    training_data = []
    for movie in data1:
        movie_with_rating = {"title": movie, "rating": 5.0}
        if movie_with_rating not in training_data:
            training_data.append(movie_with_rating)
    recommendations, genres, imdb_id = recommend_for_new_user_all(training_data)
    recommendations, genres, imdb_id = recommendations[:10], genres[:10], imdb_id[:10]
    resp = {"recommendations": recommendations, "genres": genres, "imdb_id": imdb_id}
    return resp


@app.route("/search", methods=["POST"])
def search():
    """
    Handles movie search requests.
    """
    term = request.form["q"]
    finder = Search()
    filtered_dict = finder.results_top_ten(term)
    out = [(t["title"], os.path.join("http://localhost:5000/thumbnails", f"{t['imdb_id']}.jpg")) for t in filtered_dict]
    resp = jsonify(out)
    resp.status_code = 200
    return resp


@app.route("/", methods=["POST"])
def create_acc():
    """
    Handles creating a new account
    """
    data = json.loads(request.data)
    create_account(g.db, data["email"], data["username"], data["password"])
    return request.data


@app.route("/out", methods=["POST"])
def signout():
    """
    Handles signing out the active user
    """
    user[1] = None
    return request.data


@app.route("/log", methods=["POST"])
def login():
    """
    Handles logging in the active user
    """
    data = json.loads(request.data)
    resp = login_to_account(g.db, data["username"], data["password"])
    if resp is None:
        return 400
    user[1] = resp
    return request.data


@app.route("/friend", methods=["POST"])
def friend():
    """
    Handles adding a new friend
    """
    data = json.loads(request.data)
    add_friend(g.db, data["username"], user[1])
    return request.data


@app.route("/guest", methods=["POST"])
def guest():
    """
    Sets the user to be a guest user
    """
    data = json.loads(request.data)
    user[1] = data["guest"]
    return request.data


@app.route("/review", methods=["POST"])
def review():
    """
    Handles the submission of a movie review
    """
    data = request.get_json()
    movie_name = data.get("movie")[0]
    data["imdb_id"] = get_imdb_id_by_name(g.db, movie_name)
    print(get_imdb_id_by_name(g.db, movie_name))
    submit_review(g.db, user[1], movie_name, data.get("score"), data.get("review"))
    return request.data


@app.route("/getWallData", methods=["GET"])
def wall_posts():
    """
    Gets the posts for the wall
    """
    return get_wall_posts(g.db)


@app.route("/getRecentMovies", methods=["GET"])
def recent_movies():
    """
    Gets the recent movies of the active user
    """
    return get_recent_movies(g.db, user[1])


@app.route("/getRecentFriendMovies", methods=["POST"])
def recent_friend_movies():
    """
    Gets the recent movies of a certain friend
    """
    data = json.loads(request.data)
    return get_recent_friend_movies(g.db, str(data))


@app.route("/getUserName", methods=["GET"])
def username():
    """
    Gets the username of the active user
    """
    return get_username(g.db, user[1])


@app.route("/getFriends", methods=["GET"])
def get_friend():
    """
    Gets the friends of the active user
    """
    return get_friends(g.db, user[1])


@app.route("/feedback", methods=["POST"])
def feedback():
    """
    Handles user feedback submission and mails the results.
    """
    data = json.loads(request.data)
    return data


@app.route("/sendMail", methods=["POST"])
def send_mail():
    """
    Handles user feedback submission and mails the results.
    """
    data = json.loads(request.data)
    user_email = data["email"]
    send_email_to_user(user_email, beautify_feedback_data(data))
    return data


@app.route("/add_to_watchlist", methods=["POST"])
def add_movie_to_watchlist():
    """
    Adds a movie to the user's watchlist.
    """
    print("Entered func")
    data = request.get_json()
    print(data)
    movie_name = data.get("movieName")[0]
    print(movie_name)
    imdb_id = (
        get_imdb_id_by_name(g.db, movie_name) if movie_name else data.get("imdb_id")
    )
    print("Got imdb id")
    if not imdb_id:
        return jsonify({"status": "error", "message": "Movie not found"}), 404
    print("imdb id is present")

    cursor = g.db.cursor()
    cursor.execute("SELECT idMovies FROM Movies WHERE imdb_id = ?", [imdb_id])
    movie_id_result = cursor.fetchone()
    print("Selected movie.")
    if movie_id_result:
        movie_id = movie_id_result[0]
        user_id = user[1]  # Assuming 'user' holds the currently logged-in user's ID
        print("Before was added.")
        # Add to watchlist and check if it was added successfully
        was_added = add_to_watchlist(g.db, user_id, movie_id)
        print(was_added)
        if was_added:
            return (
                jsonify({"status": "success", "message": "Movie added to watchlist"}),
                200,
            )
        else:
            return (
                jsonify({"status": "info", "message": "Movie already in watchlist"}),
                200,
            )
    else:
        return jsonify({"status": "error", "message": "Movie not found"}), 404


@app.route("/watchlist", methods=["GET"])
def watchlist_page():
    """
    Renders the watchlist page.
    """
    if user[1] is not None or user[1] == "guest":
        return render_template("watchlist.html")
    return render_template("login.html")


@app.route("/getWatchlistData", methods=["GET"])
def get_watchlist():
    """
    Retrieves the current user's watchlist.
    """
    user_id = user[1]  # Assuming 'user' holds the currently logged-in user's ID
    cursor = g.db.cursor()
    cursor.execute(
        """
        SELECT m.name, m.imdb_id, w.time
        FROM Watchlist w
        JOIN Movies m ON w.movie_id = m.idMovies
        WHERE w.user_id = ?
        ORDER BY w.time DESC;
        """,
        [user_id],
    )
    watchlist = cursor.fetchall()
    return jsonify(watchlist), 200


@app.route("/deleteWatchlistData", methods=["POST"])
def delete_watchlist_data():
    """
    Retrieves the current user
    """
    user_id = user[1]  # Assuming 'user' holds the currently logged-in user's ID
    imdb_id = json.loads(request.data)
    idMovies, _ = remove_from_watchlist(g.db, user_id, imdb_id)

    if idMovies:
        return (
            jsonify({"status": "success", "message": "Movie deleted from watchlist"}),
            200,
        )
    else:
        return (
            jsonify(
                {"status": "info", "message": "Failed to delete movie from watchlist"}
            ),
            200,
        )


@app.route("/get_api_key", methods=["GET"])
def get_api_key():
    """
    Provides the OMDB API key securely to the frontend.
    """
    if user[1] is not None and user[1] != "guest":
        return jsonify({"apikey": os.getenv("OMDB_API_KEY")})
    return jsonify({"error": "Unauthorized"}), 403


@app.route("/add_to_watched_history", methods=["POST"])
def add_movie_to_watched_history():
    """
    Adds a movie to the user's watched history.
    """
    print("Entered add_to_watched_history function")
    data = request.get_json()
    print("Request data:", data)

    # Get IMDb ID or movie name
    imdb_id = data.get("imdb_id")
    if not imdb_id:
        movie_name = data.get("movieName")[0]
        imdb_id = get_imdb_id_by_name(g.db, movie_name) if movie_name else None

    if not imdb_id:
        return jsonify({"status": "error", "message": "Movie not found"}), 404

    print("IMDb ID obtained:", imdb_id)
    user_id = user[1]  # Assuming 'user' holds the currently logged-in user's ID

    # Call utility function to add the movie
    was_added, message = add_to_watched_history(
        g.db, user_id, imdb_id, data.get("watched_date")
    )
    status = "success" if was_added else "info"
    return jsonify({"status": status, "message": message}), 200


@app.route("/watched_history", methods=["GET"])
def watched_history_page():
    """
    Renders the watched history page.
    """
    if user[1] is not None or user[1] == "guest":
        return render_template("watched_history.html")
    return render_template("login.html")


@app.route("/getWatchedHistoryData", methods=["GET"])
def get_watched_history():
    """
    Retrieves the current user's watched history.
    """
    user_id = user[1]  # Assuming 'user' holds the currently logged-in user's ID
    cursor = g.db.cursor()
    cursor.execute(
        """
        SELECT m.name AS movie_name, m.imdb_id, wh.watched_date
        FROM WatchedHistory wh
        JOIN Movies m ON wh.movie_id = m.idMovies
        WHERE wh.user_id = ?
        ORDER BY wh.watched_date DESC;
        """,
        [user_id],
    )
    watched_history = cursor.fetchall()
    return jsonify(watched_history), 200


@app.route("/removeFromWatchedHistory", methods=["POST"])
def remove_from_watched_history():
    """
    Removes a movie from the user's watched history.
    """
    print("Entered remove_from_watched_history function")
    data = request.get_json()
    print("Request data:", data)

    imdb_id = data.get("imdb_id")
    if not imdb_id:
        return jsonify({"status": "error", "message": "IMDb ID not provided"}), 400

    user_id = user[1]  # Assuming 'user' holds the currently logged-in user's ID

    # Call utility function to remove the movie
    was_removed, message = remove_from_watched_history_util(g.db, user_id, imdb_id)
    status = "success" if was_removed else "error"
    return jsonify({"status": status, "message": message}), 200


@app.route("/success")
def success():
    """
    Renders the success page.
    """
    return render_template("success.html")


@app.route("/movie/<id>")
def moviePage(id):
    """
    Renders the movie page with description and details and discussion forum
    """
    user_id = user[1]
    us = ""
    if user_id is None or user_id == "guest":
        us = "Anonymous"
    else:
        us = get_username_data(g.db, user_id)
    r = requests.get(
        "http://www.omdbapi.com/", params={"i": id, "apikey": os.getenv("OMDB_API_KEY")}
    )
    data = {"movieData": r.json(), "user": us}
    return render_template("movie.html", data=data)


@app.route("/movieDiscussion/<id>", methods=["GET"])
def getMovieDisccusion(id):
    """
    Returns the discussion store for the corresponding imdbId
    """
    return get_discussion(g.db, id)


@app.route("/movieDiscussion/<id>", methods=["POST"])
def postCommentOnMovieDisccusion(id):
    """
    Returns the discussion store for the corresponding imdbId
    """
    data = request.get_json()
    data["imdb_id"] = id
    return create_or_update_discussion(g.db, data)


@app.route("/get_imdb_id", methods=["POST"])
def get_imdb_id():
    """
    Fetches the IMDb ID for a given movie title.
    """
    data = request.get_json()
    movie_name = data.get("movie_name")[0]

    if not movie_name:
        return jsonify({"error": "Missing movie name"}), 400

    # Fetch IMDb ID using existing function
    imdb_id = get_imdb_id_by_name(g.db, movie_name)

    if imdb_id:
        return jsonify({"imdb_id": imdb_id}), 200
    else:
        return jsonify({"error": "IMDb ID not found"}), 404


import logging

logging.basicConfig(level=logging.DEBUG)

import logging
import openai
from flask import Flask, jsonify, request

logging.basicConfig(level=logging.DEBUG)


@app.route("/ai_recommendations", methods=["POST"])
def ai_recommendations():
    try:
        data = request.get_json()
        logging.debug(f"Received AI request: {data}")

        user_query = data.get("query", "")

        if not user_query:
            logging.error("Query is empty")
            return jsonify({"error": "Error occurred"}), 400

        # NEW OpenAI API usage (version 1.0+)
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a movie recommendation AI. Please provide recommendations in a JSON array format with just movie titles, the only key should be movies, I should be able to call json.loads(response.choices[0].message.content) and get a list of movies."},
                {
                    "role": "user", 
                    "content": f"Recommend 5 movies based on: {user_query}. Return just the movie titles in a JSON array."
                },
            ],
        )

        print(response.choices[0].message.content)

        # Parse the JSON response
        try:
            movie_titles = json.loads(response.choices[0].message.content)["movies"]
            recommendations = []
            
            # Look up each movie in database
            for title in movie_titles:
                print("Searching for: ", title)
                imdb_id = get_imdb_id_by_name(g.db, title)
                if imdb_id:
                    recommendations.append(
                        (title, "localhost:5000/thumbnails/" + imdb_id + ".jpg")
                    )

            logging.debug(f"AI Recommendations with thumbnails: {recommendations}")
            print(recommendations)
            return jsonify({"recommendations": recommendations})

        except json.JSONDecodeError:
            logging.error("Failed to parse AI response as JSON")
            return jsonify({"error": "Invalid AI response format"}), 500

    except Exception as e:
        logging.error(f"Error in AI recommendations: {str(e)}", exc_info=True)
        return jsonify({"error": "Error occurred"}), 500


@app.before_request
def before_request():
    """
    Opens the db connection.
    """

    # initialize database
    init_db()
    
    # Create a new connection for each request
    g.db = sqlite3.connect('movies.db')
    g.db.row_factory = sqlite3.Row  # This enables column access by name


@app.after_request
def after_request(response):
    """
    Closes the db connection.
    """
    return response


# Add a route to serve thumbnails
@app.route("/thumbnails/<path:filename>")
def serve_thumbnail(filename):
    """
    Serves thumbnail images from the thumbnails directory.
    """
    PATH = os.path.join(os.path.dirname(__file__), "thumbnails")
    thumbnail_path = os.path.join(PATH, filename)
    if os.path.exists(thumbnail_path):
        return send_from_directory(PATH, filename)
    else:
        return jsonify({"error": "Thumbnail not found"}), 404


if __name__ == "__main__":
    print("Downloading thumbnails... (Roughly 600MB)")
    download_thumbnails()
    print("Starting server...")
    app.run(port=5000)
