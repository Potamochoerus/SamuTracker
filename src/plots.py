import seaborn as sns
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
    bp = sns.stripplot(
        data=df,
        x="FixedName",
        y=stat,
        hue="FixedName",
        dodge=False,
        jitter=True,
        alpha=0.6,
        ax=bp
    )
    bp.set_xlabel("")
    
    return bp