import streamlit as st
import pandas as pd
import requests

# Mock data for movies and games
movies_df = pd.read_csv("../data/processed/processed_movies.csv")
games_df = pd.read_csv("../data/db-data/games.csv")
movies = movies_df['title'].tolist()
games = games_df['title'].tolist()

if "posters" in movies_df.columns:
    posters = movies_df['posters'].tolist()
else:
    posters = ["https://via.placeholder.com/150"] * len(movies_df)  

# FastAPI backend URL
BACKEND_URL = "http://127.0.0.1:8000"  

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
        # Assign a unique key to the Logout button
        st.button("Logout", type="primary", key="unique_logout_button", on_click=logout)

    # Display the main content
    st.title("Movie Search and Recommendations")
    st.subheader(f"Welcome, {st.session_state['username']}!")

    query = st.text_input("Enter movie name:")
    if st.button("Search", key="search_button"):
        # Filter movies by search query and remove duplicates
        filtered_movies = movies_df[movies_df['title'].str.contains(query, case=False, na=False)].drop_duplicates(subset=['title', 'posters'])

        # Display the filtered movies with posters in a 3-column layout
        if not filtered_movies.empty:
            cols = st.columns(3)  # Create 3 columns for each row
            for idx, (_, movie) in enumerate(filtered_movies.iterrows()):
                with cols[idx % 3]:  
                    st.image(movie['posters'], width=150) 
                    st.write(f"**{movie['title']}**")  
        else:
            st.write("No movies found!")

# Main entry point
if __name__ == "__main__":
    # Ensure session state variables are initialized
    initialize_session_state()

    # Route to the appropriate page based on authentication status
    if st.session_state["authenticated"]:
        movie_search_page()
    else:
        login_page()
