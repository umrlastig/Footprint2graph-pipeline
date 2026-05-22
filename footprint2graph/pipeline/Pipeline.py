# -*- coding: utf-8 -*-


import tracklib as tkl

from footprint2graph import logEnv
from . import segmentation_resample


# Paramètre : Nombre de points minimum pour un morceau de trace au moment du découpage
#             si le nombre n'est pas atteint, le morceau de trace est oublié
NB_OBS_MIN           = 10

# Paramètre : Distance en mètres entre 2 points, si supérieure au seuil on coupe la trace
DIST_MAX_2OBS        = 50


RESAMPLE_SIZE_GRID = 1
RESAMPLE_SIZE_FUSION = 5




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


    #density_polygonize(RESPATH, G1_SIZE, G2_SIZE, SEUIL_DENSITE, SEUIL_SURFACE, closing,
    #               prefix='PT', rep='resample_grid', cut_factor=cut_factor)