# Import general lib
import seaborn as sns
from faicons import icon_svg
import numpy as np

# Import data from shared.py
from shared import app_dir, match_history, threshold_score, tracked_players, total_games, participation_dictionary

# Import shiny
from shiny import reactive
from shiny.express import input, render, ui

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


with ui.layout_columns():
    with ui.card(full_screen=True):
        ui.card_header("Mean score")

        @render.plot
        def barplot_mean():
            bp = sns.barplot(
                data=filtered_mh(),
                x="FixedName",
                y="Score",
                hue="FixedName",
                errorbar=None
            )
            for p in bp.patches:
                height = p.get_height()  # height of the bar
                bp.text(
                    x=p.get_x() + p.get_width() / 2,  # center of bar
                    y=height + 0.3,                    # slightly above bar
                    s=f"{int(height)}",                # text to display
                    ha='center'                        # horizontal alignment
                )
            return bp

    with ui.card(full_screen=True):
        ui.card_header("Median score")

        @render.plot
        def barplot_median():
            bp = sns.barplot(
                data=filtered_mh(),
                x="FixedName",
                y="Score",
                hue="FixedName",
                estimator=np.median,
                errorbar=None
            )
            for p in bp.patches:
                height = p.get_height()  # height of the bar
                bp.text(
                    x=p.get_x() + p.get_width() / 2,  # center of bar
                    y=height + 0.3,                    # slightly above bar
                    s=f"{int(height)}",                # text to display
                    ha='center'                        # horizontal alignment
                )
            return bp


with ui.layout_columns():
    with ui.card(full_screen=True):
        ui.card_header(f"Less than {threshold_score} points")

        @render.plot
        def n_below_barplot():
            df = filtered_mh()
            df["below_threshold"] = df["Score"] < threshold_score

            # Count per player
            count_df = df.groupby("FixedName")["below_threshold"].sum().reset_index()
            count_df.rename(columns={"below_threshold": f"count_below_{threshold_score}"}, inplace=True)

            return sns.barplot(
                x="FixedName",
                y=f"count_below_{threshold_score}",
                data=count_df,
                hue="FixedName",
                palette="pastel"
            )

    with ui.card(full_screen=True):
        with ui.value_box(showcase=icon_svg("cow")):
            "Games played"

            @render.text
            def count_games():
                return input.n_games()

        with ui.value_box(showcase=icon_svg("dog")):
            "Games played again"

            @render.text
            def count_games_b():
                return input.n_games()
        
        with ui.value_box(showcase=icon_svg("cat")):
            "Games played to check ui"

            @render.text
            def count_games_c():
                return input.n_games()

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