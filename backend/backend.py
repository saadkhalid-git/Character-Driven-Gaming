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


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI()



movie_df = pd.read_csv('../data/db-data/movies.csv')
game_df = pd.read_csv('../data/db-data/games.csv')

games_new = pd.read_csv('../data/games_new.csv')

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
    # Load the saved graph data
    graph_data = torch.load("../models/gnn/graph_data.pt")

    node_features = graph_data.x  # Precomputed node features
    edge_index = graph_data.edge_index  # Precomputed edge structure
    edge_weight = graph_data.edge_attr  # Precomputed edge weights

    num_users = len(user_map)
    num_movies = len(movie_map)
    num_games = len(game_map)


    # Extract user ratings from request
    liked_movies = data.get("movies", [])
    liked_games = data.get("games", [])

    # Convert user ratings into a dictionary for easy lookup
    movie_ratings = {m["id"]: m["rating"] for m in liked_movies}
    game_ratings = {g["id"]: g["rating"] for g in liked_games}

    # Dynamically add user edges based on given ratings
    user_node = 0  # Assuming single-user inference

    new_edges = []
    new_edge_weights = []

    # Add edges for movies with user ratings
    for movie_id, rating in movie_ratings.items():
        if movie_id in movie_map:
            new_edges.append([user_node, movie_map[movie_id]])  # User → Movie edge
            new_edge_weights.append(rating)  # Edge weight = User rating

    # Add edges for games with user ratings
    for game_id, rating in game_ratings.items():
        if game_id in game_map:
            new_edges.append([user_node, game_map[game_id]])  # User → Game edge
            new_edge_weights.append(rating)  # Edge weight = User rating

    # Convert new edges into tensors
    if new_edges:
        new_edge_index = torch.tensor(new_edges, dtype=torch.long).t().contiguous()
        new_edge_weights = torch.tensor(new_edge_weights, dtype=torch.float)

        # Append new user-item edges to existing edges
        edge_index = torch.cat([edge_index, new_edge_index], dim=1)
        edge_weight = torch.cat([edge_weight, new_edge_weights], dim=0)

    # Find all items (movies & games) that the user hasn't rated yet
    all_movies = set(movie_map.keys())
    all_games = set(game_map.keys())

    unwatched_movies = all_movies - set(movie_ratings.keys())
    unrated_games = all_games - set(game_ratings.keys())

    # Generate test edges for prediction (User → Unwatched Movies & Unrated Games)
    test_movie_edges = [[user_node, movie_map[movie_id]] for movie_id in unwatched_movies]
    test_game_edges = [[user_node, game_map[game_id]] for game_id in unrated_games]

    # Convert test edges to tensor
    test_edges = test_movie_edges + test_game_edges
    test_edge_index = torch.tensor(test_edges, dtype=torch.long).t().contiguous()

    with torch.no_grad():
        test_data = Data(x=node_features, edge_index=test_edge_index, edge_weight=edge_weight)
        predictions = model(test_data)

    predictions = predictions.squeeze()

    # Separate movie and game predictions
    num_movie_edges = len(test_movie_edges)
    movie_predictions = predictions[:num_movie_edges].tolist()
    game_predictions = predictions[num_movie_edges:].tolist()

    # Combine predicted scores with item IDs
    movie_recommendations = list(zip(unwatched_movies, movie_predictions))
    game_recommendations = list(zip(unrated_games, game_predictions))

    # Sort and get top-k recommendations
    top_movie_recommendations = sorted(movie_recommendations, key=lambda x: x[1], reverse=True)[:top_k-5]
    top_game_recommendations = sorted(game_recommendations, key=lambda x: x[1], reverse=True)[:top_k-5]

    recommended_items = []

    for item_id, pred_rating in top_movie_recommendations:
        item_id = int(item_id)
        pred_rating = float(pred_rating)

        movie_info = movie_df[movie_df.movieId == item_id]
        movie_title = movie_info["title"].iloc[0] if not movie_info.empty else f"Unknown Movie ({item_id})"
        recommended_items.append({
            "type": "Movie",
            "id": item_id,
            "title": movie_title,
            "predicted_rating": round(pred_rating, 2)
        })

    for item_id, pred_rating in top_game_recommendations:
        item_id = int(item_id)
        pred_rating = float(pred_rating)

        game_info = game_df[game_df["app_id"] == item_id]
        game_title = game_info["title"].iloc[0] if not game_info.empty else f"Unknown Game ({item_id})"
        recommended_items.append({
            "type": "Game",
            "id": item_id,
            "title": game_title,
            "predicted_rating": round(pred_rating, 2)
        })

    return recommended_items



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)