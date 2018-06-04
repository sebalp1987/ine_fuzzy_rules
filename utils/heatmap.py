import pandas as pd
from sklearn.feature_selection import VarianceThreshold
import numpy as np
import matplotlib.pyplot as plot
import seaborn as sns


def correlation_get_column(df: pd.DataFrame, columns: list = [], output_file=False, show_plot=False):
    """
    We get correlations for specific columns selected in 'columns' list.
    :param columns: Columns of the df we want to correlate.
    :param output_file: If we want a csv with the output.
    :param show_plot: If we want a Heat Map.
    :return: df subset correlations.
    """
    import seaborn as sns
    index = []
    for i in columns:
        index_i = df.columns.get_loc(i)
        index.append(index_i)
    corrmat = df.corr().iloc[:, index]
    print(corrmat)

    if output_file:
        corrmat.to_csv('corrmat_subset.csv', sep=';')

    if show_plot:
        f, ax = plot.subplots(figsize=(12, 9))
        sns.heatmap(corrmat, vmax=.8, square=True)
        networks = corrmat.columns.values.tolist()
        for i, network in enumerate(networks):
            if i and network != networks[i - 1]:
                ax.axhline(len(networks) - i, c="w")
                ax.axvline(i, c="w")
        f.tight_layout()
        plot.show()


def correlation_get_all(df: pd.DataFrame, get_all=False, get_specific='FRAUDE', output_file=False, show_plot=False):
    """
    We get correlations for a specific column or the whole dataframe.
    :param get_all: True if we want the whole dataframe correlation.
    :param get_specific: Column of the df we want to correlate.
    :param output_file: If we want a csv with the output.
    :param show_plot: If we want a Heat Map.
    :return: df correlations.
    """
    import seaborn as sns
    if get_all:
        corrmat = df.corr()
    else:
        index_i = df.columns.get_loc(get_specific)
        corrmat = df.corr().iloc[:, index_i]
    print(corrmat)

    if output_file:
        corrmat.to_csv('corrmat_whole.csv', sep=';')

    if show_plot:
        f, ax = plot.subplots(figsize=(12, 9))
        sns.heatmap(corrmat, vmax=.8, square=True)
        networks = corrmat.columns.values.tolist()
        for i, network in enumerate(networks):
            if i and network != networks[i - 1]:
                ax.axhline(len(networks) - i, c="w")
                ax.axvline(i, c="w")
        f.tight_layout()
        plot.show()
