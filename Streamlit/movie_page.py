import streamlit as st
import requests
import pandas as pd

movies_df = pd.read_csv("/Users/wasedoo/Documents/EPITA/Semester 3/Action Learning/cross-domain-recommender-movies-and-games/data/db-data/movies.csv")
movies = movies_df['title'].tolist()

games_df = pd.read_csv("/Users/wasedoo/Documents/EPITA/Semester 3/Action Learning/cross-domain-recommender-movies-and-games/data/db-data/games.csv")
games = games_df['title'].tolist()

# FastAPI backend URL
BACKEND_URL = "http://127.0.0.1:8000"  # Replace with the actual URL of your FastAPI backend

def movie_search_page():
    """Movie search and recommendation interface."""
    if "username" not in st.session_state:
        st.session_state["username"] = "TestUser"  # Mock username for standalone testing

    st.title("Movie Search and Recommendations")
    st.subheader(f"Welcome, {st.session_state['username']}!")

    query = st.text_input("Enter movie name:")
    if st.button("Search"):
        st.write("Search functionality coming soon!")

    with st.sidebar:
        st.write(f"Welcome to the Movies Page, {st.session_state.username}!")
        if st.button("Recommend Me!"):
            st.session_state.show_recommendation = True

        if st.session_state.get("show_recommendation", False):
            selected_movies = st.multiselect("Choose Movies", movies, key="selected_movies")
            selected_games = st.multiselect("Choose Games", games, key="selected_games")
            if st.button("Submit"):
                st.write(f"You selected movies: {', '.join(selected_movies)} and games: {', '.join(selected_games)}")
                selected_movie_ids = movies_df[movies_df['title'].isin(selected_movies)]['movieId'].tolist()
                selected_game_ids = games_df[games_df['title'].isin(selected_games)]['app_id'].tolist()
                data = {
                    "username": st.session_state.username,
                    "selected_movie_ids": selected_movie_ids,
                    "selected_game_ids": selected_game_ids
                }
                response = requests.post(f"{BACKEND_URL}/recommend", json=data)
                if response.status_code == 200:
                    st.success("Recommendations sent successfully!")
                else:
                    st.error("Failed to send recommendations.")

# # Allow standalone execution
# if __name__ == "__main__":
#     if "authenticated" not in st.session_state:
#         st.session_state["authenticated"] = True  # Mock authentication for standalone testing
#         st.session_state["username"] = "TestUser"

#     movie_search_page()
