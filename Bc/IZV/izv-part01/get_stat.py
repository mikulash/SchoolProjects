#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from matplotlib import colors
import numpy as np
import matplotlib.pyplot as plt
import os, argparse
# povolene jsou pouze zakladni knihovny (os, sys) a knihovny numpy, matplotlib a argparse

from download import DataDownloader

def plot_stat(data_source, fig_location=None, show_figure=False):
    nehody = data_source["p24"] #get data for column p24
    regionNames = data_source.get("region")[:,0]
    accidents = np.array(["žádná úprava", "přerušovaná žlutá","semafor mimo provoz", "dopravní značky", "přenosné dopravní značky", "nevyznačená"])
    abs = np.zeros([6,14], dtype=np.int32)
    rel = np.zeros([6,14], dtype=np.float64)
    #get count of accidents for each type and district
    for cisloKraje, kraj in enumerate(nehody):
        unique, counts = np.unique(kraj, return_counts=True)
        for i in range(len(unique)):
            if unique[i] >= 0:
                kodNehody = int(unique[i])
                abs[kodNehody][cisloKraje] = counts[i]
    #normalize data
    for kodNehody in range(6):
        celkem = np.sum(abs[kodNehody])
        for cisloKraje, val in enumerate(abs[kodNehody]):
            value = val / celkem * 100
            value = value or np.nan
            rel[kodNehody][cisloKraje] = value
        
    fig, axs = plt.subplots(2, figsize=(8, 4))
    #setting up plots and colorbars for them
    #plot1
    cax = axs[0].imshow(abs, norm=colors.LogNorm(), origin='lower', aspect='auto')
    cbar = fig.colorbar(cax, ax=axs[0])
    cbar.ax.set_ylabel("Počet nehod")
    #plot2
    cax2 = axs[1].imshow(rel, cmap="plasma", norm=colors.Normalize(vmin=0), origin='lower', aspect='auto')
    cbar2 = fig.colorbar(cax2, ax=axs[1])
    cbar2.ax.set_ylabel("Podíl nehod pro danou příčinu [%] ", fontsize=6)
    #naming titles
    axs[0].set_title("Absolutně", fontsize=10)
    axs[1].set_title("Relativně vůči přičině", fontsize=10)
    #ticks name are the same for both plots
    for i in range(2):
        axs[i].set_xticks(np.arange(14))
        axs[i].set_yticks(np.arange(6))
        axs[i].set_xticklabels(regionNames)
        axs[i].set_yticklabels(accidents)

    plt.tight_layout()
    #optional: show or save plot
    if fig_location:
        dir, file = os.path.split(fig_location)
        if dir and not os.path.exists(dir):
            os.makedirs(dir)
        plt.savefig(fig_location)

    if show_figure:
        plt.show()
           
if __name__ == '__main__':
    data_source = DataDownloader().get_dict()
    parser = argparse.ArgumentParser()
    parser.add_argument("--fig_location", dest='filename', help="where to store an image if you want to store it")
    parser.add_argument("--show_figure", action='store_true', help="if you want to show graph")
    args = parser.parse_args()

    plot_stat(data_source, fig_location=args.filename, show_figure=args.show_figure)