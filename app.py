# Import general lib
import seaborn as sns
import numpy as np

# Import data from shared.py
from src.shared import (
    app_dir,
    match_history,
    tracked_players,
    participation_dictionary,
    variables_dictionary_numeric,
)

# Import plotting functions
from src.plots import boxplot_stat, scatterplot_interactive

# Import shiny
from shiny import reactive
from shiny.express import input, render, ui
from shinywidgets import render_widget

ui.page_opts(title="SamuTracker", fillable=True)

with ui.sidebar(title="Filter games"):
    ui.input_select(id="mode", label="Game mode", choices=["3v3", "2v2", "1v1"])

    @render.ui
    def dynamic_player_inputs():
        inputs_player = []
        for i in tracked_players.items():
            inputs_player.append(
                ui.input_radio_buttons(
                    id=f"switch_player_select_{i[0]}",
                    label=ui.tags.span(ui.tags.b(f"{i[1]}"), style="font-size:14px;"),
                    choices={
                        "in": ui.tags.span("Include", style="font-size:14px;"),
                        "out": ui.tags.span("Exclude", style="font-size:14px;"),
                        "na": ui.tags.span("Any", style="font-size:14px;"),
                    },
                    selected="na",
                )
            )
        return inputs_player

    ui.input_slider(
        id="n_games", label="Number of games to use", min=1, max=100, value=100, step=1
    )

    ui.tags.hr()
    ui.h5("Correlation options")
    ui.input_select(
        id="x_var",
        label="X variable",
        choices=variables_dictionary_numeric,
        selected="Score",
    )

    ui.input_select(
        id="y_var",
        label="Y variable",
        choices=variables_dictionary_numeric,
        selected="PossessionPerc",
    )


with ui.layout_columns():
    with ui.card(full_screen=True):
        ui.card_header("Possession time (%)")

        @render.plot
        def possession_plot():
            plot = boxplot_stat(df=filtered_mh(), stat="PossessionPerc")
            return plot

    with ui.card(full_screen=True):
        ui.card_header("Scores")

        @render.plot
        def score_plot():
            plot = boxplot_stat(df=filtered_mh(), stat="Score")
            return plot


with ui.layout_columns():
    with ui.card(full_screen=True):
        ui.card_header(f"Custom correlation")

        @render_widget
        def interactive_plot():
            plot = scatterplot_interactive(
                df=filtered_mh(), x=input.x_var(), y=input.y_var()
            )
            return plot

    with ui.card(full_screen=True):

        @render.data_frame
        def summary_table():
            df = filtered_mh()
            df_grouped = (
                df.groupby("AccountId")[
                    ["Goals", "Assists", "Saves", "Shots", "Demolishes"]
                ]
                .sum()
                .reset_index()
            )
            df_grouped["AccountId"] = df_grouped["AccountId"].replace(tracked_players)
            df_grouped = df_grouped.rename(columns={"AccountId": "Player"})
            return df_grouped


ui.include_css(app_dir / "styles.css")


@reactive.calc
def filter_mh_game_player():
    # First, filter by game mode
    filt_mh = match_history[match_history["GameMode"] == input.mode()]

    # Filter games by selected players
    players_selection = selected_players_dict()
    must_include_players = [k for k, v in players_selection.items() if v == "in"]
    must_exclude_players = [k for k, v in players_selection.items() if v == "out"]

    # Remove games with excluded players
    games_without_excluded = [
        k
        for k, v in participation_dictionary.items()
        if all(x not in v for x in must_exclude_players)
    ]
    games_with_included = [
        k
        for k, v in participation_dictionary.items()
        if all(x in v for x in must_include_players)
    ]
    games_selected = list(set(games_without_excluded) & set(games_with_included))
    filt_mh = filt_mh[filt_mh["Timestamp"].isin(games_selected)]
    # Keep only entries of players of interest
    filt_mh = filt_mh[filt_mh["AccountId"].isin(tracked_players.keys())]
    return filt_mh


@reactive.calc
def filtered_mh():
    mh = filter_mh_game_player()
    unique_games = list(set(mh.Timestamp))
    games_selected = sorted(unique_games, reverse=True)[0 : input.n_games()]
    mh = mh[mh.Timestamp.isin(games_selected)]
    return mh


@reactive.effect
def _():
    max_n_games = len(list(set(filter_mh_game_player()["Timestamp"])))
    ui.update_slider(id="n_games", max=max_n_games)


@reactive.calc
def selected_players_dict():
    out_dict = tracked_players.copy()
    for k in out_dict.keys():
        out_dict[k] = input[f"switch_player_select_{k}"]()
    return out_dict
