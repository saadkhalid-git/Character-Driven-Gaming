import streamlit as st
import requests
import pandas as pd
import time
from streamlit_autorefresh import st_autorefresh
import sys
import os


DEFAULT_GAME_IMAGE = 'game_control.png'
DEFAULT_POSTER_URL = 'player.png'

BACKEND_URL = "http://127.0.0.1:8000"

movies_df = pd.read_csv("../data/db-data/movies.csv")
movies = movies_df['title'].tolist()

games_df = pd.read_csv("../data/db-data/games.csv")
games = games_df['title'].tolist()

processed_movies = pd.read_csv("../data/processed/processed_movies.csv")

movies_with_posters = movies_df.merge(processed_movies, on="title", how="left")

movies_with_posters["posters"] = movies_with_posters["posters"].fillna(DEFAULT_POSTER_URL)
movies_with_posters["posters"] = movies_with_posters["posters"].astype(str)

movies_with_posters["posters"] = movies_with_posters["posters"].astype(str)

GAME_POSTERS_FOLDER = "../streamlit/trending_posters"

# Get top trending movies (most watched/rated)
trending_movies = movies_df.groupby("title")["movieId"].count().sort_values(ascending=False).head(5).index.tolist()

# Get top trending games (most played/rated)
trending_games = games_df.groupby("title")["app_id"].count().sort_values(ascending=False).head(5).index.tolist()


def get_game_poster_paths():
    """Retrieve all game poster image paths from the local folder."""
    # if not os.path.exists(GAME_POSTERS_FOLDER):
    #     return []

    # print(os.listdir(GAME_POSTERS_FOLDER))
    # Get all image files (JPEG, PNG, etc.)
    return [os.path.join(GAME_POSTERS_FOLDER, f) for f in os.listdir(GAME_POSTERS_FOLDER) if f.endswith((".png", ".jpg", ".jpeg"))]


def display_game_slideshow():
    """Displays a continuously running slideshow of trending game posters without blocking UI."""
    game_images = get_game_poster_paths()

    if not game_images:
        st.warning("No trending game posters found.")
        return

    # Auto-refresh only this section every 3 seconds
    refresh_count = st_autorefresh(interval=3000, limit=None, key="game_slideshow")

    # Select an image based on the refresh count
    image_index = refresh_count % len(game_images)
    st.image(game_images[image_index])


def recommendations():
    """Movie search and recommendation interface."""
    if "username" not in st.session_state:
        st.session_state["username"] = "TestUser"  # Mock username for standalone testing

    if "recommended_items" not in st.session_state:
        st.session_state["recommended_items"] = None  # Store recommendations

    st.title("🎬 Movie & Game Recommendations")
    st.subheader(f"Welcome, {st.session_state['username']}!")

    # 🔥 Display Trending Recommendations First
    st.subheader("🔥 Trending Recommendations")

    # 🎮 Display the Slideshow for Trending Game Posters
    # display_game_slideshow()

    # 🎯 Movie & Game Selection
    st.subheader("🎯 Choose Your Favorites")
    
    selected_movies = st.multiselect("Choose Movies", movies_df["title"].tolist(), key="selected_movies")
    selected_games = st.multiselect("Choose Games", games_df["title"].tolist(), key="selected_games")

    movie_ratings = {}
    game_ratings = {}

    # Collect user ratings for selected movies
    if selected_movies:
        st.subheader("Rate Selected Movies")
        for movie in selected_movies:
            movie_ratings[movie] = st.slider(f"Rate {movie}", 0, 5, 3)

    # Collect user ratings for selected games
    if selected_games:
        st.subheader("Rate Selected Games")
        for game in selected_games:
            game_ratings[game] = st.slider(f"Rate {game}", 0, 5, 3)

    if st.button("Recommend me!"):
        st.write(f"You selected movies: {', '.join(selected_movies)} and games: {', '.join(selected_games)}")

        # Convert selections into a DataFrame lookup
        selected_movie_data = movies_df[movies_df["title"].isin(selected_movies)]
        selected_game_data = games_df[games_df["title"].isin(selected_games)]

        # Prepare JSON payload
        movies_data = [
            {"id": row["movieId"], "title": row["title"], "rating": movie_ratings[row["title"]]}
            for _, row in selected_movie_data.iterrows()
        ]

        games_data = [
            {"id": row["app_id"], "title": row["title"], "rating": game_ratings[row["title"]]}
            for _, row in selected_game_data.iterrows()
        ]

        data = {
            "username": st.session_state["username"],
            "movies": movies_data,
            "games": games_data
        }

        response = requests.post(f"{BACKEND_URL}/recommend", json=data)

        if response.status_code == 200:
            st.session_state["recommended_items"] = response.json()  # Store recommendations
        else:
            st.error("Failed to send recommendations.")

    # 🔄 Show Recommendations if Available
    if st.session_state["recommended_items"]:
        display_recommendations(st.session_state["recommended_items"])


def display_recommendations(recommended_items):
    st.success("Here are your recommendations:")
    
    cols = st.columns(3)  # Grid layout
    
    for idx, item in enumerate(recommended_items):
        title = item["title"]
        predicted_rating = item["predicted_rating"]
        item_type = item["type"]  # Check if it's a Movie or a Game

        if item_type == "Movie":
            # Get movie poster from processed_movies
            movie_data = processed_movies.loc[processed_movies["title"] == title]
            poster_url = movie_data["posters"].values
            image_url = poster_url[0] if len(poster_url) > 0 and isinstance(poster_url[0], str) else DEFAULT_POSTER_URL
        else:
            # Use default image for games
            image_url = DEFAULT_GAME_IMAGE

        with cols[idx % 3]:
            st.image(image_url)  # Display image safely
            st.markdown(f"**{title}**")
            st.write(f"⭐ {predicted_rating}")


