# -*- coding: utf-8 -*-

'''
    Recalage des points sur le réseau
    Fusion des traces
'''

import sys
import csv
csv.field_size_limit(sys.maxsize)
import time

import tracklib as tkl
from ofnp import (conflateOnNetwork,
                  getcandidates)



def createNetworkGeom (RESPATH, SEARCH, BUFFER,
                       prefix='PT',
                       pathtraces='resample_fusion',
                       pathtmm='tmm',
                       pathfusion='fusion',
                       pathraccord='raccord'):

    t0 = time.time()
    print("Starting map-matching, aggregation, and conflation of GNSS trajectories.")


    # =========================================================================
    #    Lecture du réseau
    #
    print ('Loading network ...')
    fmt = tkl.NetworkFormat({
           "pos_edge_id": 0,
           "pos_source": 1,
           "pos_target": 2,
           "pos_wkt": 4,
           "srid": "ENU",
           "separator": ",",
           "header": 1})
    
    networkpath = RESPATH + 'network/reseau_' + prefix + '.csv'
    network = tkl.NetworkReader.readFromFile(networkpath, fmt, verbose=False)
    
    print ('    Number of edges = ', len(network.EDGES))
    print ('    Number of nodes = ', len(network.NODES))
    print ('    Total segment length of the network = ', network.totalLength())

    
    # =========================================================================
    #   Lecture des traces découpées et ré-échantillonnées.
    #
    print ('Loading collection of tracks ...')
    fmt = tkl.TrackFormat({'ext': 'CSV',
                           'srid': 'ENU',
                           'id_E': 1,'id_N': 0, 'id_U': 3,'id_T': 2,
                           'time_fmt': '2D/2M/4Y 2h:2m:2s',
                           'separator': ';',
                           'header': 0,
                           'cmt': '#',
                           'read_all': True})
    tracespath = RESPATH + '/' + pathtraces + '/'
    collection2 = tkl.TrackReader.readFromFile(tracespath, fmt)
    print ('    Number of tracks:', collection2.size())


    # =========================================================================

    collection = tkl.TrackCollection()
    for trace in collection2:
        num = trace.getObsAnalyticalFeature('num', 0)
        track_id = trace.getObsAnalyticalFeature('track_id', 0)
        user_id = trace.getObsAnalyticalFeature('user_id', 0)
        version = trace.getObsAnalyticalFeature('version', 0)

        trace.uid = user_id
        trace.tid = str(num) + '-' + version
        #if str(trace.tid) == '6732043.0-v1' or str(trace.tid) == '6732043.0-v1':
        collection.addTrack(trace)
    

    t1 = time.time()
    total = t1-t0
    print ("    Execution time (seconds):", total)
    t0 = t1


    # =========================================================================
    #     Map-matching
    #
    print ('Starting map-matching ...')

    si = tkl.SpatialIndex(network, verbose=False)
    network.spatial_index = si

    # Computes all distances between pairs of nodes
    network.prepare()

    # Map track on network
    tkl.mapOnNetwork(collection, network, search_radius=SEARCH, debug=False)
    print ('    Map-matching ended.')


    t1 = time.time()
    total = t1-t0
    print ("    Execution time (seconds):", total)
    t0 = t1


    # =========================================================================
    #  Résultats Map-matching
    #

    getcandidates(network, collection, SEARCH, BUFFER,
                           RESPATH, pathtmm, prefix)
    t1 = time.time()
    total = t1-t0
    print ("    Execution time (seconds):", total)
    t0 = t1


    # =========================================================================
    #     Fusion
    #

    print ("Starting aggregation ...")

    geompath = RESPATH + 'geometry/' + pathfusion + '/'
    
    # Aggregation with DTW distance
    fusions = tkl.TrackCollection()
    edgeprevious = -1
    TRACES = []
    mmpath = RESPATH + 'mapmatch/resultmm_' + prefix + '.csv'
    with open(mmpath, 'r') as file:
        cpt = 0
        for s in file:

            if cpt == 0:
                cpt += 1
                continue

            line = s.split(";")
            if len(line) < 1:
                continue
        
            edgeid = line[0]
            e = network.EDGES[edgeid]

            if edgeprevious != edgeid:

                if e.geom.length() <= SEARCH:
                    print ("    No merge for arc number (length too small):", edgeprevious)
                    central = e.geom.copy()
                    central.createAnalyticalFeature('edgeid', edgeprevious)
                    central.tid = edgeprevious
                    fusions.addTrack(central)

                    # sauvegarde
                    chemin = geompath + str(edgeprevious) + ".csv"
                    f = open(chemin, 'w')
                    f.write("EDGE_ID;TRACKS_SIZE;WKT\n")
                    f.write(str(edgeprevious) + ";" + str(len(TRACES)) + ";" + central.toWKT() + "\n")
                    f.close()

                elif edgeprevious != -1 and len(TRACES) > 1:
                    print ("    Aggregation for arc number:", edgeprevious)
                    central = _fusion(e, TRACES, SEARCH)
                    if central is not None:
                        central.createAnalyticalFeature('edgeid', edgeprevious)
                        central.tid = edgeprevious
                        fusions.addTrack(central)

                        # sauvegarde
                        chemin = geompath + str(edgeprevious) + ".csv"
                        f = open(chemin, 'w')
                        f.write("EDGE_ID;TRACKS_SIZE;WKT\n")
                        f.write(str(edgeprevious) + ";" + str(len(TRACES)) + ";" + central.toWKT() + "\n")
                        f.close()

                # if len(TRACES) > 1:
                TRACES = []
                # break

                # print ('Edge ', edgeid)

            trackid = line[1]
            wkt = line[2]

            track = tkl.TrackReader.parseWkt(wkt)
            if track.size() > 3:
                TRACES.append(track)

            edgeprevious = edgeid


    # dernière trace
    if len(TRACES) > 1:

        if e.geom.length() <= SEARCH:
            print ("    No merge for arc number (length too small):", edgeprevious)
            central = e.geom.copy()
            central.createAnalyticalFeature('edgeid', edgeprevious)
            central.tid = edgeprevious
            fusions.addTrack(central)

            # sauvegarde
            chemin = geompath + str(edgeprevious) + ".csv"
            f = open(chemin, 'w')
            f.write("EDGE_ID;TRACKS_SIZE;WKT\n")
            f.write(str(edgeprevious) + ";" + str(len(TRACES)) + ";" + central.toWKT() + "\n")
            f.close()

        else:
            print ("    Aggregation for arc number:", edgeprevious)
            central = _fusion(e, TRACES, SEARCH)
            if central is not None:
                central.createAnalyticalFeature('edgeid', edgeprevious)
                central.tid = edgeprevious
                fusions.addTrack(central)
        
                # sauvegarde
                chemin = geompath + str(edgeprevious) + ".csv"
                f = open(chemin, 'w')
                f.write("EDGE_ID;TRACKS_SIZE;WKT\n")
                f.write(str(edgeprevious) + ";" + str(len(TRACES)) + ";" + central.toWKT() + "\n")
                f.close()


    print ('    Number of aggregations:', fusions.size())
    print ("    Aggregation process finished.")

    t1 = time.time()
    total = t1-t0
    print ("    Execution time (seconds):", total)
    t0 = t1


    # =========================================================================
    # Raccord

    print ("Starting conflation ...")

    conflated = conflateOnNetwork(fusions, network, threshold=50, h=30,
                                  verbose=False)

    # enregistrer conflation
    raccordpath = RESPATH + 'geometry/' + pathraccord + '/'
    for segment in conflated:
        if segment is not None:
            # Sauvegarde
            chemin = raccordpath + str(segment.tid) + ".csv"
            f = open(chemin, 'w')
            f.write("EDGE_ID;WKT\n")
            f.write(str(segment.tid) + ";" + segment.toWKT() + "\n")
            f.close()

    print ("    Conflation process finished.")

    t1 = time.time()
    total = t1-t0
    print ("    Execution time (seconds):", total)
    t0 = t1


    # =========================================================================
    # Fin

    print ("Stage 4 completed: map-matching, aggregation, and conflation.")

    


