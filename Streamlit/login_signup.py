import streamlit as st
import requests

# Define the FastAPI backend URL
BACKEND_URL = "http://127.0.0.1:8000"

# Manage session state for login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Function for the movies page
def movies_page():
    st.title("Movies Page")
    st.write(f"Welcome to the Movies Page, {st.session_state.username}!")
    st.button("Logout", on_click=logout)

# Logout function
def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""

# Login page
def login_page():
    st.title("Login Page")
    menu = ["Login", "Sign Up"]
    choice = st.radio("Select an option", menu)

    if choice == "Login":
        st.subheader("Login to Your Account")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username and password:
                response = requests.post(f"{BACKEND_URL}/login", json={"username": username, "password": password})
                if response.status_code == 200:
                    st.success(response.json()["message"])
                    # Set session state
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    movies_page()
                else:
                    st.error(response.json()["detail"])
            else:
                st.warning("Please enter both username and password.")

    elif choice == "Sign Up":
        st.subheader("Create a New Account")
        new_username = st.text_input("Choose a Username")
        new_password = st.text_input("Choose a Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        if st.button("Sign Up"):
            if new_username and new_password and confirm_password:
                response = requests.post(f"{BACKEND_URL}/signup", 
                                         json={"username": new_username, 
                                               "password": new_password, 
                                               "confirm_password": confirm_password})
                if response.status_code == 200:
                    st.success(response.json()["message"])
                else:
                    st.error(response.json()["detail"])
            else:
                st.warning("Please fill in all fields.")

# Main execution
if __name__ == "__main__":
    if st.session_state.logged_in:
        movies_page()  # Redirect to the movies page
    else:
        login_page()  # Show the login page
