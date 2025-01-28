import streamlit as st
import requests

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

    # Recommendation feature
    if st.button("Get Recommendations"):
        try:
            response = requests.post(f"{BACKEND_URL}/recommend", json={"username": st.session_state["username"]})
            if response.status_code == 200:
                st.success(response.json()["message"])
                recommendations = response.json().get("recommendations", ["Movie 1", "Movie 2", "Movie 3"])
                st.write("Recommended Movies:")
                for movie in recommendations:
                    st.write(movie)
            else:
                st.error(response.json()["detail"])
        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to the backend: {e}")

# Allow standalone execution
if __name__ == "__main__":
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = True  # Mock authentication for standalone testing
        st.session_state["username"] = "TestUser"

    movie_search_page()
