import streamlit as st

def movie_search_page():
    """Movie search and display interface template."""
    if "username" not in st.session_state:
        st.session_state["username"] = "TestUser"
    
    st.title("Movie Search")
    st.subheader(f"Welcome, {st.session_state['username']}!")
    st.write("Search for movies and see their posters.")

    # Placeholder for search functionality
    query = st.text_input("Enter movie name:")
    if st.button("Search"):
        if query:
            # Simulated search results
            st.success(f"Displaying results for '{query}'")
            movies = [
                {"Title": "Movie 1", "Poster": "https://via.placeholder.com/150"},
                {"Title": "Movie 2", "Poster": "https://via.placeholder.com/150"},
                {"Title": "Movie 3", "Poster": "https://via.placeholder.com/150"}
            ]
            
            # Display simulated movie results
            for movie in movies:
                st.image(movie["Poster"], width=150, caption=movie["Title"])
        else:
            st.warning("Please enter a movie name to search.")

# Allow the script to run independently for testing
if __name__ == "__main__":
    movie_search_page()
