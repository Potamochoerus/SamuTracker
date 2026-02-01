# Import general lib
import seaborn as sns
from faicons import icon_svg
import numpy as np

# Import data from shared.py
from src.shared import app_dir, match_history, threshold_score, tracked_players, participation_dictionary, variables_dictionary_numeric

# Import plotting functions
from src.plots import boxplot_stat, scatterplot_interactive

# Import shiny
from shiny import reactive
from shiny.express import input, render, ui
from shinywidgets import render_widget

ui.page_opts(title="SamuTracker", fillable=True)

with ui.sidebar(title="Filter games"):
    ui.input_select(id="mode",
                    label="Game mode",
                    choices=["3v3", "2v2", "1v1"])
    
    ui.input_checkbox_group(
        id="players",
        label="Players",
        choices=tracked_players,
        selected=list(tracked_players.keys()),
    )

    ui.input_slider(id="n_games", 
                    label="Number of games to use", 
                    min=1, 
                    max=100, 
                    value=100,
                    step=1)
    
    ui.tags.hr()
    ui.h5("Correlation options")
    ui.input_select(id="x_var",
                label="X variable",
                choices=variables_dictionary_numeric,
                selected="Score")
    
    ui.input_select(id="y_var",
                label="Y variable",
                choices=variables_dictionary_numeric,
                selected="PossessionTime")


with ui.layout_columns():
    with ui.card(full_screen=True):
        ui.card_header("Possession time (s)")

        @render.plot
        def possession_plot():
            plot =  boxplot_stat(df=filtered_mh(), stat="PossessionTime")
            return plot

    with ui.card(full_screen=True):
        ui.card_header("Scores")

        @render.plot
        def score_plot():
            plot =  boxplot_stat(df=filtered_mh(), stat="Score")
            return plot


with ui.layout_columns():
    with ui.card(full_screen=True):
        ui.card_header(f"Custom correlation")

        @render_widget
        def interactive_plot():
            plot = scatterplot_interactive(df=filtered_mh(), x=input.x_var(), y=input.y_var())
            return plot

    with ui.card(full_screen=True):
        @render.data_frame
        def summary_table():
            df = filtered_mh()
            df_grouped = df.groupby("AccountId")[["Goals", "Assists", "Saves", "Shots", "Demolishes"]].sum().reset_index()
            df_grouped["AccountId"] = df_grouped["AccountId"].replace(tracked_players)
            df_grouped = df_grouped.rename(columns={"AccountId": "Player"})
            return df_grouped

ui.include_css(app_dir / "styles.css")

@reactive.calc
def filter_mh_game_player():
    player_list = list(input.players())
    # First, filter by game mode
    filt_mh = match_history[match_history["GameMode"]==input.mode()]
    # Then get only games where all selected players are present
    games_with_all_selected_players = [k for k, v in participation_dictionary.items() if all(x in v for x in input.players())]
    filt_mh = filt_mh[filt_mh["Timestamp"].isin(games_with_all_selected_players)]
    # Keep only entries of players of interest
    filt_mh = filt_mh[filt_mh["AccountId"].isin(player_list)]
    return filt_mh

@reactive.calc
def filtered_mh():
    mh = filter_mh_game_player()
    unique_games = list(set(mh.Timestamp))
    games_selected = sorted(unique_games, reverse=True)[0:input.n_games()]
    mh = mh[mh.Timestamp.isin(games_selected)]
    return mh


@reactive.effect
def _():
    max_n_games = len(list(set(filter_mh_game_player()["Timestamp"])))
    ui.update_slider(id="n_games",
                     max=max_n_games)