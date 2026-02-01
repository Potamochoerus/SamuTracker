import seaborn as sns
import matplotlib as mpl
import plotly.express as px
from src.shared import variables_dictionary_all

def boxplot_stat(df, stat):
    """
    Function for boxplots
    
    :param df: Input data frame
    :param stat: Variable to plot
    """
    bp = sns.boxplot(
        data=df,
        x="FixedName",
        y=stat,
        hue="FixedName",
        showfliers=False
    )
    for patch in bp.artists:
        fc = patch.get_facecolor()
        patch.set_facecolor(mpl.colors.to_rgba(fc, 0.3))
    bp = sns.stripplot(
        data=df,
        x="FixedName",
        y=stat,
        hue="FixedName",
        dodge=False,
        jitter=True,
        alpha=1,
        palette='dark:black',
        ax=bp
    )
    bp.set_xlabel("")
    bp.set_ylabel("")
    
    return bp

def scatterplot_interactive(df, x, y):
    fig = px.scatter(
        df,
        x=x,
        y=y,
        color="FixedName",
        custom_data=["FixedName", "Date"],
        labels=variables_dictionary_all,
        template="plotly_white"
    )
    fig.update_traces(
        hovertemplate=
        f"<b>Player:</b> %{{customdata[0]}}<br>"
        f"<b>Date:</b> %{{customdata[1]}}<br>"
        f"<b>{x}:</b> %{{x}}<br>"
        f"<b>{y}:</b> %{{y}}<extra></extra>"
    )

    return fig