def _fusion (e, TRACES, SEARCH):
    '''

    '''

    rec = 10
    cv  = 1e-3

    if len(TRACES) <= 0:
        return None

    candidats = tkl.TrackCollection()
    for track in TRACES:
        t = tkl.simplify(track, tolerance=0.5,
                         mode=tkl.MODE_SIMPLIFY_DOUGLAS_PEUCKER,
                         verbose=False)
        candidats.addTrack(t)


    NB = candidats.size()
    # print ('        Number of traces to merge (before sampling):', NB)
    if NB > 30:
        collection = candidats.randNTracks(min(NB, 30))
    else:
        collection = candidats


    # print ('        Number of candidates in the aggregation process:', collection.size())
    print ('        Number of candidate tracks / number of sampled tracks',
           NB, "/", collection.size())

    if collection.size() > 1:
        # print ('        Launching Aggregation ...')
        centralDTW = tkl.fusion(collection,
                             master=tkl.MODE_MASTER_MEDIAN_LEN,
                             dim=2,
                             mode=tkl.MODE_MATCHING_FDTW,
                             p=2,
                             represent_method=tkl.MODE_REP_BARYCENTRE,
                             agg_method=tkl.MODE_AGG_MEDIAN,
                             constraint=False,
                             verbose=False,
                             iter_max=25,
                             recursive=rec,
                             cv=cv)
        # print ('        Aggregation ended.')
        return centralDTW
    elif candidats.size() == 1:
        centralDTW = candidats.getTrack(0)
        return centralDTW

    return None






