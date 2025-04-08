#!/usr/bin/env python3
import datetime
import logging
import smtplib
import bcrypt
from smtplib import SMTPException
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import jsonify
import json
import shutil
import tempfile
import zipfile

import pandas as pd
import os
import sqlite3

def init_db(override=False):
    """
    Initialize the database
    """

    DB_NAME = 'movies.db'

    # Only initialize if database doesn't exist
    if os.path.exists(DB_NAME) and not override:
        return
    
    # Create new database
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create Users table
    cursor.execute('''
    CREATE TABLE Users (
        idUsers INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')
    
    # Create Movies table
    cursor.execute('''
    CREATE TABLE Movies (
        idMovies INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        imdb_id TEXT UNIQUE NOT NULL
    )
    ''')
    
    # Create Ratings table
    cursor.execute('''
    CREATE TABLE Ratings (
        idRatings INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        movie_id INTEGER NOT NULL,
        score INTEGER NOT NULL,
        review TEXT,
        time DATETIME NOT NULL,
        FOREIGN KEY (user_id) REFERENCES Users (idUsers),
        FOREIGN KEY (movie_id) REFERENCES Movies (idMovies)
    )
    ''')
    
    # Create Friends table
    cursor.execute('''
    CREATE TABLE Friends (
        idFriendship INTEGER PRIMARY KEY AUTOINCREMENT,
        idUsers INTEGER NOT NULL,
        idFriend INTEGER NOT NULL,
        FOREIGN KEY (idUsers) REFERENCES Users (idUsers),
        FOREIGN KEY (idFriend) REFERENCES Users (idUsers)
    )
    ''')
    
    # Create Watchlist table
    cursor.execute('''
    CREATE TABLE Watchlist (
        idWatchlist INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        movie_id INTEGER NOT NULL,
        time DATETIME NOT NULL,
        FOREIGN KEY (user_id) REFERENCES Users (idUsers),
        FOREIGN KEY (movie_id) REFERENCES Movies (idMovies)
    )
    ''')
    
    # Create WatchedHistory table
    cursor.execute('''
    CREATE TABLE WatchedHistory (
        idWatchedHistory INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        movie_id INTEGER NOT NULL,
        watched_date DATETIME NOT NULL,
        FOREIGN KEY (user_id) REFERENCES Users (idUsers),
        FOREIGN KEY (movie_id) REFERENCES Movies (idMovies)
    )
    ''')
    
    # Create Discussion table
    cursor.execute('''
    CREATE TABLE Discussion (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        imdb_id TEXT NOT NULL,
        comments TEXT
    )
    ''')

    # Add sample movies
    def extract_values(line):
        line = line.strip().split("VALUES")[1].strip().strip('();\n').split(',')
        movie_id = int(line[0])
        name = line[1].strip().strip("'")
        imdb_id = line[2].strip().strip("'")
        return (movie_id, name, imdb_id)

    with open(os.path.join(os.path.dirname(__file__), 'movies.sql'), 'r') as sql_file:
        sample_movies = []
        seen_imdb_ids = set()
        for line in sql_file:
            if line.strip() and not line.startswith('--') and line.startswith('INSERT'):
                try:
                    movie_data = extract_values(line)
                    if movie_data[2] not in seen_imdb_ids:  # Check for duplicate IMDB IDs
                        sample_movies.append(movie_data)
                        seen_imdb_ids.add(movie_data[2])
                except Exception as e:
                    logging.warning(f"Failed to process line: {line}. Error: {str(e)}")
                    continue
    
    if sample_movies:
        cursor.executemany(
            "INSERT INTO Movies (idMovies, name, imdb_id) VALUES (?, ?, ?)",
            sample_movies
        )

    # Commit changes and close connection
    conn.commit()
    conn.close()

def download_thumbnails():
    print("Downloading thumbnails...")
    PATH = os.path.join(os.path.dirname(__file__), "thumbnails")
    if(os.path.exists(PATH)):
        return
    os.makedirs(PATH, exist_ok=True)

    import requests
    zip_data = requests.get("https://www.kaggle.com/api/v1/datasets/download/rezaunderfit/48k-imdb-movies-with-posters")
    with open("48k-imdb-movies-with-posters.zip", "wb") as f:
        f.write(zip_data.content)

    temppath = tempfile.mkdtemp()
    with zipfile.ZipFile("48k-imdb-movies-with-posters.zip", "r") as zip_ref:
        zip_ref.extractall(temppath)

    for root, dirs, files in os.walk(temppath):
        for file in files:
            if file.endswith('.jpg'):
                src_path = os.path.join(root, file)
                dst_path = os.path.join(PATH, file)
                print(f"Moving {src_path} to {dst_path}")
                shutil.move(src_path, dst_path)
    
    print("Thumbnails downloaded")
    

def create_colored_tags(genres):
    """
    Utitilty function to create colored tags for different
    movie genres
    """
    # Define colors for specific genres
    genre_colors = {
        "Musical": "#FF1493",  # DeepPink
        "Sci-Fi": "#00CED1",  # DarkTurquoise
        "Mystery": "#8A2BE2",  # BlueViolet
        "Thriller": "#FF6347",  # Tomato
        "Horror": "#FF4500",  # OrangeRed
        "Documentary": "#228B22",  # ForestGreen
        "Fantasy": "#FFA500",  # Orange
        "Adventure": "#FFD700",  # Gold
        "Children": "#32CD32",  # LimeGreen
        "Film-Noir": "#2F4F4F",  # DarkSlateGray
        "Comedy": "#FFB500",  # VividYellow
        "Crime": "#8B0000",  # DarkRed
        "Drama": "#8B008B",  # DarkMagenta
        "Western": "#FF8C00",  # DarkOrange
        "IMAX": "#20B2AA",  # LightSeaGreen
        "Action": "#FF0000",  # Red
        "War": "#B22222",  # FireBrick
        "(no genres listed)": "#A9A9A9",  # DarkGray
        "Romance": "#FF69B4",  # HotPink
        "Animation": "#4B0082",  # Indigo
    }
    tags = []
    for genre in genres:
        color = genre_colors.get(genre, "#CCCCCC")  # Default color if not found
        tag = f'<span style="background-color: {color}; color: #FFFFFF; \
            padding: 5px; border-radius: 5px;">{genre}</span>'
        tags.append(tag)
    return " ".join(tags)


def beautify_feedback_data(data):
    """
    Utility function to beautify the feedback json containing predicted movies for sending in email
    """
    # Create empty lists for each category
    yet_to_watch = []
    like = []
    dislike = []

    # Iterate through the data and categorize movies
    for movie, status in data.items():
        if status == "Yet to watch":
            yet_to_watch.append(movie)
        elif status == "Like":
            like.append(movie)
        elif status == "Dislike":
            dislike.append(movie)

    # Create a category-dictionary of liked, disliked and yet to watch movies
    categorized_data_dict = {
        "Liked": like,
        "Disliked": dislike,
        "Yet to Watch": yet_to_watch,
    }

    return categorized_data_dict


def create_movie_genres(movie_genre_df):
    """
    Utility function for creating a dictionary for movie-genres mapping
    """
    # Create a dictionary to map movies to their genres
    movie_to_genres = {}

    # Iterating on all movies to create the map
    for row in movie_genre_df.iterrows():
        movie = row[1]["title"]
        genres = row[1]["genres"].split("|")
        movie_to_genres[movie] = genres
    return movie_to_genres


def send_email_to_user(recipient_email, categorized_data):
    """
    Utility function to send movie recommendations to user over email
    """

    email_html_content = """
                        <html>
                        <head></head>
                        <body>
                            <h1 style="color: #333333;">Movie Recommendations from BingeSuggest</h1>
                            <p style="color: #555555;">Dear Movie Enthusiast,</p>
                            <p style="color: #555555;">We hope you're having a fantastic day!</p>
                            <div style="padding: 10px; border: 1px solid #cccccc; border-radius: 5px; background-color: #f9f9f9;">
                            <h2>Your Movie Recommendations:</h2>
                            <h3>Movies Liked:</h3>
                            <ul style="color: #555555;">
                                {}
                            </ul>
                            <h3>Movies Disliked:</h3>
                            <ul style="color: #555555;">
                                {}
                            </ul>
                            <h3>Movies Yet to Watch:</h3>
                            <ul style="color: #555555;">
                                {}
                            </ul>
                            </div>
                            <p style="color: #555555;">Enjoy your movie time with BingeSuggest!</p>
                            <p style="color: #555555;">Best regards,<br>BingeSuggest Team 🍿</p>
                        </body>
                        </html>
                        """

    # Email configuration
    smtp_server = "smtp.gmail.com"
    # Port for TLS
    smtp_port = 587
    sender_email = os.getenv("SENDER_EMAIL")

    # Use an app password since 2-factor authentication is enabled
    sender_password = os.getenv("SENDER_EMAIL_PASSWORD")
    subject = "Your movie recommendation from BingeSuggest"

    # Create the email message
    message = MIMEMultipart("alternative")
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = subject
    # Load the CSV file into a DataFrame
    movie_genre_df = pd.read_csv("../../data/movies.csv")
    # Creating movie-genres map
    movie_to_genres = create_movie_genres(movie_genre_df)
    # Create the email message with HTML content
    html_content = email_html_content.format(
        "\n".join(
            f"<li>{movie} \
            {create_colored_tags(movie_to_genres.get(movie, ['Unknown Genre']))}</li><br>"
            for movie in categorized_data["Liked"]
        ),
        "\n".join(
            f"<li>{movie} \
            {create_colored_tags(movie_to_genres.get(movie, ['Unknown Genre']))}</li><br>"
            for movie in categorized_data["Disliked"]
        ),
        "\n".join(
            f"<li>{movie} \
            {create_colored_tags(movie_to_genres.get(movie, ['Unknown Genre']))}</li><br>"
            for movie in categorized_data["Yet to Watch"]
        ),
    )

    # Attach the HTML email body
    message.attach(MIMEText(html_content, "html"))

    # Connect to the SMTP server
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        # Start TLS encryption
        server.starttls()
        server.login(sender_email, sender_password)

        # Send the email
        server.sendmail(sender_email, recipient_email, message.as_string())
        logging.info("Email sent successfully!")

    except SMTPException as e:
        # Handle SMTP-related exceptions
        logging.error("SMTP error while sending email: %s", str(e))

    finally:
        server.quit()


def create_account(db, email, username, password):
    """
    Utility function for creating an account
    """
    cursor = db.cursor()
    new_pass = password.encode("utf-8")
    h = new_pass
    cursor.execute(
        "INSERT INTO Users(username, email, password) VALUES (?, ?, ?);",
        (username, email, h),
    )
    db.commit()


def add_friend(db, username, user_id):
    """
    Utility function for adding a friend
    """
    cursor = db.cursor()
    cursor.execute("SELECT idUsers FROM Users WHERE username = ?;", [username])
    friend_id = cursor.fetchone()[0]
    cursor.execute(
        "INSERT INTO Friends(idUsers, idFriend) VALUES (?, ?);",
        (int(user_id), int(friend_id)),
    )
    cursor.execute(
        "INSERT INTO Friends(idUsers, idFriend) VALUES (?, ?);",
        (int(friend_id), int(user_id)),
    )
    db.commit()


def login_to_account(db, username, password):
    """
    Utility function for logging in to an account
    """
    executor = db.cursor()
    executor.execute(
        "SELECT IdUsers, username, password FROM Users WHERE username = ?;",
        [username],
    )
    result = executor.fetchall()
    encoded_pass = password.encode("utf-8")
    actual_pass = (result[0][2])
    if len(result) == 0 or encoded_pass != actual_pass:
        return None
    return result[0][0]


def submit_review(db, user, movie, score, review):
    """
    Utility function for creating a dictionary for submitting a review
    """
    cursor = db.cursor()
    cursor.execute("SELECT idMovies FROM Movies WHERE name = ?", [movie])
    movie_id = cursor.fetchone()[0]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO Ratings(user_id, movie_id, score, review, time) \
        VALUES (?, ?, ?, ?, ?);",
        (int(user), int(movie_id), int(score), str(review), timestamp),
    )
    db.commit()


def get_wall_posts(db):
    """
    Utility function for creating getting wall posts from the db
    """
    cursor = db.cursor()
    cursor.execute(
        "SELECT name, imdb_id, review, score, username, time FROM Users JOIN \
        (SELECT name, imdb_id, review, score, user_id, time FROM Ratings\
        JOIN Movies on Ratings.movie_id = Movies.idMovies) AS moviereview \
        ON Users.idUsers = moviereview.user_id ORDER BY time limit 50"
    )
    rows = [x[0] for x in cursor.description]
    result = cursor.fetchall()
    json_data = []
    for r in result:
        json_data.append(dict(zip(rows, r)))
    return jsonify(json_data)


def get_recent_movies(db, user):
    """
    Utility function for getting recent movies reviewed by a user
    """
    executor = db.cursor()
    executor.execute(
        "SELECT name, score FROM Ratings AS r JOIN \
    Movies AS m ON m.idMovies = r.movie_id \
    WHERE user_id = ? \
    ORDER BY time DESC \
    LIMIT 5;",
        [int(user)],
    )
    rows = [x[0] for x in executor.description]
    result = executor.fetchall()
    json_data = []
    for r in result:
        json_data.append(dict(zip(rows, r)))
    return jsonify(json_data)


def get_username(db, user):
    """
    Utility function for getting the current users username
    """
    executor = db.cursor()
    executor.execute("SELECT username FROM Users WHERE idUsers = ?;", [int(user)])
    result = executor.fetchall()
    return jsonify(result[0][0])


def get_username_data(db, user):
    """
    Utility function for getting the current users username
    """
    executor = db.cursor()
    executor.execute("SELECT username FROM Users WHERE idUsers = ?;", [int(user)])
    result = executor.fetchall()
    return result[0][0]


def get_recent_friend_movies(db, user):
    """
    Utility function for getting a certain friends recent movies
    """
    executor = db.cursor()
    executor.execute("SELECT idUsers FROM Users WHERE username = ?;", [str(user)])
    result = executor.fetchall()
    user_id = result[0][0]
    executor.execute(
        "SELECT name, score FROM Ratings AS r JOIN \
    Movies AS m ON m.idMovies = r.movie_id \
    WHERE user_id = ? \
    ORDER BY time DESC \
    LIMIT 5;",
        [int(user_id)],
    )
    rows = [x[0] for x in executor.description]
    result = executor.fetchall()
    json_data = []
    for r in result:
        json_data.append(dict(zip(rows, r)))
    return jsonify(json_data)


def get_friends(db, user):
    """
    Utility function for getting the current users friends
    """
    executor = db.cursor()
    executor.execute(
        "SELECT username FROM Users AS u \
                     JOIN Friends AS f ON u.idUsers = f.idFriend WHERE f.idUsers = ?;",
        [int(user)],
    )
    result = executor.fetchall()
    return jsonify(result)


def add_to_watchlist(db, user_id, movie_id, timestamp=None):
    """
    Utility function to add a movie to the user's watchlist.
    Only inserts the movie if it is not already in the user's watchlist.
    """
    cursor = db.cursor()

    # Check if the movie is already in the user's watchlist
    cursor.execute(
        "SELECT 1 FROM Watchlist WHERE user_id = ? AND movie_id = ?",
        (int(user_id), int(movie_id)),
    )
    existing_entry = cursor.fetchone()

    # If the movie is not already in the watchlist, add it
    if not existing_entry:
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO Watchlist (user_id, movie_id, time) VALUES (?, ?, ?);",
            (int(user_id), int(movie_id), timestamp),
        )
        db.commit()
        return True  # Indicate that the movie was added
    else:
        return False  # Indicate that the movie was already in the watchlist


def get_imdb_id_by_name(db, movie_name):
    """
    Fetches the imdb_id for a movie based on its name.
    """
    cursor = db.cursor()
    cursor.execute("SELECT imdb_id FROM Movies WHERE name LIKE ? || '%' LIMIT 1", (movie_name,))
    result = cursor.fetchone()
    return result[0] if result else None


def add_to_watched_history(db, user_id, imdb_id, watched_date=None):
    """
    Utility function to add a movie to the user's watched history.
    """
    cursor = db.cursor()

    # Check if the movie exists in the database
    cursor.execute("SELECT idMovies FROM Movies WHERE imdb_id = ?", [imdb_id])
    movie_result = cursor.fetchone()
    if not movie_result:
        return False, "Movie not found"

    movie_id = movie_result[0]

    # Check if the movie is already in the user's watched history
    cursor.execute(
        "SELECT 1 FROM WatchedHistory WHERE user_id = ? AND movie_id = ?",
        [user_id, movie_id],
    )
    if cursor.fetchone():
        return False, "Movie already in watched history"

    # Insert the movie into the user's watched history
    watched_date = watched_date or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO WatchedHistory (user_id, movie_id, watched_date) VALUES (?, ?, ?)",
        [user_id, movie_id, watched_date],
    )
    db.commit()
    return True, "Movie added to watched history"


def remove_from_watched_history_util(db, user_id, imdb_id):
    """
    Utility function to remove a movie from the user's watched history.
    """
    cursor = db.cursor()

    # Check if the movie exists in the database
    cursor.execute("SELECT idMovies FROM Movies WHERE imdb_id = ?", [imdb_id])
    movie_result = cursor.fetchone()
    if not movie_result:
        return False, "Movie not found"

    movie_id = movie_result[0]

    # Check if the movie exists in the user's watched history
    cursor.execute(
        "SELECT 1 FROM WatchedHistory WHERE user_id = ? AND movie_id = ?",
        [user_id, movie_id],
    )
    if not cursor.fetchone():
        return False, "Movie not in watched history"

    # Delete the movie from watched history
    cursor.execute(
        "DELETE FROM WatchedHistory WHERE user_id = ? AND movie_id = ?",
        [user_id, movie_id],
    )
    db.commit()
    return True, "Movie removed from watched history"


def remove_from_watchlist(db, user_id, imdb_id):
    """
    Utility function to remove a movie from the user's watchlist.
    """
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT DISTINCT idMovies FROM Movies 
        WHERE imdb_id = ?;
        """,
        [imdb_id],
    )

    watchlist = cursor.fetchone()
    idMovies = None
    if watchlist is not None:
        idMovies = watchlist["idMovies"]

    if idMovies is None:
        return None, "Movie not in watchlist"

    # Delete the movie from watched history
    cursor.execute(
        """
        DELETE FROM Watchlist WHERE movie_id = ? AND user_id = ?;
        """,
        [idMovies, user_id],
    )
    db.commit()
    return idMovies, "Movie removed from watchlist"


def create_or_update_discussion(db, data):
    """
    create or update comments on a discussion in DB
    """
    cursor = db.cursor()
    cursor.execute(
        "SELECT * from Discussion where imdb_id = ? LIMIT 1", (data["imdb_id"],)
    )
    result = cursor.fetchone()
    if result is None:
        comments = [{"user": data["user"], "comment": data["comment"]}]
        cursor.execute(
            "Insert INTO Discussion (imdb_id, comments) values(?,?)",
            (data["imdb_id"], json.dumps(comments)),
        )
        db.commit()
    else:
        comments = json.loads(result[2])
        comments.append({"user": data["user"], "comment": data["comment"]})
        cursor.execute(
            "Update Discussion set comments = ? where imdb_id = ?",
            (json.dumps(comments), data["imdb_id"]),
        )
        db.commit()
    return (
        jsonify(
            [
                {"user": data["user"], "comment": data["comment"]},
            ]
        ),
        200,
    )


def get_discussion(db, imdb_id):
    """
    Get the discussion on the movie with imdb_id
    """
    cursor = db.cursor()
    cursor.execute("SELECT comments from Discussion where imdb_id = ?", (imdb_id,))
    result = cursor.fetchone()
    return (jsonify(json.loads(result[0])), 200)
