import streamlit as st
import pandas as pd

# Load movie data
movies_df = pd.read_csv("../data/processed/processed_movies.csv")

# Handling missing poster data
if "posters" in movies_df.columns:
    posters = movies_df['posters'].tolist()
else:
    posters = ["https://via.placeholder.com/150"] * len(movies_df)  

def initialize_session_state():
    """Ensure all necessary session state variables are initialized."""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "username" not in st.session_state:
        st.session_state["username"] = None
    if "selected_movie" not in st.session_state:
        st.session_state["selected_movie"] = None
    if "filtered_movies" not in st.session_state:
        st.session_state["filtered_movies"] = None

def logout():
    """Logout function to reset session state."""
    st.session_state["authenticated"] = False
    st.session_state["username"] = None
    st.session_state["selected_movie"] = None
    st.rerun()

def get_recommendations(selected_movie):
    """Get movie recommendations based on genre similarity and rating."""
    movie = movies_df[movies_df['title'] == selected_movie]
    
    if movie.empty:
        return None
    
    movie_genre = movie['genres'].values[0]
    
    # Find movies with the same genre, exclude the selected movie, and remove duplicates
    similar_movies = movies_df[(movies_df['genres'] == movie_genre) & (movies_df['title'] != selected_movie)]
    
    # Remove duplicates based on title
    similar_movies = similar_movies.drop_duplicates(subset=['title'])

    # Sort by rating (if available) and limit to 5 recommendations
    if 'rating' in movies_df.columns:
        similar_movies = similar_movies.sort_values(by="rating", ascending=False)
    
    return similar_movies.head(5)

def movie_details(movie_title):
    """Display details of a selected movie and show recommendations."""
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

    # Show movie recommendations
    recommendations = get_recommendations(movie_title)
    
    if recommendations is not None and not recommendations.empty:
        st.subheader("You may also like:")
        cols = st.columns(len(recommendations))
        for idx, (_, rec_movie) in enumerate(recommendations.iterrows()):
            with cols[idx]:  
                if st.button(f"View {rec_movie['title']}", key=f"rec_{rec_movie['title']}", use_container_width=True):
                    st.session_state["selected_movie"] = rec_movie['title']
                    st.rerun()
                st.image(rec_movie['posters'], width=120)
                st.write(f"**{rec_movie['title']}**")  

def movie_search_page():
    """Movie search and recommendation interface."""
    if not st.session_state.get("authenticated", False):
        return

    st.button("Logout", type="primary", key="logout_button", on_click=logout)

    st.title("Movie Search and Recommendations")
    st.subheader(f"Welcome, {st.session_state['username']}!")

    query = st.text_input("Enter movie name:")
    
    if st.button("Search", key="search_button") or query:
        filtered_movies = movies_df[movies_df['title'].str.contains(query, case=False, na=False)].drop_duplicates(subset=['title'])
        st.session_state["filtered_movies"] = filtered_movies.head(9)

    if st.session_state["filtered_movies"] is not None and not st.session_state["filtered_movies"].empty:
        cols = st.columns(3)
        for idx, (_, movie) in enumerate(st.session_state["filtered_movies"].iterrows()):
            with cols[idx % 3]:  
                if st.button(f"View {movie['title']}", key=f"movie_{movie['title']}", use_container_width=True):
                    st.session_state["selected_movie"] = movie['title']
                    st.rerun()
                st.image(movie['posters'], width=150) 
                st.write(f"**{movie['title']}**")  
        
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

if __name__ == "__main__":
    initialize_session_state()
    if st.session_state["authenticated"]:
        movie_search_page()
