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
    if "selected_movie" not in st.session_state:
        st.session_state["selected_movie"] = None


def logout():
    """Logout function to reset session state."""
    st.session_state["authenticated"] = False
    st.session_state["username"] = None
    st.session_state["show_recommendation"] = False
    st.rerun()


def movie_details(movie_title):
    """Display detailed information about a selected movie."""
    movie = movies_df[movies_df['title'] == movie_title].iloc[0]
    
    st.title(movie['title'])
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image(movie['posters'], width=200)
    
    with col2:
        if 'year' in movie:
            st.write(f"**Year:** {movie['year']}")
        if 'genres' in movie:
            st.write(f"**Genre:** {movie['genres']}")
        if 'rating' in movie:
            st.write(f"**Rating:** {movie['rating']}")


def movie_search_page():
    """Movie search and recommendation interface."""
    # Redirect immediately if user is not authenticated
    if not st.session_state.get("authenticated", False):
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
    # Store the search query in session state
    if "search_query" not in st.session_state:
        st.session_state.search_query = query
    
    # Only update filtered movies when search button is clicked or query changes
    if st.button("Search", key="search_button") or st.session_state.search_query != query:
        st.session_state.search_query = query
        # Filter movies by search query and remove duplicates based on title only
        filtered_movies = movies_df[movies_df['title'].str.contains(query, case=False, na=False)].drop_duplicates(subset=['title'])
        st.session_state.filtered_movies = filtered_movies.head(9)  # Limit to 9 movies for 3x3 grid

    if 'filtered_movies' in st.session_state and len(st.session_state.filtered_movies) > 0:
        # Display the filtered movies with posters in a 3-column layout
        cols = st.columns(3)
        for idx, (_, movie) in enumerate(st.session_state.filtered_movies.iterrows()):
            with cols[idx % 3]:  
                if st.button("View Details", key=f"movie_{idx}", use_container_width=True):
                    st.session_state["selected_movie"] = movie['title']
                st.image(movie['posters'], width=150) 
                st.write(f"**{movie['title']}**")  
        
        # Show movie details in a separate section outside the loop
        if st.session_state["selected_movie"]:
            st.divider()
            col1, col2 = st.columns([6, 1])
            with col1:
                movie_details(st.session_state["selected_movie"])
            with col2:
                if st.button("Clear", key="clear_details"):
                    st.session_state["selected_movie"] = None
                    st.rerun()
    else:
        st.write("No movies found!")

    # Show recommendation button

    if st.button("Get Recommendation", key="recommendation_button"):
        st.session_state["show_recommendation"] = True
        st.rerun()

    if st.session_state["show_recommendation"]:
        if st.session_state["selected_movie"] is None:
            st.error("Please select a movie first")
        else:
            try:
                response = requests.post(
                    f"{BACKEND_URL}/recommend/movie",
                    json={"movie_title": st.session_state["selected_movie"]}
                )
                if response.status_code == 200:
                    recommendations = response.json()
                    st.write("Recommendations:")
                    for rec in recommendations:
                        st.write(f"- {rec}")
                else:
                    st.error("Failed to get recommendations")
            except Exception as e:
                st.error(f"Error getting recommendations: {str(e)}")


# Main entry point
if __name__ == "__main__":
    # Ensure session state variables are initialized
    initialize_session_state()
    st.session_state["selected_movie"] = None

    # Route to the appropriate page based on authentication status
    if st.session_state["authenticated"]:
        movie_search_page()