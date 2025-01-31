import streamlit as st
import requests

# Ollama API endpoint
OLLAMA_API_URL = "http://localhost:11434/api/generate"


def chat_bot_page():
    """Chatbot page function for integration with the main app."""
    
    st.title("💬 Chatbot")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

    # Display chat history
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    # Input field for user messages
    if prompt := st.chat_input():
        # Add user message to chat history
        st.session_state["messages"].append({
            "role": "user",
            "content": f"{prompt}"
        })
        st.chat_message("user").write(prompt)

        # Prepare payload for Ollama
        payload = {
            "model": "llama3.2",
            "prompt": f"You are an intelligent game recommendation assistant. Your task is to suggest 5 video games that closely match the user's movie-related input, which may be a movie title, description, or any related details.\n\nFor each recommendation, provide:\n1. Game Title\n2. A short description of the game\n3. Reasons for the recommendation based on the given input\n4. A similarity score (0-100%) based on thematic, narrative, and gameplay elements\n\nEnsure recommendations prioritize gameplay mechanics, storyline, setting, and overall experience similar to the movie. If the input is vague, ask clarifying questions before making recommendations. Keep responses structured and concise.\n\nUser Query: {prompt}",
            "stream": False
        }

        # Send request to Ollama API
        try:
            response = requests.post(OLLAMA_API_URL, json=payload)
            if response.status_code == 200:
                assistant_msg = response.json().get("response", "I couldn't process that.")
            else:
                assistant_msg = f"Error from Ollama: {response.status_code} - {response.text}"
        except requests.RequestException as e:
            assistant_msg = "⚠️ Failed to connect to Ollama. Please check if the API is running."

        # Add assistant message to chat history
        st.session_state["messages"].append({"role": "assistant", "content": assistant_msg})
        st.chat_message("assistant").write(assistant_msg)
