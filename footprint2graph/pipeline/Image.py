# -*- coding: utf-8 -*-

'''
    Calculs des cartes de densités, de constraste et binaire
    A lancer dans la console QGIS

'''

import math
import os
import time
import sys

import csv
csv.field_size_limit(sys.maxsize)

import numpy as np
# import matplotlib.pyplot as plt

from scipy.ndimage import maximum_filter
from skimage.morphology import remove_small_holes, remove_small_objects
from skimage.measure import label, regionprops

from osgeo import gdal, ogr, osr

import tracklib as tkl

from footprint2graph import Shp2centerline






def density_polygonize(RESPATH, G1_SIZE, G2_SIZE, SEUIL_DENSITE, SEUIL_SURFACE,
                       closing = True, prefix='PT',
                       rep='resample_grid', cut_factor=2, interp_dist=5, clean_dist=0,
                       verbose=False):

    #main_text   = "----------------------------------------------------------------------\r\n"
    #main_text  += "STAGE 2 :                                   \r\n"
    #main_text  += "   - Calcul d’une carte de densité à partir des traces GNSS \r\n"
    #main_text  += "   - De la vectorisation on extrait une ligne centrée ≡ arc de la topologie \r\n"
    #main_text  += "----------------------------------------------------------------------\r\n"
    main_text  = "Starting rasterization and vectorization\n"
    print(main_text, end='')


    respath = RESPATH + 'image/'


    # =============================================================================
    #       Chargement des traces GPS
    #  Ici elles sont mises dans un fichier CSV dont la géométrie de la trace est
    #  dans le format WKT
    t0 = time.time()

    fmt = tkl.TrackFormat({'ext': 'CSV',
                           'srid': 'ENU',
                           'id_E': 1,'id_N': 0, 'id_U': 3,'id_T': 2,
                           'separator': ';',
                           'header': 1,
                           'read_all': True})
    
    resampledtracespath = RESPATH + rep + '/'
    tracks = tkl.TrackReader.readFromFile(resampledtracespath, fmt, verbose=False)
    total = len(tracks)
    print ('    Number of tracks to load: ', total)



    bbox = tracks.bbox()

    af_algos = ['uid']
    cell_operators = [tkl.co_count_distinct]

    marge = 0
    resolutionG1 = (G1_SIZE, G1_SIZE)

    rasterG1 = tkl.Raster(bbox=bbox, resolution=resolutionG1, margin=marge,
                    align=tkl.BBOX_ALIGN_LL,
                    novalue=tkl.NO_DATA_VALUE)


    # Pour chaque algo-agg on crée une grille vide
    for idx, af_algo in enumerate(af_algos):
        aggregate = cell_operators[idx]
        cle = tkl.AFMap.getMeasureName(af_algo, aggregate)
        rasterG1.addAFMap(cle)


    cpt = 1
    for trace in tracks:

        if cpt%500 == 0:
            print ('    ', cpt, '/', total)
        cpt += 1

        tid = trace.getObsAnalyticalFeature('TID', 0)
        mid = trace.getObsAnalyticalFeature('MID', 0)
        trace.uid = tid
        trace.tid = mid

        rasterG1.addCollectionToRaster(tkl.TrackCollection([trace]))






    # =============================================================================
    #       Calcul des densités des traces GPS


    # compute aggregate
    print ("Starting heatmap computation ...")
    rasterG1.computeAggregates()

    
    grilleG1 = rasterG1.getAFMap('uid#co_count_distinct')
    for i in range(grilleG1.raster.nrow):
        for j in range(grilleG1.raster.ncol):
            grilleG1.grid[i][j] = grilleG1.grid[i][j] / (G1_SIZE*G1_SIZE)
    
    pathG1 = respath + 'G1_' + prefix + '.asc'
    print ('pathG1', pathG1)
    tkl.RasterWriter.writeMapToAscFile(pathG1, grilleG1)
    


    # =============================================================================

    # Combien de cellules de chaque côté pour la petite résolution ?
    nb = math.floor(G2_SIZE / G1_SIZE)

    epsilon = 0.001
    
    # On construit une grille vide comme G1
    box = tkl.Bbox(tkl.ENUCoords(rasterG1.xmin, rasterG1.ymin),
                   tkl.ENUCoords(rasterG1.xmax, rasterG1.ymax))
    res = rasterG1.resolution
    margin = 0
    align = tkl.BBOX_ALIGN_CENTER
    rasterK = tkl.Raster(bbox=box, resolution=res, margin=margin, align=align)
    rasterK.addAFMap('K')


    G2 = maximum_filter(grilleG1.grid, size=nb)
    pathG2 = respath + 'G2_' + prefix + '.asc'
    print ('pathG2', pathG2)
    writeArray(pathG2, G2)

    
    for i in range(rasterK.nrow):
        for j in range(rasterK.ncol):
            x = rasterK.xmin + j * res[0] + 1
            y = rasterK.ymin - (i - rasterK.nrow + 1) * res[1] + 1
            (column, line) = rasterG1.getCell(tkl.ENUCoords(x, y))
            g1 = grilleG1.grid[line][column]
    
            g2 = G2[line][column] / (nb * G1_SIZE * nb * G1_SIZE)
            #g2 = G2[line][column] / (G2_SIZE * G2_SIZE)
    
            if g1 <= 2 / (G1_SIZE * G1_SIZE):
                g1 = 0
    
            if g2 <= 0:
                g2 = epsilon
    
            k = g1 / g2
    
            rasterK.getAFMap(0).grid[i][j] = k
    
    grilleK = rasterK.getAFMap(0)
    
    pathK = respath + 'K_' + prefix + '.asc'
    tkl.RasterWriter.writeMapToAscFile(pathK, grilleK)



    # =============================================================================

    # On construit une grille vide comme G1
    box = tkl.Bbox(tkl.ENUCoords(rasterK.xmin, rasterK.ymin),
                   tkl.ENUCoords(rasterK.xmax, rasterK.ymax))
    res = rasterK.resolution
    margin = 0
    align = tkl.BBOX_ALIGN_CENTER
    raster = tkl.Raster(bbox=box, resolution=res, margin=margin, align=align)
    raster.addAFMap('B')
    
    for i in range(raster.nrow):
        for j in range(raster.ncol):
            v = grilleK.grid[i][j]
            if v > SEUIL_DENSITE:
                raster.getAFMap(0).grid[i][j] = 1
            else:
                raster.getAFMap(0).grid[i][j] = 0
    
    pathB = respath + 'B_' + prefix + '.asc'
    tkl.RasterWriter.writeMapToAscFile(pathB, raster.getAFMap(0))


    t1 = time.time()
    total = t1-t0
    print ("    Execution time (seconds):", total)
    print ("    Finished heatmap computation.")
    t0 = t1

    # =========================================================================
    print ("Starting morphological closing ...")

    pathB             = respath + 'B_' + prefix + '.asc'
    patherosion       = respath + 'erosion_' + prefix + '.tif'
    pathdilatation    = respath + 'dilatation_' + prefix + '.tif'
    pathrien          = respath + 'rien_' + prefix + '.tif'
    surfpath          = respath + 'surface_' + prefix + '.shp'
    roadsurfpath      = respath + 'road_surface_' + prefix + '.shp'
    roadsurflissepath = respath + 'road_surface_lissee_' + prefix + '.shp'
    squelettepath     = RESPATH + 'network/squelette_' + prefix + '.shp'

    try:
        os.remove(patherosion)
        os.remove(pathdilatation)
        if verbose:
            print(f"Files '{patherosion}' and '{pathdilatation}' deleted successfully.")
    except FileNotFoundError:
        if verbose:
            print(f"File '{patherosion}' or '{pathdilatation}' not found.")

    try:
        os.remove(respath + 'road_surface_' + prefix + '.shp')
        os.remove(respath + 'road_surface_' + prefix + '.shx')
        os.remove(respath + 'road_surface_' + prefix + '.dbf')
        os.remove(respath + 'road_surface_' + prefix + '.prj')
        if verbose:
            print(f"Files road_surface.shp deleted successfully.")
    except FileNotFoundError:
        if verbose:
            print(f"File '{roadsurfpath}' not found.")

    try:
        os.remove(respath + 'road_surface_lissee_' + prefix + '.shp')
        os.remove(respath + 'road_surface_lissee_' + prefix + '.shx')
        os.remove(respath + 'road_surface_lissee_' + prefix + '.dbf')
        if verbose:
            print(f"Files road_surface_lissee.shp deleted successfully.")
    except FileNotFoundError:
        if verbose:
            print(f"File '{roadsurflissepath}' not found.")

    try:
        os.remove(respath + 'surface_' + prefix + '.shp')
        os.remove(respath + 'surface_' + prefix + '.shx')
        os.remove(respath + 'surface_' + prefix + '.dbf')
        os.remove(respath + 'surface_' + prefix + '.prj')
        if verbose:
            print(f"Files surface.shp deleted successfully.")
    except FileNotFoundError:
        if verbose:
            print(f"File '{roadsurfpath}' not found.")

    try:
        os.remove(RESPATH + 'network/squelette_' + prefix + '.shp')
        os.remove(RESPATH + 'network/squelette_' + prefix + '.shx')
        os.remove(RESPATH + 'network/squelette_' + prefix + '.dbf')
        os.remove(RESPATH + 'network/squelette_' + prefix + '.cpg')
        if verbose:
            print(f"Files '{squelettepath}' deleted successfully.")
    except FileNotFoundError:
        if verbose:
            print(f"File '{squelettepath}' not found.")





    # =============================================================================
    #   On charge le binaire

    rasterB = tkl.RasterReader.readFromAscFile(pathB, name='B', separator='\t')
    mapBinaire = rasterB.getAFMap('B')




    # =============================================================================
    #   Dilatation + Erosion

    if closing:
        mask = np.array([
            [0,1,0],
            [1,1,1],
            [0,1,0]])

        # Dilatation
        mapBinaire.filter(mask, np.max)
        tkl.RasterWriter.writeMapToAscFile(pathdilatation, mapBinaire)

        # Erosion
        if prefix=='PT':
            mapBinaire.filter(np.array([[1]]), lambda x : 1-x)     # Dual de la carte
            mapBinaire.filter(mask, np.max)                        # Dilatation
            mapBinaire.filter(np.array([[1]]), lambda x : 1-x)     # Dual de la carte
            tkl.RasterWriter.writeMapToAscFile(patherosion, mapBinaire)
            pathdepart = patherosion
        else:
            pathdepart = pathdilatation
    else:
        asize = G1_SIZE * G1_SIZE * G1_SIZE * G1_SIZE + 1
        clean = remove_small_holes(mapBinaire.grid.astype(bool), area_threshold=asize,
                                     connectivity=1)
        clean = remove_small_objects(clean, min_size=asize,
                                     connectivity=1)
        clean_uint8 = clean.astype(np.uint8)


        # print(np.unique(clean_uint8))

        mapBinaire.grid = clean_uint8



        tkl.RasterWriter.writeMapToAscFile(pathrien, mapBinaire)
        pathdepart = pathrien



    t1 = time.time()
    total = t1-t0
    print ("    Execution time (seconds):", total)
    print ("    Finished morphological opening.")
    t0 = t1



    # =========================================================================
    #   Vectorisation dans le layer surface

    print ("Vectorizing ...")

    shpDriver = ogr.GetDriverByName("ESRI Shapefile")
    dsSurface = shpDriver.CreateDataSource(surfpath)

    l93Ref = osr.SpatialReference()
    l93Ref.SetFromUserInput('EPSG:2154')

    surfaceLayername = 'surface'
    layerSurface = dsSurface.CreateLayer(surfaceLayername, srs=l93Ref)

    fld2 = ogr.FieldDefn("DN", ogr.OFTInteger)
    layerSurface.CreateField(fld2)
    dst_field = layerSurface.GetLayerDefn().GetFieldIndex("DN")

    #  get raster datasource
    dsDepart = gdal.Open(pathdepart)
    srcband = dsDepart.GetRasterBand(1)

    gdal.Polygonize(srcband, None, layerSurface, dst_field, [], callback=None)

    # forcer écriture
    layerSurface.SyncToDisk()
    dsSurface.FlushCache()
    
    # fermeture propre
    layerSurface = None
    dsSurface = None
    dsDepart = None


    # =========================================================================
    # On "transfere" Surface vers RoadSurface

    # ouvrir la source
    dsSurface = ogr.Open(surfpath)
    layer = dsSurface.GetLayer(0)
    print("    Number of polygonize features: ", layer.GetFeatureCount())

    dsRoadSurface = shpDriver.CreateDataSource(roadsurfpath)
    layerRoadSurface = dsRoadSurface.CreateLayer("road_surface", srs=l93Ref)

    '''
    DN=0 + filtre sur la surface + id + enleve le cadre
           on corrige la géométrie
    '''

    field_defn = ogr.FieldDefn("id", ogr.OFTInteger)
    layerRoadSurface.CreateField(field_defn)

    cpt = 0

    minx1, maxx1, miny1, maxy1 = layerRoadSurface.GetExtent()
    extent = bbox_to_polygon(minx1, maxx1, miny1, maxy1)

    for feat in layer:
        geom = feat.GetGeometryRef()
        # print(geom.IsValid(), feat.GetField("DN"))

        if feat.GetField("DN") == 1:
            # print ('DN = 1')
            if geom is not None:
                area = geom.GetArea()
                if area > SEUIL_SURFACE:
                    # print ('Bonne surface')

                    minx2, maxx2, miny2, maxy2 = geom.GetEnvelope()
                    envelope = bbox_to_polygon(minx2, maxx2, miny2, maxy2)

                    intersection = extent.Intersection(envelope)
                    union = extent.Union(envelope)
                    iou = intersection.GetArea() / union.GetArea()
                    if iou < 0.99:
                        cpt += 1
                        # print ('pas cadre')
                        g = geom.Clone()
                        if not g.IsValid():
                            g = g.Buffer(0)

                        new_feat = ogr.Feature(layerRoadSurface.GetLayerDefn())
                        new_feat.SetGeometry(g)
                        new_feat.SetField("id", cpt)
                        layerRoadSurface.CreateFeature(new_feat)
                        new_feat = None


    print("    Number of polygonize features copied: ", cpt)

    # fermer proprement
    layerRoadSurface.SyncToDisk()
    dsRoadSurface = None


    # -----------------------------------------
    #
    t1 = time.time()
    total = t1-t0
    print ("    Execution time (seconds):", total)
    print ("    Vectorization completed.")
    t0 = t1



    # =========================================================================
    #   Lissage du polygone pour oublier le profil en escalier

    print ('Smoothing polygon to remove stair-step artifacts ...')

    smoothingLayer(roadsurfpath, roadsurflissepath, shpDriver, G1_SIZE, cut_factor)

    t1 = time.time()
    total = t1-t0
    print ("    Execution time (seconds):", total)
    print ("    Road surface smoothing completed.")
    t0 = t1


    # =========================================================================
    #   Squeletisation : centerline

    print ('Starting centerline computation ...')

    Shp2centerline(roadsurflissepath, squelettepath, interp_dist, clean_dist, verbose=False)

    t1 = time.time()
    total = t1-t0
    print ("    Execution time (seconds):", total)
    print ("    Centerline computed.")


    # =========================================================================

    print ("Stage 2 completed: rasterization and vectorization.")
    # Fin



