from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import hashlib
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os
import torch
import uvicorn
from torch_geometric.data import Data
import pickle
import pandas as pd
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.gnn.gnn import GNNRecommender

model_args = {
    "num_features": 1093,
    "hidden_channels": [128, 256, 256, 512],
    "classifier_hidden_dims": [256],
    "use_dropout_in_conv": True,
    "use_dropout_in_classifier": True,
    "dropout_rate": 0.3,
    "use_input_masking": True,
    "debug": False
}

model = GNNRecommender(**model_args)  

# Load the saved state_dict
model.load_state_dict(torch.load('../models/gnn/best-model.pt', map_location=torch.device('cpu')))
model.eval()


# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI()



movie_df = pd.read_csv('../data/db-data/movies.csv')
game_df = pd.read_csv('../data/db-data/games.csv')

with open('../models/gnn/movie_map.pkl', 'rb') as f:
    movie_map = pickle.load(f)
with open('../models/gnn/game_map.pkl', 'rb') as f:
    game_map = pickle.load(f)
with open('../models/gnn/user_map.pkl', 'rb') as f:
    user_map = pickle.load(f)

# Hashing function
def hash_password(password):
    """Hash a password for secure storage."""
    return hashlib.sha256(password.encode()).hexdigest()

# Function to connect to the database
def get_db_connection():
    """Establish a database connection."""
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

# Pydantic models for request bodies
class User(BaseModel):
    username: str
    password: str

class NewUser(User):
    confirm_password: str

# FastAPI endpoints
@app.post("/login")
def login(user: User):
    """Login endpoint."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s AND password_hash = %s",
                   (user.username, hash_password(user.password)))
    user_record = cursor.fetchone()
    conn.close()

    if not user_record:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    return {"message": f"Welcome back, {user.username}!"}

@app.post("/signup")
def signup(new_user: NewUser):
    """Signup endpoint."""
    if new_user.password != new_user.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                       (new_user.username, hash_password(new_user.password)))
        conn.commit()
        conn.close()
        return {"message": "Account created successfully!"}
    except psycopg2.IntegrityError:
        conn.rollback()
        conn.close()
        raise HTTPException(status_code=400, detail="Username already exists")
    
@app.post("/recommend")
def recommend(data: dict, top_k: int = 10):

    num_users = len(user_map)
    num_movies = len(movie_map)
    num_games = len(game_map)
    num_nodes = num_users + num_movies + num_games
    node_features = torch.zeros(num_nodes, model_args["num_features"])  # Correct shape

    liked_movies = data.get('movies', [])
    liked_games = data.get('games', [])

    # Map the liked items to their internal IDs
    liked_movie_edges = [[movie_map[movie_id], movie_map[movie_id]] for movie_id in liked_movies if movie_id in movie_map]
    liked_game_edges = [[game_map[game_id], game_map[game_id]] for game_id in liked_games if game_id in game_map]

    # Get all movies and games
    all_movies = set(movie_map.keys())
    all_games = set(game_map.keys())

    # Determine unwatched/unrated movies and games
    unwatched_movies = all_movies - set(liked_movies)
    unrated_games = all_games - set(liked_games)

    # Create test edges for movies and games
    test_movie_edges = [[movie_map[movie_id], movie_map[movie_id]] for movie_id in unwatched_movies]
    test_game_edges = [[game_map[game_id], game_map[game_id]] for game_id in unrated_games]
    test_edges = test_movie_edges + test_game_edges
    test_edge_index = torch.tensor(test_edges, dtype=torch.long).t().contiguous()

    with torch.no_grad():
        test_data = Data(x=node_features, edge_index=test_edge_index)
        predictions = model(test_data)
    
    predictions = predictions.squeeze()

    # Separate movie and game predictions
    num_movie_edges = len(test_movie_edges)
    movie_predictions = predictions[:num_movie_edges].tolist()
    game_predictions = predictions[num_movie_edges:].tolist()

    # Combine movie and game predictions with their respective IDs
    movie_recommendations = list(zip(unwatched_movies, movie_predictions))
    game_recommendations = list(zip(unrated_games, game_predictions))

    # Sort by predicted rating and select the top movies and games
    top_movie_recommendations = sorted(movie_recommendations, key=lambda x: x[1], reverse=True)[:top_k]
    top_game_recommendations = sorted(game_recommendations, key=lambda x: x[1], reverse=True)[:top_k]

    recommended_items = []
    for item_id, pred_rating in top_movie_recommendations:
        item_id = int(item_id)
        pred_rating = float(pred_rating)  # Ensure pred_rating is a Python float

        print(f"item_id: {item_id}, pred_rating: {pred_rating}, type(pred_rating): {type(pred_rating)}")

        # Ensure pred_rating is a single float
        pred_rating = float(pred_rating) if isinstance(pred_rating, (int, float)) else float(pred_rating[0])
        movie_info = movie_df[movie_df.movieId == item_id]
        movie_title = movie_info['title'].iloc[0] if not movie_info.empty else f"Unknown Movie ({item_id})"
        recommended_items.append({
            'type': 'Movie',
            'id': item_id,
            'title': movie_title,
            'predicted_rating': round(pred_rating, 2)
        })

    for item_id, pred_rating in top_game_recommendations:
        item_id = int(item_id)
        pred_rating = float(pred_rating)  # Ensure pred_rating is a Python float


        print(f"item_id: {item_id}, pred_rating: {pred_rating}, type(pred_rating): {type(pred_rating)}")

        # Ensure pred_rating is a single float
        pred_rating = float(pred_rating) if isinstance(pred_rating, (int, float)) else float(pred_rating[0])
        game_info = game_df[game_df['app_id'] == item_id]
        game_title = game_info['title'].iloc[0] if not game_info.empty else f"Unknown Game ({item_id})"
        recommended_items.append({
            'type': 'Game',
            'id': item_id,
            'title': game_title,
            'predicted_rating': round(pred_rating, 2)
        })

    return recommended_items




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)