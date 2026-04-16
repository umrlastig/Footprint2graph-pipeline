#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 15:01:57 2026

@author: md_vandamme
"""



import tracklib as tkl
import numpy as np

from osgeo import gdal, ogr, osr
from ofnp import Shp2centerline

from skimage.measure import label, regionprops
import numpy as np





surfpath          = '/home/md_vandamme/4_RESEAU/diag1/surface_PT.shp'
roadsurfpath      = '/home/md_vandamme/4_RESEAU/diag1/road_surface_PT.shp'
roadsurflissepath = '/home/md_vandamme/4_RESEAU/diag1/road_surface_lissee_PT.shp'
squelettepath     = '/home/md_vandamme/4_RESEAU/diag1/network/squelette_PT.shp'

shpDriver = ogr.GetDriverByName("ESRI Shapefile")

dsSurface = ogr.Open(surfpath)

# copier la datasource
dsRoadSurface = shpDriver.CopyDataSource(dsSurface, roadsurfpath)

# fermer les datasets
dsSurface = None
dsRoadSurface = None

































