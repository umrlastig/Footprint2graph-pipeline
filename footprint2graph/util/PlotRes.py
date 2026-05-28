# -*- coding: utf-8 -*-


import tracklib as tkl

import csv
import os
import re

import matplotlib.pyplot as plt

import fiona
import geopandas as gpd
import rasterio
from rasterio.plot import show
from shapely.geometry import LineString, MultiLineString
from shapely.geometry import shape as geom_shape




def maPlotRasterTiff(pathres, filename, append):
    with rasterio.open(pathres + filename) as src:
        show(src, ax=append, cmap="Blues")  # Greys


def matPlotRasterShp(pathres, filename, append):
    gdf = gpd.read_file(pathres + filename)
    gdf.plot(ax=append)


def matPlotShapefile(pathres, filename, append):
    chemin = pathres + filename
    shape = fiona.open(chemin)

    for i in range(len(shape)):
        if (i == 2):
            continue
        feature = shape[i]
        geom = geom_shape(feature["geometry"])

        if isinstance(geom, MultiLineString):
            for line in geom.geoms:
                x, y = line.xy
                append.plot(x, y, 'b-', linewidth=0.5)




def plotMM(pathres, append):
    collection = tkl.TrackCollection()
    mmtrackpath = pathres + '/mapmatch/tmm/'
    XR = []
    YR = []
    XG = []
    YG = []
    XB = []
    YB = []
    for mmfilename in os.listdir(mmtrackpath):
        #N;E;time;U;num;track_id;user_id;hmm_inference;mmtype;idedge
        fmt = tkl.TrackFormat({'ext': 'CSV',
                                   'srid': 'ENU',
                                   'id_E': 1,'id_N': 0, 'id_U': 3,'id_T': 2,
                                   'separator': ';',
                                   'header': 0,
                                   'comment': '#',
                                   'read_all': True})
        trace = tkl.TrackReader.readFromFile(mmtrackpath + mmfilename, fmt)
        for j in range(trace.size()):
                obs = trace.getObs(j)
                x = float(obs.position.getX())
                y = float(obs.position.getY())

                s = trace["hmm_inference", j]
                hmminf = list(map(float, re.findall(r"[0-9.]+", s)))
                ds = float(hmminf[4])
                dt = float(hmminf[5])
                edgeid = trace["idedge", j]
    
                if str(trace["mmtype", j]) == "NOT":
                    # pas de MM
                    XR.append(x)
                    YR.append(y)
                if str(trace["mmtype", j]) == "EDGE":
                    XG.append(hmminf[0])
                    YG.append(hmminf[1])
                if str(trace["mmtype", j]) == "SOURCE" or str(trace["mmtype", j]) == "TARGET":
                    XB.append(hmminf[0])
                    YB.append(hmminf[1])

        append.scatter(XG, YG, color='green', s=3, label='Map-matched on edge')
        append.scatter(XR, YR, color='red', s=3, label='Not Map-matched')
        append.scatter(XB, YB, color='cyan', s=3, label='Map-matched on node')

        # Supprime les doublons dans la légende
        handles, labels = append.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        append.legend(by_label.values(), by_label.keys())



def plotSegmentsConstruction(pathres, ax, squelette):
    mmpath = pathres + '/mapmatch/resultmm_PT.csv'

    n = len(squelette.EDGES)
    cmap = plt.cm.get_cmap('tab20', n)
    colors = [cmap(i) for i in range(n)]

    TRACES = {}
    with open(mmpath, 'r', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';', quotechar='|')
        for row in spamreader:
            edgeid   = row[0]
            wkt      = row[2]
            if wkt == 'WKT':
                continue

            if not edgeid in TRACES:
                TRACES[edgeid] = []
            trace = tkl.TrackReader.parseWkt(wkt, 'ENU')
            TRACES[edgeid].append(trace)
    
    for i, edgeid in enumerate(TRACES.keys()):
        color = colors[i]
        for trace in TRACES[edgeid]:
            ax.plot(trace.getX(), trace.getY(), color=color, linestyle='-')
            
    squelette.plot('k-', nodes='ko', size=0.8, append=ax)



def plotAggregation(pathres, ax):
    fusionpath = pathres + '/geometry/fusion/'
    for fusionfilename in os.listdir(fusionpath):
        with open(fusionpath + fusionfilename, 'r') as file:
            line = file.readline()
            line = file.readline()
            wkt = line.split(";")[2].strip()
            if wkt == 'WKT':
                continue
    
            trace = tkl.TrackReader.parseWkt(wkt, 'ENU')
            ax.plot(trace.getX(), trace.getY(), color='red', linestyle='-')


def plotConflation(pathres, append, size=0.8, label=''):
    raccordpath = pathres + '/geometry/raccord/'
    for raccordfilename in os.listdir(raccordpath):
        with open(raccordpath + raccordfilename, 'r') as file:
            line = file.readline()
            line = file.readline()
            wkt = line.split(";")[1].strip()
            if wkt == 'WKT':
                continue
    
            trace = tkl.TrackReader.parseWkt(wkt, 'ENU')
            append.plot(trace.getX(), trace.getY(), color='green', linestyle='-',
                    linewidth=size, label=label)

    # Supprime les doublons dans la légende
    handles, labels = append.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    append.legend(by_label.values(), by_label.keys())



def plotSqueletteTopo(pathres, ax):
    output_file = str(pathres) + 'network/squelette_topology_simplifie_1.csv'
    fmt = tkl.NetworkFormat({
           "pos_edge_id": 0,
           "pos_source": 1,
           "pos_target": 2,
           "pos_wkt": 3,
           "srid": "ENU",
           "separator": ",",
           "header": 1})
    network = tkl.NetworkReader.readFromFile(output_file, fmt, verbose=False)
    network.plot('k-', nodes='ko', size=0.8, append=ax)






