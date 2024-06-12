#!/usr/bin/env python3.9
# coding=utf-8
from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import os

# muzete pridat libovolnou zakladni knihovnu ci knihovnu predstavenou na prednaskach
# dalsi knihovny pak na dotaz

""" Ukol 1:
načíst soubor nehod, který byl vytvořen z vašich dat. Neznámé integerové hodnoty byly mapovány na -1.

Úkoly:
- vytvořte sloupec date, který bude ve formátu data (berte v potaz pouze datum, tj sloupec p2a)
- vhodné sloupce zmenšete pomocí kategorických datových typů. Měli byste se dostat po 0.5 GB. Neměňte však na kategorický typ region (špatně by se vám pracovalo s figure-level funkcemi)
- implementujte funkci, která vypíše kompletní (hlubkou) velikost všech sloupců v DataFrame v paměti:
orig_size=X MB
new_size=X MB

Poznámka: zobrazujte na 1 desetinné místo (.1f) a počítejte, že 1 MB = 1e6 B. 
"""


def get_dataframe(filename: str, verbose: bool = False) -> pd.DataFrame:
    """returns dataframe from pickle

    Args:
        filename (str): [description]
        verbose (bool, optional): [description]. Defaults to False.

    Returns:
        pd.DataFrame: [description]
    """
    df = pd.read_pickle(filename)
    if verbose:
        size = df.memory_usage(False, True).sum() / 1000000
        print("orig_size={:.1f} MB".format(size))
    df['date'] = df['p2a'].astype('datetime64')

    colsToConv = ["p36", "weekday(p2a)", "p6", "p7", "p8", "p9",
                  "p10", "p11", "p12", "p15", "p16", "p17", "p18",
                  "p19", "p20", "p21", "p22", "p23", "p24", "p27",
                  "p28", "p35", "p39", "p44", "p45a", "p48a", "p49",
                  "p50a", "p50b", "p51", "p52", "p55a", "p57", "p58",
                  "h", "i", "j", "k", "l", "n", "o", "p", "q", "r", "s", "t", "p5a"]
    df[colsToConv] = df[colsToConv].astype('category')
    if verbose:
        size = df.memory_usage(False, True).sum() / 1000000
        print("new_size={:.1f} MB".format(size))
    return df

# Ukol 2: počty nehod v jednotlivých regionech podle druhu silnic


def plot_roadtype(df: pd.DataFrame, fig_location: str = None,
                  show_figure: bool = False):
    """[vytvori graf poctu nehod podle jednotlivych regionu]

    Args:
        df (pd.DataFrame): 
        fig_location (str, optional): cesta k souboru pro ulozeni. Defaults to None.
        show_figure (bool, optional): pro zobrazeni grafu. Defaults to False.
    """
    df = df.copy() #in case more functions will be run on the same dataframe
    df['p21X'] = pd.Categorical(df['p21'])
    df.set_index('region', inplace=True)
    regions = ['PHA', 'ZLK', 'OLK', 'VYS']
    filtered = df.loc[regions, ['p21', 'p21X']]

    bins = [0, 1, 2, 3, 5, 6, 7]
    titles = ['Dvoupruhová komunikace',
              "Třípruhová komunikace",
              "Čtyřpruhová komunikace",
              "Vícepruhová komunikace",
              "Rychlostní komunikace",
              "Žádná z uvedených"]

    filtered['p21'] = pd.cut(filtered['p21'], bins, right=False, labels=titles)
    filtered = filtered.groupby(['p21', 'region']).agg(
        {'p21X': 'count'}).reset_index()

    sns.set_style("whitegrid")
    ax = sns.catplot(saturation=.5, sharey=False, data=filtered,
                     col='p21', col_wrap=3, y='p21X', x='region', kind="bar")
    ax.set_axis_labels("Kraj", "Počet nehod")
    ax.set_titles("{col_name}")

    if fig_location:
        dir, file = os.path.split(fig_location)
        if dir and not os.path.exists(dir):
            os.makedirs(dir)
        plt.savefig(fig_location)

    if show_figure:
        plt.show()

# Ukol3: zavinění zvěří


