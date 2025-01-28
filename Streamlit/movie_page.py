import streamlit as st
import pandas as pd
import requests

# Mock data for movies and games
movies_df = pd.read_csv("../data/db-data/movies.csv")
movies = movies_df['title'].tolist()

games_df = pd.read_csv("../data/db-data/games.csv")
games = games_df['title'].tolist()

# FastAPI backend URL
BACKEND_URL = "http://127.0.0.1:8000"  # Replace with your actual FastAPI URL


def initialize_session_state():
    """Ensure all necessary session state variables are initialized."""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "username" not in st.session_state:
        st.session_state["username"] = None
    if "show_recommendation" not in st.session_state:
        st.session_state["show_recommendation"] = False


def logout():
    """Logout function to reset session state."""
    st.session_state["authenticated"] = False
    st.session_state["username"] = None
    st.session_state["show_recommendation"] = False
    st.rerun()  # Force Streamlit to rerun and show login page


def login_page():
    """Login page for authentication."""
    st.title("Sign In")
    st.subheader("Please log in to access the movie search page.")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username and password:  # Mock authentication logic
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
        else:
            st.warning("Please enter both username and password.")


def movie_search_page():
    """Movie search and recommendation interface."""
    # Redirect immediately if user is not authenticated
    if not st.session_state.get("authenticated", False):
        login_page()
        return

    # Create a container at the top right for the logout button
    top_placeholder = st.empty()
    with top_placeholder.container():
        st.button("Logout", type="primary", key="logout_button", on_click=logout)

    # Display the main content
    st.title("Movie Search and Recommendations")
    st.subheader(f"Welcome, {st.session_state['username']}!")

    query = st.text_input("Enter movie name:")
    if st.button("Search"):
        st.write("Search functionality coming soon!")

    with st.sidebar:
        st.write(f"Welcome to the Movies Page, {st.session_state['username']}!")
        if st.button("Recommend Me!"):
            st.session_state["show_recommendation"] = True

        if st.session_state.get("show_recommendation", False):
            selected_movies = st.multiselect("Choose Movies", movies, key="selected_movies")
            selected_games = st.multiselect("Choose Games", games, key="selected_games")
            if st.button("Submit"):
                st.write(f"You selected movies: {', '.join(selected_movies)} and games: {', '.join(selected_games)}")
                selected_movie_ids = movies_df[movies_df['title'].isin(selected_movies)]['movieId'].tolist()
                selected_game_ids = games_df[games_df['title'].isin(selected_games)]['app_id'].tolist()
                data = {
                    "username": st.session_state["username"],
                    "selected_movie_ids": selected_movie_ids,
                    "selected_game_ids": selected_game_ids
                }
                response = requests.post(f"{BACKEND_URL}/recommend", json=data)
                if response.status_code == 200:
                    st.success("Recommendations sent successfully!")
                else:
                    st.error("Failed to send recommendations.")


# Main entry point
if __name__ == "__main__":
    # Ensure session state variables are initialized
    initialize_session_state()

    # Route to the appropriate page based on authentication status
    if st.session_state["authenticated"]:
        movie_search_page()
    else:
        login_page()
