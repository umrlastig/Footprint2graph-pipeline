# -*- coding: utf-8 -*-

'''
      TOPOLOGIE DU SQUELETTE
'''


import fiona
from shapely.geometry import shape
import progressbar
import time

import tracklib as tkl

from ofnp import skeleton_smoothing


def addTopologyToNetwork(RESPATH, DIST_MIN_ARC, prefix='PT'):

    t0 = time.time()

    # Pour la construction du réseau
    tolerance     = 0.1    # 0.05
    seuil_doublon = 0.1

    print("Starting topology creation for the network")



    # =========================================================================
    #          CHARGEMENT DU SQUELETTE

    collection = tkl.TrackCollection()

    squelettepath = str(RESPATH) + 'network/squelette_' + str(prefix) + '.shp'
    with fiona.open(squelettepath, 'r') as shapefile:
        for feature in shapefile:
            # 1 MultiLineString
            geom = shape(feature['geometry'])
            if geom.geom_type == "MultiLineString":
                for line in geom.geoms:
                    track = tkl.TrackReader().parseWkt(line.wkt)
                    if track.length() < tolerance/2:
                        continue
                    collection.addTrack(track)
            if geom.geom_type == "LineString":
                print ('ohoh')

    input_file = str(RESPATH) + 'network/edgegeom.csv'
    with open(input_file, "w") as f:
        for track in collection:
            f.write(track.toWKT() + "\n")


    print ('    Number of edges in the smoothed skeleton:', collection.size())
    print ('    Finished loaded skeleton.')



    # =============================================================================
    #             CONSTRUCTION RESEAU
    #
    # tkl.NetworkReader.counter = 1
    # network = createNetwork(collection, tolerance)

    print ('Starting topology creation ...')

    output_file = str(RESPATH) + 'network/squelette_topology_' + str(prefix) + '.csv'
    tkl.Topology.create_topology(input_file, '2154', output_file)

    fmt = tkl.NetworkFormat({
           "pos_edge_id": 0,
           "pos_source": 1,
           "pos_target": 2,
           "pos_wkt": 3,
           "srid": "ENU",
           "separator": ",",
           "header": 1})
    network = tkl.NetworkReader.readFromFile(output_file, fmt, verbose=False)

    t1 = time.time()
    total = t1-t0
    print ("    Execution time (seconds):", total)
    print ('    Finished created topology.')
    t0 = t1





    # =============================================================================
    #          SUPPRIME LES parties crochues du squelette
    #

    network.simplify(0, tkl.MODE_SIMPLIFY_REM_POS_DUP, verbose=False)
    print ('Finished removing hooked parts of the skeleton.')


    for idx in progressbar.progressbar(network.getEdgesId()):
        network.getEdge(idx).geom = skeleton_smoothing(
            network.getEdge(idx).geom, 1, 5)


    network.simplify(5, tkl.MODE_SIMPLIFY_DOUGLAS_PEUCKER, verbose=False)
    print ('Finished simplification of the skeleton.')










    # =========================================================================
    # Sauvegarde dans un fichier
    netwokpath = RESPATH + 'network/reseau_' + prefix + '.csv'
    tkl.NetworkWriter.writeToCsv(network, netwokpath)

    print ("Stage 3 completed: adding topology to the skeleton.")


    
