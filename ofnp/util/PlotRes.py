# -*- coding: utf-8 -*-


import tracklib as tkl

import fiona
import geopandas as gpd
from shapely.geometry import LineString, MultiLineString
from shapely.geometry import shape as geom_shape


def matPlotRaster(pathres, filename, append):
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




def plotMM(pathres):
    collection = tkl.TrackCollection()
    mmtrackpath = respath + '/mapmatch/tmm/'
    for mmfilename in os.listdir(mmtrackpath):
        fmt = tkl.TrackFormat({'ext': 'CSV',
                               'srid': 'ENU',
                               'id_E': 1,'id_N': 0, 'id_U': 3,'id_T': 2,
                               'separator': ';',
                               'header': 0,
                               'comment': '#',
                               'read_all': True})
        trace = tkl.TrackReader.readFromFile(mmtrackpath + mmfilename, fmt)
        collection.addTrack(trace)
    '''
    for i in range(collection.size()):
        track = collection.getTrack(i)
        pkid = track.tid
        # print (pkid)

        num = track.getObsAnalyticalFeature('num', 0)
        track_id = track.getObsAnalyticalFeature('track_id', 0)
        user_id = track.getObsAnalyticalFeature('user_id', 0)

        for j in range(track.size()):
            obs = track.getObs(j)
            x = float(obs.position.getX())
            y = float(obs.position.getY())
            pt1 = QgsPointXY(x, y)
            g1 = QgsGeometry.fromPointXY(pt1)

            s = track["hmm_inference", j]
            hmminf = list(map(float, re.findall(r"[0-9.]+", s)))
            ds = float(hmminf[4])
            dt = float(hmminf[5])
            edgeid = track["idedge", j]

            # print (track["mmtype", j])

            if str(track["mmtype", j]) == "NOT":
                # pas de MM
                attrs1 = [str(pkid), j, x, y, -1, -1, 'NOTMM', num, track_id, user_id]
                fet = QgsFeature()
                fet.setAttributes(attrs1)
                fet.setGeometry(g1)
                pr.addFeature(fet)
            if str(track["mmtype", j]) == "EDGE":
                xmm = hmminf[0]
                ymm = hmminf[1]
                pt2 = QgsPointXY(xmm, ymm)
                g2 = QgsGeometry.fromPointXY(pt2)

                attrs1 = [str(pkid), j, x, y, float(xmm), float(ymm), 'ARC', num, track_id, user_id]
                fet = QgsFeature()
                fet.setAttributes(attrs1)
                fet.setGeometry(g2)
                pr.addFeature(fet)

                line = QgsGeometry.fromPolylineXY([pt1, pt2])
                fet = QgsFeature()
                fet.setGeometry(line)
                attrs1 = [str(pkid), str(edgeid), ds, dt, num, track_id, user_id]
                fet.setAttributes(attrs1)
                prMM.addFeature(fet)

            if str(track["mmtype", j]) == "SOURCE" or str(track["mmtype", j]) == "TARGET":
                xmm = hmminf[0]
                ymm = hmminf[1]
                pt2 = QgsPointXY(xmm, ymm)
                g2 = QgsGeometry.fromPointXY(pt2)

                attrs1 = [str(pkid), j, x, y, float(xmm), float(ymm), 'NOEUD', num, track_id, user_id]
                fet = QgsFeature()
                fet.setAttributes(attrs1)
                fet.setGeometry(g2)
                pr.addFeature(fet)

                line = QgsGeometry.fromPolylineXY([pt1, pt2])
                fet = QgsFeature()
                fet.setGeometry(line)
                attrs1 = [str(pkid), str(edgeid), ds, dt, num, track_id, user_id]
                fet.setAttributes(attrs1)
                prMM.addFeature(fet)
    '''


