import streamlit as st
import requests

# FastAPI backend URL
BACKEND_URL = "http://0.0.0.0:8000"

def login_page():
    """Login and Sign-Up Interface using tabs."""
    st.title("Login Page")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.subheader("Login to Your Account")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            if username and password:
                try:
                    response = requests.post(f"{BACKEND_URL}/login", json={"username": username, "password": password})
                    if response.status_code == 200:
                        st.success(response.json()["message"])
                        st.session_state["authenticated"] = True
                        st.session_state["username"] = username
                        st.session_state["page"] = "movie_search_page"
                        st.rerun()
                    else:
                        st.error(response.json()["detail"])
                except requests.exceptions.RequestException as e:
                    st.error(f"Connection error: {e}")
            else:
                st.warning("Please enter both username and password.")
    
    with tab2:
        st.subheader("Create a New Account")
        new_username = st.text_input("Choose a Username", key="signup_username")
        new_password = st.text_input("Choose a Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_password")
        if st.button("Sign Up"):
            if new_username and new_password and confirm_password:
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/signup",
                        json={
                            "username": new_username,
                            "password": new_password,
                            "confirm_password": confirm_password,
                        },
                    )
                    if response.status_code == 200:
                        st.success(response.json()["message"])
                    else:
                        st.error(response.json()["detail"])
                except requests.exceptions.RequestException as e:
                    st.error(f"Connection error: {e}")
            else:
                st.warning("Please fill in all fields.")

def logout():
    """Logout function to reset session state and rerun."""
    st.session_state["authenticated"] = False
    st.session_state["username"] = None
    st.session_state["selected_movie"] = None
    st.session_state["filtered_movies"] = None  # Ensure reset
    st.session_state["search_query"] = ""
    
    st.rerun()

# Allow standalone execution
if __name__ == "__main__":
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        st.session_state["username"] = None
    
    login_page()
