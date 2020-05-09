import os
import math
#import json
import datetime
import pandas as pd
import numpy as np
import folium
from folium.plugins import MarkerCluster
import argparse

#Ritorna una griglia nxn su mappa, nel rettangolo formato dai punti
#lat/lon in alto a destra e lat/lon in basso a sinistra

def get_geojson_grid(upper_right, lower_left, n=6):
    
    all_boxes = []

    lat_steps = np.linspace(lower_left[0], upper_right[0], n+1)
    lon_steps = np.linspace(lower_left[1], upper_right[1], n+1)

    lat_stride = lat_steps[1] - lat_steps[0]
    lon_stride = lon_steps[1] - lon_steps[0]

    for lat in lat_steps[:-1]:
        for lon in lon_steps[:-1]:
            # Define dimensions of box in grid
            upper_left = [lon, lat + lat_stride]
            upper_right = [lon + lon_stride, lat + lat_stride]
            lower_right = [lon + lon_stride, lat]
            lower_left = [lon, lat]

            # Define json coordinates for polygon
            coordinates = [
                upper_left,
                upper_right,
                lower_right,
                lower_left,
                upper_left
            ]

            geo_json = {"type": "FeatureCollection",
                        "properties":{
                            "lower_left": lower_left,
                            "upper_right": upper_right
                        },
                        "features":[]}

            grid_feature = {
                "type":"Feature",
                "geometry":{
                    "type":"Polygon",
                    "coordinates": [coordinates],
                }
            }

            geo_json["features"].append(grid_feature)

            all_boxes.append(geo_json)

    return all_boxes

#Verifica se un punto x, y si trova in un rettangolo formato 
#dal vertice basso a sinistra(x1, y1) e dal vertice alto a destra(x2, y2)
def FindPoint(x1, y1, x2, y2, x, y): 
    if (x >= x1 and x <= x2 and 
        y >= y1 and y <= y2): 
        return True
    else: 
        return False

#Trasforma la data in formato datetime lasciando solo giorno, mese e anno
def deleteTime(stringa):
    data=""
    for letter in stringa:
        if letter == "T":
            break
        else:
            data += letter
    #elimino il 29-2 degli anni bisestili che da fastidio al formato datetime
    if data[len(data)-1] == "9" and data[len(data)-2] == "2" and data[len(data)-4] == "2":
        if data[len(data)-5] != "1":
            data = data[0]+data[1]+data[2]+data[3]+"-02-28"
    output = datetime.datetime.strptime(data, "%Y-%m-%d")
    return output