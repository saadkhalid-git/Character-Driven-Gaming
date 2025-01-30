from streamlit_autorefresh import st_autorefresh
import streamlit as st
import pandas as pd
import os
import sys
import time


DEFAULT_GAME_IMAGE = '../streamlit/trending_posters/game_control.png'
DEFAULT_POSTER_URL = '../streamlit/trending_posters/1f3ac.png'

# Load movie data
movies_df = pd.read_csv("../data/processed/processed_movies.csv")

# Ensure "title" column is a string
movies_df['title'] = movies_df['title'].astype(str)

# Handling missing poster data
if "posters" in movies_df.columns:
    posters = movies_df['posters'].tolist()
else:
    posters = ["https://via.placeholder.com/150"] * len(movies_df)  

# 🔹 Custom CSS for UI enhancements
st.markdown("""
    <style>
        .movie-card {
            border-radius: 10px;
            padding: 10px;
            text-align: center;
            transition: 0.3s;
        }
        .movie-card:hover {
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
        }
        .movie-poster {
            border-radius: 10px;
            margin-bottom: 10px;
        }
        .movie-title {
            font-size: 16px;
            font-weight: bold;
        }
        .rec-card {
            padding: 8px;
            text-align: center;
        }
        .rec-card:hover {
            background-color: #f5f5f5;
            border-radius: 10px;
        }
        .stButton>button {
            width: 100%;
            border-radius: 10px;
            font-size: 14px;
            padding: 6px;
        }
    </style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Ensure all necessary session state variables are initialized."""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "username" not in st.session_state:
        st.session_state["username"] = None
    if "selected_movie" not in st.session_state:
        st.session_state["selected_movie"] = None
    if "search_query" not in st.session_state:
        st.session_state["search_query"] = ""

initialize_session_state()


def get_recommendations(selected_movie):
    """Get up to 5 movie recommendations based on genre similarity."""
    movie = movies_df[movies_df['title'] == selected_movie]

    if movie.empty:
        return pd.DataFrame()

    movie_genre = movie.iloc[0]['genres']
    similar_movies = movies_df[(movies_df['genres'] == movie_genre) & (movies_df['title'] != selected_movie)]
    similar_movies = similar_movies.drop_duplicates(subset=['title'])
    
    if 'rating' in movies_df.columns:
        similar_movies = similar_movies.sort_values(by="rating", ascending=False)

    return similar_movies.head(5)


def movie_details(movie_title):
    """Display details of a selected movie and show recommendations."""
    movie = movies_df[movies_df['title'] == movie_title]

    if movie.empty:
        st.warning("⚠️ Movie details not found!")
        return

    movie = movie.iloc[0]
    
    st.markdown(f"<h2 style='text-align: center;'>{movie['title']}</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(movie['posters'], width=250, caption=f"🎬 {movie['title']}", use_container_width=True)

    with col2:
        if 'year' in movie:
            st.markdown(f"<p style='font-size:16px'><b>📅 Year:</b> {movie['year']}</p>", unsafe_allow_html=True)
        if 'genres' in movie:
            st.markdown(f"<p style='font-size:16px'><b>🎭 Genre:</b> {movie['genres']}</p>", unsafe_allow_html=True)
        if 'rating' in movie:
            st.markdown(f"<p style='font-size:16px'><b>⭐ Rating:</b> {movie['rating']}</p>", unsafe_allow_html=True)

    recommendations = get_recommendations(movie_title)

    if not recommendations.empty:
        st.subheader("🎬 You may also like:")
        rec_cols = st.columns(len(recommendations))

        for idx, (_, rec_movie) in enumerate(recommendations.iterrows()):
            with rec_cols[idx]:  
                with st.container():
                    st.image(rec_movie['posters'], width=120, use_container_width=True, caption=rec_movie['title'])
                    if st.button(f"View {rec_movie['title']}", key=f"rec_{rec_movie['title']}"):
                        st.session_state["selected_movie"] = rec_movie['title']
                        st.rerun()


def movie_search_page():
    """Movie search and recommendation interface."""
    if not st.session_state.get("authenticated", False):
        return

    st.markdown("<h1 style='text-align: center; color: #3498db;'>🎬 Movie Catalog</h1>", unsafe_allow_html=True)
    st.subheader(f"Welcome, {st.session_state['username']}!")

    query = st.text_input("🔍 Enter movie name:", value=st.session_state.get("search_query", ""))

    if query:
        st.session_state["search_query"] = query.strip()
        filtered_movies = movies_df[movies_df['title'].str.contains(query, case=False, na=False)].drop_duplicates(subset=['title'])
    else:
        filtered_movies = movies_df.head(9)

    if not filtered_movies.empty:
        cols = st.columns(3)
        for idx, (_, movie) in enumerate(filtered_movies.iterrows()):
            with cols[idx % 3]:
                with st.container():
                    st.image(movie['posters'], width=160, use_container_width=True, caption=movie['title'])
                    if st.button(f"View {movie['title']}", key=f"movie_{movie['title']}"):
                        st.session_state["selected_movie"] = movie['title']
                        st.rerun()

        if st.session_state["selected_movie"]:
            st.divider()
            col1, col2 = st.columns([6, 1])

            with col1:
                movie_details(st.session_state["selected_movie"])
            
            with col2:
                if st.button("❌ Clear", key="clear_details"):
                    st.session_state["selected_movie"] = None
                    st.rerun()
    else:
        st.warning("⚠️ No movies found! Try another search.")


if __name__ == "__main__":
    if st.session_state["authenticated"]:
        movie_search_page()


