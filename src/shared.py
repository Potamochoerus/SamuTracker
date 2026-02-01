from pathlib import Path
import pandas as pd
import glob
import yaml
from datetime import timedelta

app_dir = Path(__file__).parent / ".."
threshold_score = 100
with open("tracked_players.yml", "r") as f:
    tracked_players = yaml.safe_load(f)
raw_data_path = app_dir / "data"

# Reformat duration
def str_to_timedelta(s):
    m, sec = map(int, s.split(":"))
    return timedelta(minutes=m, seconds=sec)

def handle_players_with_coma(fields):
    # Keep only the first field, fill the rest with NaN
    expected_cols = 16  # adjust to your CSV's expected number of columns
    new_line = fields[:1] + [pd.NA]*(expected_cols-1)
    return new_line

# Read all matches
def read_history(data_path):
    """
    Read all match history and parse it in a readable way for the app

    :param data_path: Folder where the exported .csv from Bakkesmod are stored
    """
    all_matches = glob.glob(str(data_path / "*.csv"))
    match_history = []
    for match in all_matches:
        df_match = pd.read_csv(match, index_col=None, header=0, on_bad_lines=handle_players_with_coma, engine='python')
        match_history.append(df_match)

    # Regroup all matches
    match_history = pd.concat(match_history, axis=0, ignore_index=True)
    
    # Add date and time
    match_history[["Date", "Time"]] = match_history["Timestamp"].str.split("_", expand = True)

    # Deduplicate in case the same game is added twice
    match_history = match_history.drop_duplicates()

    # For now bakkesmod does not log these for every player
    match_history = match_history.drop(columns = ["Pads", "Boosts", "BoostUsage"])

    # Add game mode
    game_mode = match_history["Timestamp"].value_counts().reset_index()
    game_mode.columns = ["Timestamp", "n_players"]
    game_mode["GameMode"] = game_mode["n_players"].apply(lambda x: f"{int(x/2)}v{int(x/2)}")
    game_mode = game_mode.drop(columns = ["n_players"])
    match_history = pd.merge(match_history, game_mode, on="Timestamp", how="left")
    
    # Select players of interest
    match_history = match_history[(match_history.AccountId.isin(tracked_players.keys()))]

    # Add Fixed name
    match_history["FixedName"] = match_history["AccountId"].map(tracked_players)

    # Reformat possession
    match_history["PossessionTime"] = [str_to_timedelta(x) for x in match_history["PossessionTime"]]
    match_history["PossessionTime"] = match_history["PossessionTime"].dt.total_seconds()

    return match_history

def participation_dict(match_history):
    """
    Generate a participation dictionary containing the list of players in each game
    
    :param match_history: Description
    """
    match_dict = match_history.groupby("Timestamp")["AccountId"].apply(list).to_dict()
    return(match_dict)

match_history = read_history(raw_data_path)
participation_dictionary = participation_dict(match_history)