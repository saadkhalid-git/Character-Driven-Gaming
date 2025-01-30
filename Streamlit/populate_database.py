import pandas as pd
import psycopg2
from psycopg2 import sql
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

csv_file_path = '../data/db-data/movies.csv'

DATABASE_URL = os.getenv("DATABASE_URL")
DB_NAME = "Recommendations"

# Step 1: Connect to PostgreSQL server and create the database if it doesn't exist
def create_database():
    try:
        # Remove the database name from the URL for this step
        server_url = DATABASE_URL.rsplit('/', 1)[0]

        # Connect to the PostgreSQL server (default database: postgres)
        conn = psycopg2.connect(f"{server_url}/postgres")
        conn.autocommit = True
        cursor = conn.cursor()

        # Check if the 'Recommendations' database exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
        if not cursor.fetchone():
            # Create the 'Recommendations' database
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
            print(f"Database '{DB_NAME}' created successfully.")
        else:
            print(f"Database '{DB_NAME}' already exists.")

        cursor.close()
        conn.close()
    except Exception as e:
        print("Error creating database:", e)

# Step 2: Create 'movies' table and populate it with data from CSV
def create_and_populate_movies_table():
    try:
        # Use the DATABASE_URL directly to connect to the Recommendations database
        engine = create_engine(DATABASE_URL)
        conn = engine.connect()

        # Read the CSV file into a DataFrame
        df = pd.read_csv(csv_file_path)

        # Write the DataFrame to the 'movies' table
        df.to_sql("movies", engine, if_exists="replace", index=False)
        print("Table 'movies' created and data inserted successfully.")

        conn.close()
    except Exception as e:
        print("Error populating 'movies' table:", e)

csv = '../data/processed/processed_movies.csv'
def create_and_populate_another_table():
    try:
        # Use the DATABASE_URL directly to connect to the Recommendations database
        engine = create_engine(DATABASE_URL)
        conn = engine.connect()

        # Read the CSV file into a DataFrame
        df = pd.read_csv(csv)

        # Write the DataFrame to a new table, e.g., 'movies_backup'
        df.to_sql("movies_backup", engine, if_exists="replace", index=False)
        print("Table 'movies_backup' created and data inserted successfully.")

        conn.close()
    except Exception as e:
        print("Error populating 'movies_backup' table:", e)

create_database()
#create_and_populate_movies_table()
#create_and_populate_another_table()