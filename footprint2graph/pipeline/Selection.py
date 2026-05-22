# -*- coding: utf-8 -*-

import math
import os
import sys
import csv
csv.field_size_limit(sys.maxsize)

import tracklib as tkl




def load_raw_tracks_split(RESPATH, tracespathsource, fmt, X, Y):
    '''
    Dédié aux traces de Outdoorvision :
        les attributs sont stockés dans le fichier .csv
    '''

    print ('Loading and split track data...')


    """ ======================================================================= """
    """         Reading                                                         """
    """                                                                         """
    print ('Reading track data...')

    poly = tkl.Polygon(X, Y)
    constraintBBox = tkl.Constraint(shape=poly,
                                    mode=tkl.MODE_CROSSES,
                                    type=tkl.TYPE_CUT_AND_SELECT)


    tracks = tkl.TrackSource(tracespathsource, fmt)
    total = len(tracks)
    print ('     Number files to load: ', total)


    """ ======================================================================= """
    """         Découpage                                                       """
    """                                                                         """
    print ('Starting split ...')

    metacollectionpath = RESPATH + 'metadata_collection.csv'
    f1 = open(metacollectionpath,'w')
    f1.write("ID;NUM;TRACK_ID;USER_ID\n")

    cpt = 1
    cutCollection = tkl.TrackCollection()

    for track in tracks:
        if cpt%500 == 0:
            print ('    ', cpt, '/', total)

        ID = 'OV_' + str(cpt)
        cpt += 1

        num = str(int(track.getObsAnalyticalFeature('num', 0)))
        uid = str(int(track.getObsAnalyticalFeature('user_id', 0)))
        tid = str(int(track.getObsAnalyticalFeature('track_id', 0)))
        f1.write(ID + ";" + str(num) + ";" + str(tid) + ";" + str(uid) + "\n")

        selection = constraintBBox.select(tkl.TrackCollection([track]))
        if len(selection) <= 0:
            continue

        newtrack = tkl.Track()
        newtrack.tid = ID
        newtrack.uid = ID
        for o in selection.getTrack(0):
            newtrack.addObs(tkl.Obs(tkl.ENUCoords(o.position.getX(), o.position.getY()),
                                    tkl.ObsTime()))
        newtrack.createAnalyticalFeature('TID', str(ID))
        cutCollection.addTrack(newtrack)

    f1.close()


    print ('     Number of tracks after split: ' + str(cutCollection.size()))

    return cutCollection




def segmentation_resample(RESPATH, collection, fmt,
                          NB_OBS_MIN = 10, DIST_MAX_2OBS = 50,
                    resampleSizeGrid = 1, resampleSizeFusion = 5):

    print ("Starting segmentation and resampling...")

    RESAMPLE_SIZE_GRID   = resampleSizeGrid
    RESAMPLE_SIZE_FUSION = resampleSizeFusion

    total = len(collection)


    """ =================================================================== """
    """         Segmentation                                                """
    """                                                                     """
    print ('Starting segmentation ...')

    cpt = 1
    cutCollection = tkl.TrackCollection()

    for track in collection:
        if cpt%500 == 0:
            print ('    ', cpt, '/', total)
        cpt += 1

        num = str(track.getObsAnalyticalFeature('TID', 0))

        idxSelect = 1
        o1 = None
        newtrack = tkl.Track()
        newtrack.uid = num
        newtrack.tid = num
        for o2 in track:
            if o1 is not None:
                if o1.distance2DTo(o2) > DIST_MAX_2OBS:
                    # on coupe la trace pour créer un nouveau morceau
                    if newtrack.size() >= NB_OBS_MIN:
                        tid = num + "-s" + str(idxSelect)
                        newtrack.createAnalyticalFeature('TID', num)
                        newtrack.createAnalyticalFeature('MID', tid)
                        cutCollection.addTrack(newtrack)
                        idxSelect += 1
                    newtrack = tkl.Track()
                    newtrack.uid = num
                    newtrack.tid = num
            newtrack.addObs(tkl.Obs(tkl.ENUCoords(o2.position.getX(), o2.position.getY()), o2.timestamp.copy()))
            o1 = o2
    
        # Last track segment
        if newtrack.size() >= NB_OBS_MIN:
            tid = num + "-s" + str(idxSelect)
            newtrack.createAnalyticalFeature('TID', num)
            newtrack.createAnalyticalFeature('MID', tid)
            cutCollection.addTrack(newtrack)

    print ('    Number of tracks after segmentation: ' + str(cutCollection.size()))


    """ ======================================================================= """
    """         Saving                                                          """
    """                                                                         """

    af_names = ['TID', 'MID']
    tracespath = RESPATH + "decoup/"

    tkl.TrackWriter.writeToFiles(cutCollection, tracespath,
                                 id_E=1, id_N=0, id_U=3, id_T=2,
                                 h=1, separator=";", af_names=af_names)

    print ("Finished saving segmented tracks.")


    # =========================================================================
    #

    



    # =========================================================================
    #         Resampling spatial
    #

    print ('Starting resampling ...')

    collectionGrid = tkl.TrackCollection()
    collectionFusion = tkl.TrackCollection()

    tracks = tkl.TrackSource(tracespath, fmt)
    total = len(tracks)
    print ('    Number of tracks to resample: ', total)


    for track in tracks:
        num1 = str(track.getObsAnalyticalFeature('TID', 0))
        num2 = str(track.getObsAnalyticalFeature('MID', 0))

        if cpt%100 == 0:
            print ('   ', cpt, '/', total)


        trackG = track.copy()
        trackG.resample(RESAMPLE_SIZE_GRID, mode=tkl.MODE_SPATIAL)
        trackG.uid = num1
        trackG.tid = num1
        trackG.createAnalyticalFeature('TID', num1)
        trackG.createAnalyticalFeature('MID', num2)
        collectionGrid.addTrack(trackG)

        trackF = track.copy()
        trackF.resample(RESAMPLE_SIZE_FUSION, mode=tkl.MODE_SPATIAL)
        trackF.uid = num1
        trackF.tid = num1
        trackF.createAnalyticalFeature('TID', num1)
        trackF.createAnalyticalFeature('MID', num2)
        collectionFusion.addTrack(trackF)


    print ('    Number of tracks after resampling:', str(collectionGrid.size()))
    print ('    Number of tracks after resampling:', str(collectionFusion.size()))




    # =========================================================================
    #        Enregistrement
    #

    af_names = ['TID', 'MID']
    
    resampledtracespath = RESPATH + 'resample_grid/'
    tkl.TrackWriter.writeToFiles(collectionGrid, resampledtracespath,
                                 id_E=1, id_N=0, id_U=3, id_T=2,
                                 h=1, separator=";", af_names=af_names)

    resampledtracespath = RESPATH + 'resample_fusion/'
    tkl.TrackWriter.writeToFiles(collectionFusion, resampledtracespath,
                                 id_E=1, id_N=0, id_U=3, id_T=2,
                                 h=1, separator=";", af_names=af_names)

    print ("Finished saving resampled tracks.")




    # =========================================================================
    print ("Stage 1 finished: segmentation and resampling.")







