# Cross Domain Recommendation System

## Overview
This project integrates FastAPI as the backend, Streamlit as the frontend, and Ollama as a locally hosted chatbot. Additionally, it includes a Graph Neural Network (GNN) model for recommending movies and games based on user preferences.

## Features
- **User Authentication**: Sign up and log in using FastAPI with PostgreSQL database.
- **Chatbot Interaction**: Communicate with the Ollama chatbot via a local server.
- **Movie & Game Recommendation**: Uses a trained GNN model to suggest movies and games based on user interactions.
- **Frontend UI**: Built with Streamlit for a simple and intuitive interface.

## Technologies Used
- **FastAPI**: Backend framework for handling API requests.
- **Streamlit**: Frontend framework for interactive UI.
- **Ollama**: Locally served chatbot for AI interactions.
- **PyTorch & PyG (PyTorch Geometric)**: Used to build and run the GNN model.
- **PostgreSQL**: Database for storing user authentication data.
- **Requests**: For API communication between components.
- **Pandas**: For data handling and processing.

## Installation

### Prerequisites
Ensure you have the following installed:
- Python 3.8+
- FastAPI
- Streamlit
- Requests
- Ollama (locally running chatbot)
- PostgreSQL
- PyTorch & PyTorch Geometric

### Setup

1. **Clone the Repository**
   ```sh
   git clone git@github.com:saadkhalid-git/cross-domain-recommender-movies-and-games.git
   cd cross-domain-recommender-movies-and-games
   ```

2. **Create and Activate Virtual Environment**
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**
   ```sh
   pip install -r requirements.txt
   ```

4. **Set Up Database**
   - Create a PostgreSQL database.
   - Add the database URL to a `.env` file:
     ```sh
     DATABASE_URL=postgresql://user:password@localhost/dbname
     ```

5. **Start the FastAPI Backend**
   ```sh
   uvicorn main:app --reload
   ```

6. **Run the Streamlit Frontend**
   ```sh
   streamlit run app.py
   ```

7. **Start Ollama Chatbot Server**
   ```sh
   ollama serve
   ```

## Usage
- Open the Streamlit web UI in your browser.
- Log in or sign up to access the chatbot and recommendation system.
- Provide ratings for movies and games to get recommendations.
- Start chatting with the locally hosted AI.

## API Endpoints
- `POST /login` - User authentication.
- `POST /signup` - User registration.
- `POST /chat` - Send messages to the chatbot.
- `POST /recommend` - Get movie and game recommendations.
- `GET /status` - Check API status.

## Future Enhancements
- Deploying the project to a cloud environment.
- Enhancing the chatbot capabilities with fine-tuned models.
- Expanding the recommendation system to include more media categories.
- Adding a UI feature for users to browse recommendations interactively.

## License
This project is open-source and available under the [MIT License](LICENSE).