def bbox_to_polygon(minx, maxx, miny, maxy):
    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint(minx, miny)
    ring.AddPoint(maxx, miny)
    ring.AddPoint(maxx, maxy)
    ring.AddPoint(minx, maxy)
    ring.AddPoint(minx, miny)

    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(ring)
    return poly



def smoothingLayer(roadsurfpath, roadsurflissepath, shpDriver, r, f):

    dsRoadSurface = ogr.Open(roadsurfpath, 1)
    layerRoadSurface = dsRoadSurface.GetLayer()

    # Créer datasource
    dsRoadSurfaceLissee = shpDriver.CreateDataSource(roadsurflissepath)
    
    # Créer layer
    layerRoadSurfaceLissee = dsRoadSurfaceLissee.CreateLayer(
        "road_surface_lissee",
        layerRoadSurface.GetSpatialRef(),
        geom_type = ogr.wkbPolygon
    )
    
    # copier les champs attributaires
    src_defn = layerRoadSurface.GetLayerDefn()
    for i in range(src_defn.GetFieldCount()):
        field_defn = src_defn.GetFieldDefn(i)
        layerRoadSurfaceLissee.CreateField(field_defn)

    dst_defn = layerRoadSurfaceLissee.GetLayerDefn()


    dsRoadSurface = ogr.Open(roadsurfpath, 0)
    layerRoadSurface = dsRoadSurface.GetLayer()
    for feature in layerRoadSurface:
        geom = feature.GetGeometryRef().Clone()
        if geom is None:
            continue

        polygon = ogr.Geometry(ogr.wkbPolygon)

        # ==================================================================
        # Gestion de l'extérieur
        # ==================================================================
        exterior_ring = geom.GetGeometryRef(0)
        exterior = exterior_ring.GetPoints()
        # x = [p[0] for p in exterior]
        # y = [p[1] for p in exterior]
        # plt.plot(x, y, 'b-', linewidth=0.5)

        # ------------------------------------------------------------------
        # Géométrie filtrée
        # ------------------------------------------------------------------
        out = smoothing(exterior, r, f)
        xout = [p[0] for p in out]
        yout = [p[1] for p in out]
        #plt.plot(xout, yout, 'r-', linewidth=0.75)

        # ------------------------------------------------------------------
        # Construit une ligne
        # ------------------------------------------------------------------
        newring = ogr.Geometry(ogr.wkbLinearRing)
        for i in range(len(xout)):
            newring.AddPoint(xout[i], yout[i])
        newring.CloseRings()
        polygon.AddGeometry(newring)

        # ==================================================================
        # Gestion des intérieurs éventuels
        # ==================================================================
        for j in range(1, geom.GetGeometryCount()):
            ring = geom.GetGeometryRef(j)
            interior = ring.GetPoints()
            is_closed = interior[0] == interior[-1]
            if not is_closed or geom.GetArea() <= 0.001:
                continue

            #x = [p[0] for p in interior]
            #y = [p[1] for p in interior]
            #plt.plot(x, y, 'b-', linewidth=0.5)
                
            # ------------------------------------------------------------------
            # Géométrie filtrée
            # ------------------------------------------------------------------
            out = smoothing(interior, r, f)
            xout = [p[0] for p in out]
            yout = [p[1] for p in out]
            #plt.plot(xout, yout, 'r-', linewidth=0.75)

            # ------------------------------------------------------------------
            # Construit une ligne
            # ------------------------------------------------------------------
            newring = ogr.Geometry(ogr.wkbLinearRing)
            for i in range(len(xout)):
                newring.AddPoint(xout[i], yout[i])
            newring.CloseRings()
            polygon.AddGeometry(newring)


        # =====================================================================
        # Créer une nouvelle feature
        # =====================================================================
        dst_feat = ogr.Feature(dst_defn)
        
        # Copier les attributs
        for i in range(dst_defn.GetFieldCount()):
            dst_feat.SetField(i, feature.GetField(i))
        
        # Assigner la géométrie
        dst_feat.SetGeometry(polygon)
        
        # Ajouter au layer
        layerRoadSurfaceLissee.CreateFeature(dst_feat)
        
        dst_feat = None


    dsRoadSurface = None
    dsRoadSurfaceLissee = None
    




