from __future__ import annotations

import os

import pandas as pd
from datasets import load_dataset


# Load datasets
def load_data():
    """Load and return the MovieLens and Steam Games datasets."""
    movies_data = load_dataset("ashraq/movielens_ratings", split="train")
    games_data = load_dataset(
        "FronkonGames/steam-games-dataset", split="train"
    )

    movie_lens_df = pd.DataFrame(movies_data)
    steam_games_df = pd.DataFrame(games_data)

    return movie_lens_df, steam_games_df


# Process MovieLens Data
def process_movies_data(movie_lens_df):
    """Process and clean the MovieLens dataset."""
    # Extract and clean year from the title
    movie_lens_df["year"] = movie_lens_df["title"].str.extract(r"\((\d{4})\)")
    movie_lens_df["year"] = movie_lens_df["year"].fillna(0)
    movie_lens_df["title"] = movie_lens_df["title"].str.replace(
        r"\s*\(\d{4}\)", "", regex=True
    )

    return movie_lens_df


# Process Steam Games Data
def process_steam_games_data(steam_games_df):
    """Process and clean the Steam Games dataset."""
    # Select relevant columns
    games_relevent_columns = [
        "Name",
        "Release date",
        "Price",
        "Genres",
        "Tags",
        "Reviews",
        "User score",
        "Movies",
        "Metacritic score",
        "Categories",
        "About the game",
    ]
    steam_games_df = steam_games_df[games_relevent_columns]

    # Handle missing Name
    steam_games_df = steam_games_df.drop(
        steam_games_df.loc[steam_games_df["Name"].isna()].index
    )

    # Extract the year from the release date
    steam_games_df["Release Year"] = pd.to_datetime(
        steam_games_df["Release date"], errors="coerce"
    ).dt.year

    # Clean Release Date
    steam_games_df["Release date"] = steam_games_df["Release date"].apply(
        lambda x: "01 " + x if len(x.split()) == 2 else x
    )

    # Handle missing About the Game values
    steam_games_df = fill_missing_about_game(steam_games_df)

    # Handle missing Categories
    steam_games_df = fill_missing_categories(steam_games_df)

    # Handle missing Genres
    steam_games_df = fill_missing_genres(steam_games_df)

    # Handle missing Tags
    steam_games_df = fill_missing_tags(steam_games_df)

    # Handle missing Movies
    steam_games_df = fill_missing_movies(steam_games_df)

    # Finalize year column
    steam_games_df["year"] = steam_games_df["Release Year"].fillna(0)
    steam_games_df = steam_games_df.rename(columns={"Release Year": "year"})

    return steam_games_df


def fill_missing_about_game(steam_games_df):
    """Fill missing 'About the game' column with appropriate values."""
    for index, row in steam_games_df.iterrows():
        if pd.isnull(row["About the game"]):
            # Check various conditions for 'About the game'
            if "Playtest" in row["Name"]:
                steam_games_df.at[
                    index, "About the game"
                ] = "This is a playtest game."
            elif "Alpha" in row["Name"]:
                steam_games_df.at[
                    index, "About the game"
                ] = "This game is in alpha and still under testing."
            elif "Beta" in row["Name"]:
                steam_games_df.at[
                    index, "About the game"
                ] = "This game is in beta and still under testing."
            elif "Test" in row["Name"]:
                steam_games_df.at[
                    index, "About the game"
                ] = "This game is still under testing."
            elif "SDK" in row["Name"]:
                steam_games_df.at[
                    index, "About the game"
                ] = "Software Development Kit of the game."
            elif "Demo" in row["Name"]:
                steam_games_df.at[
                    index, "About the game"
                ] = "This is a demo version of the game."
            elif "Server" in row["Name"]:
                steam_games_df.at[
                    index, "About the game"
                ] = "This is a server for the game."
            elif "Editor" in row["Name"]:
                steam_games_df.at[
                    index, "About the game"
                ] = "This is an editor for the game."
            else:
                steam_games_df.at[
                    index, "About the game"
                ] = "No description available."

    return steam_games_df


