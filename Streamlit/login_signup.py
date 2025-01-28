import streamlit as st
import requests

# FastAPI backend URL
BACKEND_URL = "http://127.0.0.1:8000"  # Replace with the actual URL of your FastAPI backend

def login_page():
    """Login and Sign-Up Interface."""
    st.title("Login Page")
    menu = ["Login", "Sign Up"]
    choice = st.radio("Select an option", menu)

    if choice == "Login":
        st.subheader("Login to Your Account")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username and password:
                try:
                    response = requests.post(f"{BACKEND_URL}/login", json={"username": username, "password": password})
                    if response.status_code == 200:
                        st.success(response.json()["message"])
                        st.session_state["authenticated"] = True
                        st.session_state["username"] = username
                    else:
                        st.error(response.json()["detail"])
                except requests.exceptions.RequestException as e:
                    st.error(f"Connection error: {e}")
            else:
                st.warning("Please enter both username and password.")

    elif choice == "Sign Up":
        st.subheader("Create a New Account")
        new_username = st.text_input("Choose a Username")
        new_password = st.text_input("Choose a Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
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

# Allow standalone execution
if __name__ == "__main__":
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        st.session_state["username"] = None

    login_page()
