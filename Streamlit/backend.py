from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import hashlib
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI()

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
def recommend(data: dict):
    pass