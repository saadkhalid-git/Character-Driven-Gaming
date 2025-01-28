import streamlit as st
import requests
import pandas as pd

# Define the FastAPI backend URL
BACKEND_URL = "http://127.0.0.1:8000"

# Manage session state for login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Load movies from CSV
movies_df = pd.read_csv("/Users/wasedoo/Documents/EPITA/Semester 3/Action Learning/cross-domain-recommender-movies-and-games/data/db-data/movies.csv")
movies = movies_df['title'].tolist()

games_df = pd.read_csv("/Users/wasedoo/Documents/EPITA/Semester 3/Action Learning/cross-domain-recommender-movies-and-games/data/db-data/games.csv")
games = games_df['title'].tolist()

# Function for the movies page
def movies_page():
    st.title("Movies Page")
    with st.sidebar:
        st.write(f"Welcome to the Movies Page, {st.session_state.username}!")
        if st.button("Recommend Me!"):
            st.session_state.show_recommendation = True

        if st.session_state.get("show_recommendation", False):
            selected_movies = st.multiselect("Choose Movies", movies, key="selected_movies")
            selected_games = st.multiselect("Choose Games", games, key="selected_games")
            if st.button("Submit"):
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
                st.session_state.show_recommendation = False

        st.button("Logout", on_click=logout)

# Logout function
def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""

# Login page
def login_page():
    st.title("Login Page")
    menu = ["Login", "Sign Up"]
    choice = st.radio("Select an option", menu)

    if choice == "Login":
        st.subheader("Login to Your Account")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username and password:
                response = requests.post(f"{BACKEND_URL}/login", json={"username": username, "password": password})
                if response.status_code == 200:
                    st.success(response.json()["message"])
                    # Set session state
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error(response.json()["detail"])
            else:
                st.warning("Please enter both username and password.")

    elif choice == "Sign Up":
        st.subheader("Create a New Account")
        new_username = st.text_input("Choose a Username")
        new_password = st.text_input("Choose a Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        if st.button("Sign Up"):
            if new_username and new_password and confirm_password:
                response = requests.post(f"{BACKEND_URL}/signup", 
                                         json={"username": new_username, 
                                               "password": new_password, 
                                               "confirm_password": confirm_password})
                if response.status_code == 200:
                    st.success(response.json()["message"])
                else:
                    st.error(response.json()["detail"])
            else:
                st.warning("Please fill in all fields.")

# Main execution
if __name__ == "__main__":
    if st.session_state.logged_in:
        movies_page()  # Redirect to the movies page
    else:
        login_page()  # Show the login page
