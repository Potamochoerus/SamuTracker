from pathlib import Path
import pandas as pd
import glob
import yaml
import numpy as np

app_dir = Path(__file__).parent / ".."
threshold_score = 100
with open("tracked_players.yml", "r") as f:
    tracked_players = yaml.safe_load(f)
raw_data_path = app_dir / "data"

variables_dictionary_all = {
    "team": "Team",
    "player": "Player name",
    "id": "Account ID",
    "fixedname": "Player",
    "timestamp": "Time stamp",
    "date": "Date",
    "time": "Time",
    "core_shots": "Shots",
    "core_shots_against": "Shots opponents",
    "core_goals": "Goals",
    "core_goals_against": "Goals opponents",
    "core_saves": "Saves",
    "core_assists": "Assists",
    "core_score": "Score",
    "core_mvp": "MVP",
    "core_shooting_percentage": "Successful shots (%)",
    "boost_bpm": "Boost used (u/min)",
    "boost_bcpm": "Boost collected (u/min)",
    "boost_avg_amount": "Average boost",
    "boost_amount_collected": "Total boost collected",
    "boost_amount_stolen": "Boost stolen",
    "boost_amount_collected_big": "Boost collected (big pads)",
    "boost_amount_stolen_big": "Boost stolen (big pads)",
    "boost_amount_collected_small": "Boost collected (small pads)",
    "boost_amount_stolen_small": "Boost stolen (small pads)",
    "boost_count_collected_big": "Boost collected (n big pads)",
    "boost_count_stolen_big": "Boost stolen (n big pads)",
    "boost_count_collected_small": "Boost collected (n small pads)",
    "boost_count_stolen_small": "Boost stolen (n small pads)",
    "boost_amount_overfill": "Boost overfill",
    "boost_amount_overfill_stolen": "Boost overfill stolen",
    "boost_amount_used_while_supersonic": "Boost wasted while supersonic",
    "boost_time_zero_boost": "Time at zero boost (s)",
    "boost_percent_zero_boost": "Time at zero boost (%)",
    "boost_time_full_boost": "Time at full boost (s)",
    "boost_percent_full_boost": "Time at full boost (%)",
    "boost_time_boost_0_25": "Time boost 0-25 (s)",
    "boost_time_boost_25_50": "Time boost 25-50 (s)",
    "boost_time_boost_50_75": "Time boost 50-75 (s)",
    "boost_time_boost_75_100": "Time boost 75-100 (s)",
    "boost_percent_boost_0_25": "Time boost 0-25 (%)",
    "boost_percent_boost_25_50": "Time boost 25-50 (%)",
    "boost_percent_boost_50_75": "Time boost 50-75 (%)",
    "boost_percent_boost_75_100": "Time boost 75-100 (%)",
    "movement_avg_speed": "Avg speed",
    "movement_total_distance": "Total distance",
    "movement_time_supersonic_speed": "Time in supersonic (s)",
    "movement_time_boost_speed": "Time using boost (s)",
    "movement_time_slow_speed": "Time slow (s)",
    "movement_time_ground": "Time on the ground (s)",
    "movement_time_low_air": "Time low in the air (s)",
    "movement_time_high_air": "Time high in the air (s)",
    "movement_time_powerslide": "Time powersliding (s)",
    "movement_count_powerslide": "Number of powerslides",
    "movement_avg_powerslide_duration": "Average duration of powerslides (s)",
    "movement_avg_speed_percentage" : "Average speed (%)",
    "movement_percent_slow_speed": "Time slow (%)",
    "movement_percent_boost_speed": "Time boost (%)",
    "movement_percent_supersonic_speed": "Time in supersonic (%)",
    "movement_percent_ground": "Time on ground (%)",
    "movement_percent_low_air": "Time low in the air (%)",
    "movement_percent_high_air": "Time high in the air (%)",
    "positioning_avg_distance_to_ball": "Avg distance to ball",
    "positioning_avg_distance_to_ball_possession": "Avg distance to ball during possession",
    "positioning_avg_distance_to_ball_no_possession": "Avg distance to ball without possession",
    "positioning_avg_distance_to_mates": "Avg distance to mates",
    "positioning_time_defensive_third": "Time defensive third (s)",
    "positioning_time_neutral_third": "Time neutral third (s)",
    "positioning_time_offensive_third": "Time offensive third (s)",
    "positioning_time_defensive_half": "Time defensive half (s)",
    "positioning_time_offensive_half": "Time offensive half (s)",
    "positioning_time_behind_ball": "Time behind ball (s)",
    "positioning_time_infront_ball": "Time in front ball (s)",
    "positioning_time_most_back": "Time last player (s)",
    "positioning_time_most_forward": "Time first player (s)",
    "positioning_time_closest_to_ball": "Time closest to ball (s)",
    "positioning_time_farthest_from_ball": "Time farthest to ball (s)",
    "positioning_percent_defensive_third": "Time defensive third (%)",
    "positioning_percent_neutral_third": "Time neutral third (%)",
    "positioning_percent_offensive_third": "Time offensive third (%)",
    "positioning_percent_defensive_half": "Time defensive half (%)",
    "positioning_percent_offensive_half": "Time offensive half (%)",
    "positioning_percent_behind_ball": "Time behind ball (%)",
    "positioning_percent_infront_ball": "Time in front ball (%)",
    "positioning_percent_most_back": "Time last player (%)",
    "positioning_percent_most_forward": "Time first player (%)",
    "positioning_percent_closest_to_ball": "Time closest to ball (%)",
    "positioning_percent_farthest_from_ball": "Time farthest to ball (%)",
    "demo_inflicted": "Demolishes",
    "demo_taken": "Demolishes taken",
    "positioning_goals_against_while_last_defender": "Goals taken when last defender",
    "gamelength": "Game length (s)",
    "gamewin": "Result",
    "gamemode": "Game mode"
}

