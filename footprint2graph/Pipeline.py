# -*- coding: utf-8 -*-


import tracklib as tkl

from footprint2graph import logEnv, STEnv
from footprint2graph import segmentation_resample
from footprint2graph import density_polygonize
from footprint2graph import addTopologyToNetwork
from footprint2graph import createNetworkGeom


# Paramètre : Nombre de points minimum pour un morceau de trace au moment du découpage
#             si le nombre n'est pas atteint, le morceau de trace est oublié
NB_OBS_MIN           = 10 # il faudrait qu'une trace fasse au moins 50m


# Paramètre : Distance en mètres entre 2 points,
#             si supérieure au seuil on coupe la trace
DIST_MAX_2OBS        = 50


# Pour des raisons logistiques, on sur-échantillone la trace :
#   - 1m pour le traitement d'images
#   - 5m pour la fusion
RESAMPLE_SIZE_GRID   = 1
RESAMPLE_SIZE_FUSION = 5


# Définition des grilles géométrique et contraste
G1_SIZE              = 2
G2_SIZE              = 30



def run_iteration(pipeline_idx, respath, collection):
    '''
    En entrée une collection de traces avec un TID

    Parameters
    ----------
    pipeline_idx : TYPE
        DESCRIPTION.
    respath : TYPE
        DESCRIPTION.
    collection : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    '''

    logEnv(respath)

    #  On définit un format pour le stockage des traces modifiées dans le pipeline
    fmt = tkl.TrackFormat({'ext': 'CSV',
                       'srid': 'ENU',
                       'id_E': 1, 'id_N': 0, 'id_U': 3, 'id_T': 2,
                       'time_fmt': '2D/2M/4Y 2h:2m:2s',
                       'separator': ';',
                       'header': 0,
                       'cmt': '#',
                       'read_all': True})

    # -------------------------------------------------------------------------
    #    PREPARE COLLECTION
    #
    if collection is not None:
        segmentation_resample(respath, collection, fmt, NB_OBS_MIN, DIST_MAX_2OBS,
                    RESAMPLE_SIZE_GRID, RESAMPLE_SIZE_FUSION)



    # -------------------------------------------------------------------------
    #    STEP 1 : IMAGE
    #
    SEUIL_DENSITE = 25    # 20-24-34 - 450 - 360 - 500 - 280 - 15 - 1000
    SEUIL_SURFACE = 1000  # m2 - 50000 - 7000
    cut_factor    = 5
    density_polygonize(respath, G1_SIZE, G2_SIZE, SEUIL_DENSITE, SEUIL_SURFACE,
                       pipeline_idx,
                       cut_factor=cut_factor)
    
    # -------------------------------------------------------------------------
    #    STEP 2 : TOPOLOGY
    #
    SEARCH = 50
    h = 10
    addTopologyToNetwork(respath, SEARCH, h, pipeline_idx)


    # -------------------------------------------------------------------------
    #    STEP 3 : GEOMETRY
    #
    SEARCH = 20
    BUFFER = 15
    createNetworkGeom(RESPATH, SEARCH, BUFFER)









