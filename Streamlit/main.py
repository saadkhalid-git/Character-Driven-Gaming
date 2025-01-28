import streamlit as st
from login_signup import login_page
from movie_page import movie_search_page

# Main entry point
if __name__ == "__main__":
    # Initialize session state
    if "authenticated" not in st.session_state:
        st.session_state['authenticated'] = False
        st.session_state['username'] = None

    # Route based on authentication
    if st.session_state['authenticated']:
        movie_search_page()  # Load movie search page
    else:
        login_page()  # Load login/signup page