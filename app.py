# Import data from shared.py
from src.shared import (
    app_dir,
    match_history,
    tracked_players,
    participation_dictionary,
    variables_dictionary_all,
    numeric_variables
)

# Import plotting functions
from src.plots import boxplot_stat, scatterplot_interactive, winrate_plot

# Import shiny
from shiny import reactive
from shiny.express import input, render, ui
from shinywidgets import render_widget
import numpy as np
import plotly.express as px

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

    ui.input_switch(id="trendline_display", label="Trendline", value=True)

    @render.ui
    def dynamic_trendline_scope():
        input_trendscope = []
        if input.trendline_display():
            input_trendscope = ui.input_switch(
                id="trendline_scope", label="Trendline per player", value=False
            )
        return input_trendscope

    ui.input_select(
        id="x_var",
        label="X variable",
        choices=numeric_variables,
        selected=variables_dictionary_all["core_score"],
    )

    ui.input_select(
        id="y_var",
        label="Y variable",
        choices=numeric_variables,
        selected=variables_dictionary_all["core_goals"],
    )


with ui.layout_columns():
    with ui.card(full_screen=True):
        ui.card_header("Average distance to ball")

        @render_widget
        def possession_plot():
            plot = boxplot_stat(df=filtered_mh(), stat=variables_dictionary_all["positioning_avg_distance_to_ball"])
            for layer in plot.data:
                layer.on_hover(on_point_hover)
            return plot

    with ui.card(full_screen=True):
        ui.card_header("Scores")

        @render_widget
        def score_plot():
            plot = boxplot_stat(df=filtered_mh(), stat=variables_dictionary_all["core_score"])
            for layer in plot.data:
                layer.on_hover(on_point_hover)
            return plot

    with ui.card(full_screen=True):
        ui.card_header("Winrates")

        @render_widget
        def wr_plot():
            plot = winrate_plot(df=filtered_mh())
            for layer in plot.data:
                layer.on_hover(on_point_unhover)
            return plot


with ui.layout_columns():
    with ui.card(full_screen=True):
        ui.card_header(f"Custom correlation")

        @render_widget
        def interactive_plot():
            trend_type = "ols" if input.trendline_display() else None
            trend_scope = "trace" if input.trendline_scope() else "overall"
            plot = scatterplot_interactive(
                df=filtered_mh(),
                x=input.x_var(),
                y=input.y_var(),
                trend=trend_type,
                scope=trend_scope,
            )
            for layer in plot.data:
                layer.on_hover(on_point_hover)
            return plot

    with ui.card(full_screen=True):

        @render.data_frame
        def summary_table():
            df = filtered_mh()
            df_grouped = (
                df.groupby(variables_dictionary_all["id"])
                .agg(
                    Games=(variables_dictionary_all["timestamp"], "size"),
                    Goals=(variables_dictionary_all["core_goals"], "sum"),
                    Assists=(variables_dictionary_all["core_assists"], "sum"),
                    Saves=(variables_dictionary_all["core_saves"], "sum"),
                    Shots=(variables_dictionary_all["core_shots"], "sum"),
                    Demolishes=(variables_dictionary_all["demo_inflicted"], "sum"),
                )
                .reset_index()[
                    [
                        variables_dictionary_all["id"],
                        "Games",
                        "Goals",
                        "Assists",
                        "Saves",
                        "Shots",
                        "Demolishes",
                    ]
                ]
            )
            df_grouped[variables_dictionary_all["id"]] = df_grouped[variables_dictionary_all["id"]].replace(tracked_players)
            df_grouped = df_grouped.rename(columns={variables_dictionary_all["id"]: "Player"})
            return df_grouped

        @render.ui
        def hovered_game():
            hovered_timestamp = hover_reactive.get()
            game_out = match_history[
                (match_history[variables_dictionary_all["timestamp"]].isin([hovered_timestamp]))
            ]
            game_out = game_out[
                [
                    variables_dictionary_all["team"],
                    variables_dictionary_all["player"],
                    variables_dictionary_all["core_score"],
                    variables_dictionary_all["core_goals"],
                    variables_dictionary_all["core_saves"],
                    variables_dictionary_all["core_shots"],
                    variables_dictionary_all["demo_inflicted"],
                ]
            ]
            styled = (
                game_out.style.apply(highlight_scores, axis=1)
                .hide(subset=[variables_dictionary_all["team"]], axis="columns")
                .hide(axis="index")
                .set_table_styles(
                    [
                        {"selector": "", "props": [("border", "2px solid grey")]},
                        {
                            "selector": "tbody td",
                            "props": [("border", "1px solid grey")],
                        },
                        {
                            "selector": "th",
                            "props": [
                                ("border", "1px solid grey"),
                                ("text-align", "left"),
                                ("padding-left", "4px"),
                                ("font-size", "12px"),
                            ],
                        },
                    ]
                )
                .set_properties(
                    **{"text-align": "left", "padding-left": "4px", "font-size": "12px"}
                )
            )
            return ui.HTML(styled.to_html())