# Read all matches
def read_history(data_path):
    """
    Read all match history and parse it in a readable way for the app

    :param data_path: Folder where the exported .csv from Bakkesmod are stored
    """
    all_matches = data_path / "main.pkl"
    match_history = pd.read_pickle(all_matches)

    # Add date and time
    match_history[["date", "time"]] = match_history["timestamp"].str.split(
        "T", expand=True
    )

    # Deduplicate in case the same game is added twice
    match_history = match_history.drop_duplicates()

    # Add game mode
    game_mode = match_history["timestamp"].value_counts().reset_index()
    game_mode.columns = ["timestamp", "n_players"]
    game_mode["gamemode"] = game_mode["n_players"].apply(
        lambda x: f"{int(x/2)}v{int(x/2)}"
    )
    game_mode = game_mode.drop(columns=["n_players"])
    match_history = pd.merge(match_history, game_mode, on="timestamp", how="left")

    # Compute win/loose
    win_df = (
        match_history.pivot_table(
            index="timestamp", columns="team", values="core_goals", aggfunc="sum"
        )
        .reset_index()
        .rename_axis(None, axis=1)
    )
    win_df["winner"] = np.where(
        win_df["blue"] > win_df["orange"],
        "blue",
        np.where(win_df["orange"] > win_df["blue"], "orange", "draw"),
    )
    win_df = win_df[["timestamp", "winner"]]
    match_history = pd.merge(match_history, win_df, on="timestamp", how="left")
    match_history["gamewin"] = np.where(
        match_history["winner"] == match_history["team"], "win", "loss"
    )
    match_history = match_history.drop(columns=["winner"])
    match_history.rename(columns=variables_dictionary_all, inplace=True)

    return match_history


def participation_dict(match_history):
    """
    Generate a participation dictionary containing the list of players in each game

    :param match_history: Description
    """
    timestamp = variables_dictionary_all["timestamp"]
    id = variables_dictionary_all["id"]
    match_dict = match_history.groupby(timestamp)[id].apply(list).to_dict()
    return match_dict


match_history = read_history(raw_data_path)
participation_dictionary = participation_dict(match_history)
numeric_variables = match_history.select_dtypes(include="number").columns.tolist()
