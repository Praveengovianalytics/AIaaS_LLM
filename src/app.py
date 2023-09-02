import streamlit as st
from view import view_app

# Create a dictionary to store user session data
sessions = {}


def main():
    st.set_page_config(page_title="BTO Chatbot")
    st.title("BTO Chatbot")

    session_state = st.session_state

    if not hasattr(session_state, "username"):
        # User is not logged in
        show_login_form(session_state)
    else:
        # User is logged in
        show_chat_app(session_state)


def show_login_form(session_state):
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if authenticate_user(username, password):
            st.session_state.username = username  # Store the logged-in user's username
            st.success("Logged in!")
            show_chat_app(st.session_state)
        else:
            st.error("Invalid credentials")


def authenticate_user(username, password):
    # Add your authentication logic here
    # Example: Check if username and password are valid
    return username == "bto_user" and password == "bto@123"


def show_chat_app(session_state):
    st.title("Chat App")
    st.write(f"Welcome, {session_state.username}!")

    # Logout button
    if st.button("Logout"):
        end_session(session_state)
        st.info("Logged out!")

    # Display chat app here
    view_app.show_chat_app(st, session_state.username)


def end_session(session_state):
    if hasattr(session_state, "username"):
        delattr(session_state, "username")


if __name__ == "__main__":
    main()