ui.include_css(app_dir / "styles.css")


@reactive.calc
def filter_mh_game_player():

    # Select players of interest
    filt_mh = match_history[(match_history[variables_dictionary_all["id"]].isin(tracked_players.keys()))]

    # Add Fixed name
    filt_mh["FixedName"] = filt_mh[variables_dictionary_all["id"]].map(tracked_players)

    # First, filter by game mode
    filt_mh = filt_mh[filt_mh[variables_dictionary_all["gamemode"]] == input.mode()]

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
    filt_mh = filt_mh[filt_mh[variables_dictionary_all["timestamp"]].isin(games_selected)]
    # Keep only entries of players of interest
    filt_mh = filt_mh[filt_mh[variables_dictionary_all["id"]].isin(tracked_players.keys())]
    return filt_mh


@reactive.calc
def filtered_mh():
    mh = filter_mh_game_player()
    unique_games = list(set(mh[variables_dictionary_all["timestamp"]]))
    games_selected = sorted(unique_games, reverse=True)[0 : input.n_games()]
    mh = mh[mh[variables_dictionary_all["timestamp"]].isin(games_selected)]
    return mh


@reactive.effect
def _():
    max_n_games = len(list(set(filter_mh_game_player()[variables_dictionary_all["timestamp"]])))
    ui.update_slider(id="n_games", max=max_n_games)


@reactive.calc
def selected_players_dict():
    out_dict = tracked_players.copy()
    for k in out_dict.keys():
        out_dict[k] = input[f"switch_player_select_{k}"]()
    return out_dict


hover_reactive = reactive.value()


def on_point_hover(trace, points, state):
    if points.point_inds:
        idx = points.point_inds[0]
        hover_reactive.set(trace["customdata"][points.point_inds][0][3])
        with possession_plot.widget.batch_update():
            n_boxes = len(possession_plot.widget.data) - 1
            custom_data = [
                x["customdata"] for x in possession_plot.widget.data[0:n_boxes]
            ]
            hovered_match = np.vstack(
                [x[x[:, 4] == hover_reactive.get()] for x in custom_data]
            )
            possession_plot.widget.data[n_boxes].x = hovered_match[:, 0]
            possession_plot.widget.data[n_boxes].y = hovered_match[:, 3]

        with score_plot.widget.batch_update():
            n_boxes = len(score_plot.widget.data) - 1
            custom_data = [x["customdata"] for x in score_plot.widget.data[0:n_boxes]]
            hovered_match = np.vstack(
                [x[x[:, 4] == hover_reactive.get()] for x in custom_data]
            )
            score_plot.widget.data[n_boxes].x = hovered_match[:, 0]
            score_plot.widget.data[n_boxes].y = hovered_match[:, 2]

        with interactive_plot.widget.batch_update():
            mh = filtered_mh()
            mh = mh[mh[variables_dictionary_all["timestamp"]] == hover_reactive.get()]
            n_boxes = len(interactive_plot.widget.data) - 1
            player_data = [
                x
                for x in interactive_plot.widget.data
                if x["legendgroup"] in mh["FixedName"].tolist()
            ]
            color_map = dict(
                zip(
                    [x["legendgroup"] for x in player_data],
                    [x["marker"]["color"] for x in player_data],
                )
            )
            interactive_plot.widget.data[n_boxes].x = mh[input.x_var()]
            interactive_plot.widget.data[n_boxes].y = mh[input.y_var()]
            interactive_plot.widget.data[n_boxes].marker = dict(
                size=14, color=mh["FixedName"].map(color_map), symbol="star"
            )


def on_point_unhover(trace, points, state):
    hover_reactive.set(None)
    with possession_plot.widget.batch_update():
        n_boxes = len(possession_plot.widget.data) - 1
        possession_plot.widget.data[n_boxes].x = []
        possession_plot.widget.data[n_boxes].y = []

    with score_plot.widget.batch_update():
        n_boxes = len(score_plot.widget.data) - 1
        score_plot.widget.data[n_boxes].x = []
        score_plot.widget.data[n_boxes].y = []

    with interactive_plot.widget.batch_update():
        n_boxes = len(interactive_plot.widget.data) - 1
        interactive_plot.widget.data[n_boxes].x = []
        interactive_plot.widget.data[n_boxes].y = []


def highlight_scores(val):
    team_color = list(val)[0]
    if team_color == "blue":
        return ["background-color: lightskyblue"] * len(val)
    elif team_color == "orange":
        return ["background-color: lightsalmon"] * len(val)
    return [""] * len(val)
