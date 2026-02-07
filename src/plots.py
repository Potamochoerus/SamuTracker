import plotly.express as px
from src.shared import variables_dictionary_all
from scipy.stats import pearsonr
import plotly.graph_objects as go


def boxplot_stat(df, stat):
    """
    Function for boxplots

    :param df: Input data frame
    :param stat: Variable to plot
    """
    bp = px.box(
        df,
        x="FixedName",
        y=stat,
        points="all",
        labels=variables_dictionary_all,
        color="FixedName",
        template="plotly_white",
        custom_data=["FixedName", "Date", "Score", "PossessionPerc", "Timestamp"],
    )
    for trace in bp.data:
        if trace["type"] == "box":
            trace.hoveron = "points"
            trace.marker.size = 6
            trace.marker.opacity = 1
            trace.jitter = 0.5
            trace.pointpos = 0

    bp.update_traces(
        hovertemplate=f"<b>Player:</b> %{{customdata[0]}}<br>"
        f"<b>Date:</b> %{{customdata[1]}}<br>"
        f"<b>Score:</b> %{{customdata[2]}}<br>"
        f"<b>Possession:</b> %{{customdata[3]}}%<br><extra></extra>"
    )
    return go.FigureWidget(bp)


def scatterplot_interactive(df, x, y, trend, scope):
    # Compute correlation coefficient
    r, _ = pearsonr(df[x], df[y])
    corr_text = f"r² = {r*r:.2f}"

    fig = px.scatter(
        df,
        x=x,
        y=y,
        color="FixedName",
        custom_data=["FixedName", "Date", "Score", "PossessionPerc", "Timestamp"],
        labels=variables_dictionary_all,
        template="plotly_white",
        trendline=trend,
        trendline_scope=scope,
    )

    if scope == "overall" and trend == "ols":
        # Add correlation as annotation
        fig.add_annotation(
            x=df[x].max(),
            y=df[y].min(),
            text=corr_text,
            showarrow=False,
            font=dict(size=12, color="#a16300"),
        )

    x_lab = variables_dictionary_all[x]
    y_lab = variables_dictionary_all[y]
    fig.update_traces(
        hovertemplate=f"<b>Player:</b> %{{customdata[0]}}<br>"
        f"<b>Date:</b> %{{customdata[1]}}<br>"
        f"<b>{x_lab}:</b> %{{x}}<br>"
        f"<b>{y_lab}:</b> %{{y}}<extra></extra>"
    )

    return go.FigureWidget(fig)
