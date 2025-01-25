import streamlit as st
import hashlib

user_db = {}

def hash_password(password):
    """Hash a password for secure storage."""
    return hashlib.sha256(password.encode()).hexdigest()

def login_page():
    """Display login and sign-up interface."""
    st.title("Login Page")
    menu = ["Login", "Sign Up"]
    choice = st.radio("Select an option", menu)

    if choice == "Login":
        st.subheader("Login to Your Account")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username in user_db and user_db[username] == hash_password(password):
                st.success(f"Welcome back, {username}!")
            else:
                st.error("Invalid username or password. Please try again.")

    elif choice == "Sign Up":
        st.subheader("Create a New Account")
        new_username = st.text_input("Choose a Username")
        new_password = st.text_input("Choose a Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        if st.button("Sign Up"):
            if new_password != confirm_password:
                st.warning("Passwords do not match. Please try again.")
            elif new_username in user_db:
                st.warning("Username already exists. Please choose a different username.")
            else:
                user_db[new_username] = hash_password(new_password)
                st.success("Account created successfully! You can now log in.")

# Main execution
if __name__ == "__main__":
    login_page()