# --------------------------------------------------------------------------------------
# Filtre de Fourier coupe-bande sur une géométrie
# --------------------------------------------------------------------------------------
# Inputs:
#    - geom  : polygone (simple)
#    - r     : résolution centrale de coupure (en m)
#    - f     : facteur de coupure
# Output: géométrie filtrée avec suppression de toutes les longueurs d'onde comprises 
# entre r/f et r*f
# --------------------------------------------------------------------------------------
def smoothing(geom, r, f):

    # Préparation
    wl_sup = r*f
    wl_inf = r/f
    
    x = [p[0] for p in geom]
    y = [p[1] for p in geom]
    
    trace = tkl.Track()
    for ii in range(len(x)):
        trace.addObs(tkl.Obs(tkl.ENUCoords(x[ii], y[ii], 0)))

    N = len(trace)
    
    # Centrage du signal
    trace = trace.copy()
    c0 = trace.getCentroid(); 
    cx = c0.E; cy = c0.N
    trace.translate(-cx, -cy)
    
    # Sauvegarde des extrémités
    ci = trace[0]
    cf = trace[-1]
    
    # Periodisation du signal
    geom_in = trace + trace + trace
    
    # Filtre coupe-bande
    signal_low_freq = tkl.filter_freq(geom_in, (1.0/wl_sup), mode=tkl.FILTER_SPATIAL,
                                      type=tkl.FILTER_LOW_PASS , dim=tkl.FILTER_XY)[N:2*N]
    signal_hgh_freq = tkl.filter_freq(geom_in, (1.0/wl_inf), mode=tkl.FILTER_SPATIAL,
                                      type=tkl.FILTER_HIGH_PASS, dim=tkl.FILTER_XY)[N:2*N]
   
    # Somme passe-haut/passe-bas
    out = trace.copy()
    for i in range(N):
        out[i, "x"] = signal_low_freq[i, "x"] + signal_hgh_freq[i, "x"]
        out[i, "y"] = signal_low_freq[i, "y"] + signal_hgh_freq[i, "y"] 
        
    # Reconstruction des extrémités 
    out[0]  = ci
    out[-1] = cf   
        
    # Decentrage du signal
    out.translate(cx, cy)
    
    # Retransformation en géométrie
    out_geom = [(obs.position.getX(), obs.position.getY()) for obs in out]
    
    return out_geom



def writeArray(filename, arr):

    with open("output.asc", "w") as f:
        f.write(f"ncols {arr.shape[1]}\n")
        f.write(f"nrows {arr.shape[0]}\n")
        f.write("xllcorner 0\n")
        f.write("yllcorner 0\n")
        f.write("cellsize 1\n")
        f.write("NODATA_value -9999\n")
    
        np.savetxt(f, arr, fmt="%d")



