import streamlit as st
import pandas as pd
import ast  # To safely evaluate the string representation of a list
import json
import matplotlib.pyplot as plt

# Load Movies and Games Data (using static CSV files)
movies_df = pd.read_csv("../data/processed/processed_movies.csv")
games_df = pd.read_csv("../data/db-data/games.csv")

USER_DATA_FILE = "user_data.json"

# Load user data
def load_user_data():
    """Load user watch history and preferences from JSON file."""
    try:
        with open(USER_DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"watched_movies": [], "played_games": [], "watchlist": []}

# Save user data
def save_user_data(data):
    """Save user watch history and preferences to JSON file."""
    with open(USER_DATA_FILE, "w") as f:
        json.dump(data, f)

# Initialize session state
user_data = load_user_data()
for key in ["watched_movies", "played_games", "watchlist"]:
    if key not in st.session_state:
        st.session_state[key] = user_data.get(key, [])

def logout():
    """Logout function to reset session state."""
    st.session_state["authenticated"] = False
    st.session_state["username"] = None
    st.session_state["show_recommendation"] = False
    st.rerun()  # Force Streamlit to rerun and show login page

# Function to plot genre distribution
def plot_genre_distribution(watched_movies):
    """Generate a pie chart of the most-watched genres."""
    genre_counts = {}

    for movie in watched_movies:
        genres = movies_df[movies_df["title"] == movie]["genres"].values
        if len(genres) > 0:
            for genre in genres[0].split(", "):
                genre_counts[genre] = genre_counts.get(genre, 0) + 1

    if genre_counts:
        fig, ax = plt.subplots()
        ax.pie(genre_counts.values(), labels=genre_counts.keys(), autopct="%1.1f%%", startangle=90)
        ax.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle.
        st.pyplot(fig)
    else:
        st.write("No genre data available yet.")

# Function to display the recommendation page
def recommendation_page():
    """Movie and Game recommendation page with filters and interactive UI."""

    if "username" not in st.session_state:
        st.session_state["username"] = "TestUser"  # Mock username for testing

    # Create a container at the top right for the logout button
    top_placeholder = st.empty()
    with top_placeholder.container():
        st.button("Logout", type="primary", key="unique_logout_button", on_click=logout)

    # Page Title and User Greeting
    st.title("Your Personalized Recommendations")
    st.subheader(f"Welcome back, {st.session_state['username']}!")

    # Movie & Game Filters
    genre_filter = st.selectbox("Select Movie Genre", ["All"] + sorted(movies_df['genres'].dropna().unique().tolist()), key="genre")
    tag_filter = st.selectbox("Select Game Tag", ["All"] + sorted(games_df['tags'].dropna().unique().tolist()), key="tag")

    # Search Bar for Movies or Games
    search_query = st.text_input("Search for a movie or game...")

    # Movie Search and Recommendations
    st.header("Recommended Movies")
    
    # Filtering movies by genre
    if genre_filter != "All":
        filtered_movies = movies_df[movies_df['genres'].str.contains(genre_filter, case=False, na=False)]
    else:
        filtered_movies = movies_df[movies_df['title'].str.contains(search_query, case=False, na=False)]

    cols = st.columns(3)  # Create 3 columns for displaying movie posters
    for idx, (_, movie) in enumerate(filtered_movies.head(5).iterrows()):
        with cols[idx % 3]:  # Arrange posters in columns
            st.image(movie['posters'], width=160, use_container_width=True, caption=movie['title'])

    # Game Search and Recommendations
    st.header("Recommended Games")

    # Filter and limit games to top 5
    if tag_filter != "All":
        filtered_games = games_df[games_df['tags'].apply(lambda x: tag_filter.lower() in ast.literal_eval(x.lower()))]
    else:
        filtered_games = games_df[games_df['title'].str.contains(search_query, case=False, na=False)]

    filtered_games = filtered_games.head(5)  # Show only 5 games

    # Display in columns (like movies)
    cols = st.columns(3)
    for idx, (_, game) in enumerate(filtered_games.iterrows()):
        with cols[idx % 3]:  # Arrange games in columns
            st.image("/Users/vinaykumar/Assignments/Action_lerning/newCDR/cross-domain-recommender-movies-and-games/Streamlit/joystick.jpg", 
                    width=160, use_container_width=True, caption=game['title'])



    # Display Watch History
    st.subheader("Your Watch History")
    st.write(", ".join(st.session_state["watched_movies"]) if st.session_state["watched_movies"] else "No movies watched yet.")

    st.subheader("Your Played Games")
    st.write(", ".join(st.session_state["played_games"]) if st.session_state["played_games"] else "No games played yet.")

    # Add movie to watch history
    selected_movie = st.selectbox("Select a movie you've watched:", movies_df["title"].unique())
    if st.button("Add to Watch History"):
        if selected_movie not in st.session_state["watched_movies"]:
            st.session_state["watched_movies"].append(selected_movie)
            user_data["watched_movies"] = st.session_state["watched_movies"]
            save_user_data(user_data)
            st.success(f"Added {selected_movie} to your watch history!")

    # Add game to played games
    selected_game = st.selectbox("Select a game you've played:", games_df["title"].unique())
    if st.button("Add to Played Games"):
        if selected_game not in st.session_state["played_games"]:
            st.session_state["played_games"].append(selected_game)
            user_data["played_games"] = st.session_state["played_games"]
            save_user_data(user_data)
            st.success(f"Added {selected_game} to played games!")

    # Show Genre Insights
    st.subheader("Your Favorite Movie Genres")
    plot_genre_distribution(st.session_state["watched_movies"])

    # Watchlist Feature
    selected_watchlist_movie = st.selectbox("Add a movie to your watchlist:", movies_df["title"].unique())
    if st.button("Add to Watchlist"):
        if selected_watchlist_movie not in st.session_state["watchlist"]:
            st.session_state["watchlist"].append(selected_watchlist_movie)
            user_data["watchlist"] = st.session_state["watchlist"]
            save_user_data(user_data)
            st.success(f"Added {selected_watchlist_movie} to your watchlist!")

    st.subheader("Your Watchlist")
    st.write(", ".join(st.session_state["watchlist"]) if st.session_state["watchlist"] else "No movies in watchlist yet.")

# Display the page
if __name__ == "__main__":
    recommendation_page()