def plot_animals(df: pd.DataFrame, fig_location: str = None,
                 show_figure: bool = False):
    """[vytvori graf poctu nehod zavinenych zveri podle mesice a druhu srazky]

    Args:
        df (pd.DataFrame): 
        fig_location (str, optional): cesta k souboru pro ulozeni. Defaults to None.
        show_figure (bool, optional): pro zobrazeni grafu. Defaults to False.
    """
    df = df.copy() #in case more functions will be run on the same dataframe
    regions = ['JHM', 'ZLK', 'STC', 'VYS']

    # prepare data
    df['p10'].replace({1: "řidičem", 2: "řidičem", 3: "jiné", 4: "zvěří",
                      5: "jiné", 6: "jiné", 7: "jiné", 0: "jiné"}, inplace=True)
    df['p10'] = pd.Categorical(df['p10'])

    # filter data
    df.set_index('region', inplace=True)
    # fdf = filtered data frame
    fdf = df.loc[regions, ['p10', 'p58', 'p2a']].reset_index()
    fdf = fdf[fdf['p2a'] < '2021-01-01']

    fdf.set_index('p58', inplace=True)
    fdf = fdf.loc[5].reset_index()

    fdf['month'] = pd.to_datetime(fdf['p2a']).dt.month
    fdf['p10X'] = pd.Categorical(fdf['p10'])

    fdf = fdf.groupby(['region', 'month', 'p10']).agg(
        {'p10X': 'count'}).reset_index()

    # plotting
    sns.set_style("darkgrid")
    g = sns.catplot(data=fdf, col='region', y='p10X', x='month', hue='p10', hue_order=[
                    "zvěří", "řidičem", "jiné"], col_wrap=2, kind='bar', sharey=False)
    g.set_axis_labels("Měsíc", "Počet nehod")
    g._legend.set_title("Zavinění")
    g.set_titles("Kraj: {col_name}",  size=16)

    if fig_location:
        dir, file = os.path.split(fig_location)
        if dir and not os.path.exists(dir):
            os.makedirs(dir)
        plt.savefig(fig_location)

    if show_figure:
        plt.show()


# Ukol 4: Povětrnostní podmínky
def plot_conditions(df: pd.DataFrame, fig_location: str = None,
                    show_figure: bool = False):
    """udela graf nehod podle povetrnostnich podminek

    Args:
        df (pd.DataFrame): 
        fig_location (str, optional): cesta k souboru pro ulozeni. Defaults to None.
        show_figure (bool, optional): pro zobrazeni grafu. Defaults to False.
    """
    df = df.copy() #in case more functions will be run on the same dataframe
    regions = ['JHM', 'ZLK', 'STC', 'VYS']

    df.set_index('region', inplace=True)
    df = df.loc[regions, ['p18', 'p2a', 'p1']]
    df = df[df['p18'] != 0].reset_index()
    df = df[(df['p2a'] < '2021-01-01') & (df['p2a'] > '2016-01-01')]
    df['p2a'] = pd.to_datetime(df['p2a'])

    df['p18'].replace({1: "neztížené", 2: "mlha", 3: "na počátku deště",
                      4: "déšť", 5: "sněžení", 6: "náledí", 7: "nárazový vítr"}, inplace=True)

    df['p18'] = pd.Categorical(df['p18'])

    # pivoting
    table = df.pivot_table(index=['region', 'p2a'],
                           columns='p18', values='p1', aggfunc='count')
    table = table.reset_index().set_index('p2a').groupby(
        ['region']).resample("M").sum().stack()  # reshaping and stacking
    table = table.reset_index()

    # plotting
    sns.set_style("darkgrid")
    g = sns.relplot(x='p2a', data=table, col='region',
                    col_wrap=2, hue='p18', y=0, kind='line')
    g.set_axis_labels("", "Počet nehod")
    g._legend.set_title("Zavinění")
    g.set_titles("Kraj: {col_name}",  size=16)

    if fig_location:
        dir, file = os.path.split(fig_location)
        if dir and not os.path.exists(dir):
            os.makedirs(dir)
        plt.savefig(fig_location)

    if show_figure:
        plt.show()


if __name__ == "__main__":
    df = get_dataframe("accidents.pkl.gz", True)
    plot_roadtype(df, fig_location="01_roadtype.png", show_figure=True)
    plot_animals(df, "02_animals.png", True)
    plot_conditions(df, "03_conditions.png", True)
