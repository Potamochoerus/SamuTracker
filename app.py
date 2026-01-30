# Import general lib
import seaborn as sns
from faicons import icon_svg
import numpy as np

# Import data from shared.py
from shared import app_dir, match_history, threshold_score

# Import shiny
from shiny import reactive
from shiny.express import input, render, ui

ui.page_opts(title="SamuTracker", fillable=True)

with ui.sidebar(title="Filter games"):
    ui.input_slider("n_games", "Number of games to use", 1, min(100, match_history.shape[0]), min(100, match_history.shape[0]))
    ui.input_checkbox_group(
        "players",
        "Players",
        ["Jayke Stew", "Pongo Abeii", "Palaindrome"],
        selected=["Jayke Stew", "Pongo Abeii", "Palaindrome"],
    )


with ui.layout_columns():
    with ui.card(full_screen=True):
        ui.card_header("Mean score")

        @render.plot
        def barplot_mean():
            return sns.barplot(
                data=filtered_mh_longer(),
                x="players",
                y="score",
                hue="players",
                errorbar=None
            )

    with ui.card(full_screen=True):
        ui.card_header("Median score")

        @render.plot
        def barplot_median():
            return sns.barplot(
                data=filtered_mh_longer(),
                x="players",
                y="score",
                hue="players",
                estimator=np.median,
                errorbar=None
            )


with ui.layout_columns():
    with ui.card(full_screen=True):
        ui.card_header(f"Less than {threshold_score} points")

        @render.plot
        def n_below_barplot():
            df = filtered_mh_longer()
            df["below_threshold"] = df["score"] < threshold_score

            # Count per player
            count_df = df.groupby("players")["below_threshold"].sum().reset_index()
            count_df.rename(columns={"below_threshold": f"count_below_{threshold_score}"}, inplace=True)

            return sns.barplot(
                x="players",
                y=f"count_below_{threshold_score}",
                data=count_df,
                hue="players",
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
def filtered_mh():
    player_list = list(input.players())
    player_list.append("game_id")
    filt_mh = match_history[player_list]
    filt_mh = filt_mh.head(input.n_games())
    return filt_mh

@reactive.calc
def filtered_mh_longer():
    df = filtered_mh()
    df_long = df.melt(
        id_vars=["game_id"],
        value_vars=list(input.players()),
        var_name="players",
        value_name="score"
    )
    return df_long