def second_round(RESPATH, NB_OBS_MIN = 10, DIST_MAX_2OBS = 50, RESAMPLE_SIZE_GRID = 1,
                 rep='points_not_mm_1', pathtmm='tmm'):
    '''
    
    Doit créer un nouveau jeu de traces à partir des points non matchés.
    
    - Quand c'est fait, ils sont enregistrés dans la destination : rep
    - Les résultats du MM sont dans la source pathtmm
    - Un post-traitement : resample 

    '''

    #buffer_size = 5
    #k = 0.6

    OPT_PLUS_PTS = True
    NB_PTS = 5


    # =========================================================================
    #   Lecture des traces découpées et ré-échantillonnées.
    #

    collection = tkl.TrackCollection()
    mmtrackpath = RESPATH + '/mapmatch/' + pathtmm + '/'
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
        collection.addTrack(trace)
    print ('Number of tracks map matched :', collection.size())






    # =========================================================================

    morceaux = tkl.TrackCollection()

    for i in range(collection.size()):
        track = collection.getTrack(i)
        tid = track.getObsAnalyticalFeature('TID', 0)
        mid = track.getObsAnalyticalFeature('MID', 0)
        #track.tid = mid
        #track.uid= tid

        nummorceau = 1
        #morceau = tkl.Track()

        PRIS = []
        POINTS = []
        for j in range(track.size()):
            obs = track.getObs(j)

            if str(track["mmtype", j]) == "NOT":
                PRIS.append(j)
                POINTS.append((j, tkl.Obs(tkl.ENUCoords(obs.position.getX(), obs.position.getY()),
                                        tkl.ObsTime())))
                #morceau.addObs(tkl.Obs(tkl.ENUCoords(obs.position.getX(), obs.position.getY()),
                #                        tkl.ObsTime()))
                #pos = morceau.size() - 1

                # On modifie un petit peu la position
                # POINTS = index.neighborhood(obs.position, None, buffer_size)
                # TODO : il faudrait trouver le barycentre et faire le kième de la distance encore
                # print (len(POINTS))

                # je prends les 4 points précédents s'ils sont recalés sinon j'arrête
                # (il est déjà pris)
                o1 = obs
                for k in range(j-1, j-NB_PTS-1, -1):
                    o2 = track[k]
                    if o1.distance2DTo(o2) <= DIST_MAX_2OBS:
                        if str(track["mmtype", k]) != "NOT":
                            PRIS.append(k)
                            # morceau.addObs(o2)
                            #morceau.insertObs(tkl.Obs(tkl.ENUCoords(o2.position.getX(), o2.position.getY()),
                            #                        tkl.ObsTime()), pos-1)
                            #pos = pos - 1
                            POINTS.append((k,tkl.Obs(tkl.ENUCoords(o2.position.getX(), o2.position.getY()),
                                                    tkl.ObsTime())))
                        else:
                            break
                    o1 = o2


                # je prends les 4 points suivants s'ils sont recalés sinon j'arrête
                # (il est déjà pris)
                o1 = obs
                for k in range(j+1, min(j+NB_PTS+1,track.size()), 1):
                    o2 = track[k]
                    if o1.distance2DTo(o2) <= DIST_MAX_2OBS:
                        if str(track["mmtype", k]) != "NOT":
                            PRIS.append(k)
                            # morceau.addObs(o2)
                            #morceau.addObs(tkl.Obs(tkl.ENUCoords(o2.position.getX(), o2.position.getY()),
                            #                        tkl.ObsTime()))
                            POINTS.append((k,tkl.Obs(tkl.ENUCoords(o2.position.getX(), o2.position.getY()),
                                                    tkl.ObsTime())))
                        else:
                            break
                    o1 = o2


            else:
                # On a un trou, sauf si j est pris
                if j not in PRIS and len(POINTS) >= NB_OBS_MIN:
                    newnum = str(mid) + '-i' + str(nummorceau)
                    nummorceau += 1

                    PTS = []
                    points_sorted = sorted(POINTS, key=lambda x: x[0])
                    for p in points_sorted:
                        PTS.append(p[1])

                    morceau = tkl.Track(PTS, tid, newnum)
                    morceau.createAnalyticalFeature('TID', tid)
                    morceau.createAnalyticalFeature('MID', newnum)
                    trackmorceau = tkl.simplify(morceau, 0, tkl.MODE_SIMPLIFY_REM_POS_DUP, verbose=False)
                    if trackmorceau.size() >= NB_OBS_MIN:
                        morceaux.addTrack(trackmorceau)

                    POINTS = []



        if len(POINTS) >= NB_OBS_MIN:
            # morceau.resample(RESAMPLE_SIZE_GRID, mode=tkl.MODE_SPATIAL)
            newnum = str(mid) + '-i' + str(nummorceau)
            nummorceau += 1

            PTS = []
            points_sorted = sorted(POINTS, key=lambda x: x[0])
            for p in points_sorted:
                PTS.append(p[1])

            morceau = tkl.Track(PTS, tid, newnum)
            morceau.createAnalyticalFeature('TID', tid)
            morceau.createAnalyticalFeature('MID', newnum)
            trackmorceau = tkl.simplify(morceau, 0, tkl.MODE_SIMPLIFY_REM_POS_DUP, verbose=False)
            if trackmorceau.size() >= NB_OBS_MIN:
                morceaux.addTrack(trackmorceau)


    # On découpe suivant DIST_MAX_2OBS
    cutCollection = tkl.TrackCollection()
    for segment in morceaux:

        tid = segment.getObsAnalyticalFeature('TID', 0)
        mid = segment.getObsAnalyticalFeature('MID', 0)

        idxSelect = 1
        o1 = None
        newtrack = tkl.Track()
        for o2 in segment:
            if o1 is not None:
                if o1.distance2DTo(o2) > DIST_MAX_2OBS:
                    # on coupe la trace pour créer un nouveau morceau
                    if newtrack.size() >= NB_OBS_MIN:
                        newtrack.resample(RESAMPLE_SIZE_GRID, mode=tkl.MODE_SPATIAL)
                        version = mid + "-s" + str(idxSelect)
                        newtrack.createAnalyticalFeature('TID', tid)
                        newtrack.createAnalyticalFeature('MID', version)
                        newtrack.uid = tid
                        newtrack.tid = version
                        if newtrack.size() < NB_OBS_MIN:
                            print ('----')
                        cutCollection.addTrack(newtrack)
                        idxSelect += 1
                    newtrack = tkl.Track()
                    #newtrack.uid = uid
                    #newtrack.tid = tid
            newtrack.addObs(tkl.Obs(tkl.ENUCoords(o2.position.getX(), o2.position.getY()), o2.timestamp.copy()))
            o1 = o2
    
        # Last track segment
        if newtrack.size() >= NB_OBS_MIN:
            newtrack.resample(RESAMPLE_SIZE_GRID, mode=tkl.MODE_SPATIAL)
            version = mid + "-s" + str(idxSelect)
            newtrack.createAnalyticalFeature('TID', tid)
            newtrack.createAnalyticalFeature('MID', version)
            newtrack.uid = tid
            newtrack.tid = version
            if newtrack.size() < NB_OBS_MIN:
                print ('----')
            cutCollection.addTrack(newtrack)


    # On enregistre
    af_names = ['TID', 'MID']

    tracespath = RESPATH + rep + "/"
    #tkl.TrackWriter.writeToFiles(cutCollection, tracespath,
    #                             id_E=1, id_N=0, id_U=3, id_T=2,
    #                             h=1, separator=";", af_names=af_names)

