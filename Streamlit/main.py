import streamlit as st
from login_signup import login_page
from movie_page import movie_search_page
from movie_rec import recommendation_page
from movie_game_recommendation import recommendations
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname('__file__'), '..')))

def logout():
    """Logout function to reset session state."""
    st.session_state["authenticated"] = False
    st.session_state["username"] = None
    st.session_state["selected_movie"] = None
    st.session_state["search_query"] = ""
    st.experimental_rerun()


# ✅ Main Entry Point
if __name__ == "__main__":
    # Initialize session state variables
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        st.session_state["username"] = None
    if "page" not in st.session_state:
        st.session_state["page"] = "movie_search"  

    # ✅ Navigation for Authenticated Users
    if st.session_state["authenticated"]:
        with st.sidebar:
            st.title("📌 Navigation")
            page_selection = st.radio(
                "Go to:",
                ["🎬 Movie Search", "🌟 Movie Recommendations", "🎮 Game & Movie Recs"],  # ✅ Added "Game & Movie Recs"
                index=0 if st.session_state["page"] == "movie_search" else
                      1 if st.session_state["page"] == "recommendation" else 2,
            )

            # ✅ Map selection to session state
            if page_selection == "🎬 Movie Search":
                st.session_state["page"] = "movie_search"
            elif page_selection == "🌟 Movie Recommendations":
                st.session_state["page"] = "recommendation"
            elif page_selection == "🎮 Game & Movie Recs":
                st.session_state["page"] = "game_movie_recs"

            # ✅ Logout Button
            st.button("🚪 Logout", key="logout_button", on_click=logout)

        # ✅ Display the selected page
        if st.session_state["page"] == "movie_search":
            movie_search_page()
        elif st.session_state["page"] == "recommendation":
            recommendation_page()
        elif st.session_state["page"] == "game_movie_recs":
            recommendations()

    else:
        login_page()
