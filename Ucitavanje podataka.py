import openrouteservice
from openrouteservice.directions import directions
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import csv

stations = pd.read_csv('./stanice.csv')
stations_names = stations.loc[:, 'name']
stations_names.values
lat = stations.loc[:, 'lat']
lat = lat.values
long = stations.loc[:, 'long']
long = long.values

# jedan red iz datoteke linije
linija = pd.read_csv('./linije_novo.csv', header=None)
linija -= 2
linija = linija.values
linija = linija.T

client = openrouteservice.Client(key='5b3ce3597851110001cf62483c04d84e40074740b84767a5ea263525')

header = ['stanica1', 'stanica2', 'distance', 'duration']
filename = "linija13.csv"

G = nx.Graph()

with open(filename, 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter=',') 
    csvwriter.writerow(header) 
    for index, value in enumerate(linija):
        station = value[0]
        coords = ((long[station], lat[station]), (long[linija[index + 1]][0], lat[linija[index + 1]][0]))
        routes = directions(client, coords)
        G.add_edge(stations_names[station], stations_names[linija[index + 1][0]], weight=routes["routes"][0]["summary"]["distance"])
        csvwriter.writerow([station, linija[index + 1][0], routes["routes"][0]["summary"]["distance"], routes["routes"][0]["summary"]["duration"]])
        r, c = linija.shape
        if index == (r - 2):
            break


# prikaz linije za provjeru podataka 
labels = nx.get_edge_attributes(G,'weight')
pos=nx.spring_layout(G)
plt.figure()
nx.draw_networkx(G, pos, with_labels=(True))
nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
plt.show()



