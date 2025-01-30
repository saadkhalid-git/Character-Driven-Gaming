import streamlit as st
import requests
import pandas as pd
import ast  # To safely evaluate the string representation of a list
 
# Load Movies and Games Data
movies_df = pd.read_csv("../data/processed/processed_movies.csv")
games_df = pd.read_csv("../data/db-data/games.csv")
movies = movies_df['title'].tolist()
games = games_df['title'].tolist()
 
# FastAPI backend URL 
BACKEND_URL = "http://127.0.0.1:8000"  

def logout():
    """Logout function to reset session state."""
    st.session_state["authenticated"] = False
    st.session_state["username"] = None
    st.session_state["show_recommendation"] = False
    st.rerun()  # Force Streamlit to rerun and show login page

# Function to display the recommendation page
def recommendation_page():
    """Movie and Game recommendation page with filters and interactive UI."""
    
    if "username" not in st.session_state:
        st.session_state["username"] = "TestUser"  # Mock username for testing
 
        # Create a container at the top right for the logout button
    top_placeholder = st.empty()
    with top_placeholder.container():
        # Assign a unique key to the Logout button
        st.button("Logout", type="primary", key="unique_logout_button", on_click=logout)

    # Page Title and User Greeting
    st.title("Your Personalized Recommendations")
    st.subheader(f"Welcome back, {st.session_state['username']}!")
    
    # Movie & Game Filters
    genre_filter = st.selectbox("Select Movie Genre", ["All", "Action", "Comedy", "Drama", "Thriller"], key="genre")
    tag_filter = st.selectbox("Select Game Tag", ["All", "Action", "Adventure", "RPG", "Puzzle", "Horror"], key="tag")
 
    # Search Bar for Movies or Games
    search_query = st.text_input("Search for a movie or game...")
 
    # Movie Search and Recommendations
    st.header("Recommended Movies")
    
    # Filtering movies by genre
    if genre_filter != "All":
        filtered_movies = movies_df[movies_df['genres'].str.contains(genre_filter, case=False, na=False)]
    else:
        filtered_movies = movies_df[movies_df['title'].str.contains(search_query, case=False)]
 
    movie_display = st.selectbox("Choose a Movie", filtered_movies['title'].tolist())
    st.write(f"Selected Movie: {movie_display}")
 
    # Game Search and Recommendations
    st.header("Recommended Games")
    
    # Filter games by the selected tag
    if tag_filter != "All":
        filtered_games = games_df[games_df['tags'].apply(lambda x: tag_filter.lower() in ast.literal_eval(x.lower()))]
    else:
        filtered_games = games_df[games_df['title'].str.contains(search_query, case=False)]
    
    game_display = st.selectbox("Choose a Game", filtered_games['title'].tolist())
    st.write(f"Selected Game: {game_display}")
 
    # Recommendations based on user selection
    if st.button("Get Recommendations"):
        # Simulating backend interaction
        selected_movie_ids = movies_df[movies_df['title'] == movie_display]['movieId'].tolist()
        selected_game_ids = games_df[games_df['title'] == game_display]['app_id'].tolist()
 
        # Prepare data for backend API
        data = {
            "username": st.session_state.username,
            "selected_movie_ids": selected_movie_ids,
            "selected_game_ids": selected_game_ids
        }
 
        # Make API request for recommendations
        response = requests.post(f"{BACKEND_URL}/recommend", json=data)
        
        if response.status_code == 200:
            st.success("Recommendations sent successfully!")
            recommendations = response.json()
            # Display the received recommendations (Placeholder here)
            st.write(recommendations)
        else:
            st.error("Failed to get recommendations. Please try again later.")
 
# Display the page
if __name__ == "__main__":
    recommendation_page()
 