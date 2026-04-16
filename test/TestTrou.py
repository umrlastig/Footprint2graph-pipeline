# -*- coding: utf-8 -*-

import os
import time
from scipy.ndimage import maximum_filter
from skimage.morphology import remove_small_holes, remove_small_objects

# import matplotlib.pyplot as plt

import tracklib as tkl
import numpy as np

from osgeo import gdal, ogr, osr
from ofnp import Shp2centerline

from skimage.measure import label, regionprops
import numpy as np



pathB = '/home/md_vandamme/4_RESEAU/ZTEMP/image/B_PT.asc'
rasterB = tkl.RasterReader.readFromAscFile(pathB, name='B', separator='\t')
mapBinaire = rasterB.getAFMap('B')


G1_SIZE = 2
asize = G1_SIZE * G1_SIZE * G1_SIZE * G1_SIZE + 1
clean = remove_small_holes(mapBinaire.grid.astype(bool), area_threshold=asize,
                             connectivity=1)
clean = remove_small_objects(clean, min_size=asize,
                             connectivity=1)
clean_uint8 = clean.astype(np.uint8)


holes = clean_uint8.astype(bool)
print(np.any(holes[0,:]), np.any(holes[-1,:]))