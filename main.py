# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 16:27:42 2023

@author: ivana
"""

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib as mpl
import os
import numpy as np
import random as rnd
import matplotlib.patches as mpatches

# imena svih datoteka u kojima su linije
arr = os.listdir('./podaci')

# ime, lat, long
stations = pd.read_csv('./stanice.csv')
stations_names = stations.loc[:, 'name']
stations_names.values

G = nx.Graph()

# kreiranje grafova i podgrafova (linije)
subgraphs = []
names_linije = []
for file in arr:
    data = pd.read_csv('./podaci/' + file)
    names_linije.append(file[6:len(file)-4])
    linija = []
    for i in range(len(data)):
        G.add_edge(stations_names[data.loc[i, 'stanica1']], stations_names[data.loc[i, 'stanica2']], weight=data.loc[i, 'duration'])
        linija.append((stations_names[data.loc[i, 'stanica1']], stations_names[data.loc[i, 'stanica2']]))
    subgraphs.append(G.edge_subgraph(linija))
 
lat = stations.loc[:, 'lat']
lat = lat.values
long = stations.loc[:, 'long']
long = long.values

coords =  np.column_stack((lat, long))

# pozicije pomoću kojih su čvorovi grafa raspoređeni kao u stvarnosti
positions = dict(zip(stations_names, np.column_stack((long, lat))))
    
# prva vizualizacija
labels = nx.get_edge_attributes(G,'weight')
pos=nx.spring_layout(G)
plt.figure()
plt.title('Grafički prikaz linija Autotroleja')
nx.draw(G, positions, node_size=30, node_color="skyblue", font_size=10, with_labels=(True))
# prikaz težina bridova na grafu
#nx.draw_networkx_edge_labels(G, positions, edge_labels=labels)

legend_elements = []
for i in range(len(subgraphs)):
    color = (rnd.random(),rnd.random(),rnd.random())
    nx.draw(subgraphs[i], positions, edge_color=[color], node_color=[color], node_size=30)
    legend_elements.append(mpatches.Patch(color=color, label=names_linije[i]))
plt.legend(handles=legend_elements)
plt.tight_layout()
plt.show()

# računanje vremena od svake stanice do svih drugih
paths = dict(nx.shortest_path_length(G, weight='weight'))

df = pd.DataFrame(columns=['station', 'total_dist', 'color'])
index = 0

# izračun kvalitete, što je broj veći -> kvaliteta je manja (više vremena)
for first in paths:
    suma = 0
    for second in paths[first]:
        suma += paths[first][second]
        
    df.loc[index, 'station'] = first
    df.loc[index, 'total_dist'] = suma
    index += 1

# Colorbar
dist = df['total_dist']
dist = dist.astype(float)
dist_norm = (dist-np.min(dist))/(np.max(dist)-np.min(dist))
min_val, max_val = min(dist_norm), max(dist_norm)

# Kreirati mapu boja
cmap = mpl.cm.RdYlGn.reversed()
norm = mpl.colors.Normalize(vmin=min_val, vmax=max_val)

color_list = cmap(dist_norm)
for i, color in enumerate(color_list):
    df.loc[i, 'color'] = color

# druga vizualizacija
plt.figure()
plt.title('Vizualizacija kvalitete povezanosti stanica')
nx.draw(G, positions, node_size=500, node_color=df.loc[:, 'color'], font_size=10, with_labels=(True))
sm = plt.cm.ScalarMappable(cmap=cmap.reversed(), norm=plt.Normalize(vmin=min_val, vmax=max_val))
sm.set_array([])
cbar = plt.colorbar(sm, ticks=[0, 1], shrink=0.75)
cbar.ax.set_yticklabels(['Niska', 'Visoka'])
plt.tight_layout()
plt.show()

