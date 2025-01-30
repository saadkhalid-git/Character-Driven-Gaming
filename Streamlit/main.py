import streamlit as st
from login_signup import login_page
from movie_page import movie_search_page
from Movie_rec import recommendation_page  # Import recommendation page

# Main entry point
if __name__ == "__main__":
    # Initialize session state
    if "authenticated" not in st.session_state:
        st.session_state['authenticated'] = False
        st.session_state['username'] = None
    if "page" not in st.session_state:
        st.session_state['page'] = "movie_search"  

    # Route based on authentication
    if st.session_state['authenticated']:
        # Navigation options for authenticated users
        with st.sidebar:
            st.title("Navigation")
            page_selection = st.radio(
                "Go to:",
                ["Movie Search", "Movie Recommendations"],  
                index=0 if st.session_state["page"] == "movie_search" else 1,
            )

            # Update the page based on user selection
            st.session_state["page"] = (
                "movie_search" if page_selection == "Movie Search" else "recommendation"
            )

        # Display the selected page
        if st.session_state["page"] == "movie_search":
            movie_search_page()
        elif st.session_state["page"] == "recommendation":
            recommendation_page()
    else:
        login_page()