def fill_missing_categories(steam_games_df):
    """Fill missing 'Categories' column with appropriate values."""
    for index, row in steam_games_df.iterrows():
        if pd.isnull(row["Categories"]):
            # Check various conditions for 'Categories'
            if "Playtest" in row["Name"]:
                steam_games_df.at[
                    index, "Categories"
                ] = "Playtest game not playable"
            elif "Alpha" in row["Name"]:
                steam_games_df.at[
                    index, "Categories"
                ] = "Alpha game not playable"
            elif "Beta" in row["Name"]:
                steam_games_df.at[
                    index, "Categories"
                ] = "Beta game not playable"
            elif "Test" in row["Name"]:
                steam_games_df.at[
                    index, "Categories"
                ] = "Test game not playable"
            elif "SDK" in row["Name"]:
                steam_games_df.at[
                    index, "Categories"
                ] = "Software Development Kit of the game not playable"
            elif "Demo" in row["Name"]:
                steam_games_df.at[
                    index, "Categories"
                ] = "Demo game not playable"
            elif "Server" in row["Name"]:
                steam_games_df.at[
                    index, "Categories"
                ] = "Server of a game not playable"
            elif "Editor" in row["Name"]:
                steam_games_df.at[
                    index, "Categories"
                ] = "Editor of a game not playable"
            else:
                steam_games_df.at[index, "Categories"] = "No Category added"

    return steam_games_df


def fill_missing_genres(steam_games_df):
    """Fill missing 'Genres' column with appropriate values."""
    for index, row in steam_games_df.iterrows():
        if pd.isnull(row["Genres"]):
            if "Playtest" in row["Name"]:
                steam_games_df.at[
                    index, "Genres"
                ] = "Playtest game not playable"
            elif "Alpha" in row["Name"]:
                steam_games_df.at[index, "Genres"] = "Alpha game not playable"
            elif "Beta" in row["Name"]:
                steam_games_df.at[index, "Genres"] = "Beta game not playable"
            else:
                steam_games_df.at[index, "Genres"] = "No Genres added"

    return steam_games_df


def fill_missing_tags(steam_games_df):
    """Fill missing 'Tags' column with 'Genres' value."""
    for index, row in steam_games_df.iterrows():
        if pd.isnull(row["Tags"]):
            steam_games_df.at[index, "Tags"] = steam_games_df.at[
                index, "Genres"
            ]

    return steam_games_df


def fill_missing_movies(steam_games_df):
    """Fill missing 'Movies' column with appropriate values."""
    for index, row in steam_games_df.iterrows():
        if pd.isnull(row["Movies"]):
            if "Playtest" in row["Name"]:
                steam_games_df.at[
                    index, "Movies"
                ] = "Playtest game no trailer available"
            elif "Alpha" in row["Name"]:
                steam_games_df.at[
                    index, "Movies"
                ] = "Alpha game no trailer available"
            elif "Beta" in row["Name"]:
                steam_games_df.at[
                    index, "Movies"
                ] = "Beta game no trailer available"
            else:
                steam_games_df.at[index, "Movies"] = "No trailer available"

    return steam_games_df


# ensure the directory exists
def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)


# Save DataFrames to CSV
def save_to_csv(movie_lens_df, steam_games_df):
    """Save the cleaned DataFrames to CSV files."""
    # Save processed data to CSV with cross-platform path handling
    processed_data_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "data", "processed"
    )

    # Create the directory if it does not exist
    # create_directory(processed_data_dir)

    # Save the cleaned data
    movie_lens_df.to_csv(
        os.path.join(processed_data_dir, "processed_movies.csv"), index=False
    )
    steam_games_df.to_csv(
        os.path.join(processed_data_dir, "processed_games.csv"), index=False
    )


# Main function
def main():
    # Load data
    movie_lens_df, steam_games_df = load_data()

    # Process datasets
    movie_lens_df = process_movies_data(movie_lens_df)
    steam_games_df = process_steam_games_data(steam_games_df)

    # Save processed data to CSV files
    save_to_csv(movie_lens_df, steam_games_df)

    print(
        """Data processing complete. Files saved as
        'processed_movies.csv' and 'processed_games.csv'.
        """
    )


# Run the script
if __name__ == "__main__":
    main()
