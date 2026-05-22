# -*- coding: utf-8 -*-


import tracklib as tkl

from footprint2graph import logEnv
from . import segmentation_resample
from . import density_polygonize


# Paramètre : Nombre de points minimum pour un morceau de trace au moment du découpage
#             si le nombre n'est pas atteint, le morceau de trace est oublié
NB_OBS_MIN           = 10

# Paramètre : Distance en mètres entre 2 points, si supérieure au seuil on coupe la trace
DIST_MAX_2OBS        = 50


RESAMPLE_SIZE_GRID = 1
RESAMPLE_SIZE_FUSION = 5


G1_SIZE = 2
G2_SIZE = 30 # 30, 50









def run_iteration(pipeline_idx, respath, collection):

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

    segmentation_resample(respath, collection, fmt, NB_OBS_MIN, DIST_MAX_2OBS,
                RESAMPLE_SIZE_GRID, RESAMPLE_SIZE_FUSION)


    SEUIL_DENSITE = 450 # 360 - 500 - 280 - 15 - 1000
    SEUIL_SURFACE = 1000 # m2 - 50000 - 7000
    cut_factor = 5
    closing = False
    density_polygonize(respath, G1_SIZE, G2_SIZE, SEUIL_DENSITE, SEUIL_SURFACE, closing,
                       prefix='PT', rep='resample_grid', cut_factor=cut_factor)


    SEARCH = 50
    h = 10
