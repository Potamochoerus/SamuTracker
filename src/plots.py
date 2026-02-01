import seaborn as sns
import matplotlib as mpl
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