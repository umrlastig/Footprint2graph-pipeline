:Author: Marie-Dominique Van Damme
:Version: 1.0
:License: --
:Date: 08/04/2026


Installation
=============

# Environment Setup

## Requirements

OutdoorFootprintNetworkPipeline requires the following Python packages and Plugin QGIS:

- Tracklib
- osgeo : gdal, ogr, osr (pour la partie vectorisation)
- Fiona, Shapely (centerline et smooth)




## "Just want to run the pipeline on a use case" Environment Setup

1. Install tracklib


2. Configuer dans QGis la librairie tracklib:

Cliquer dans la barre de menu sur Préférences >> Options >> Système >> 

Puis dans le bloc "Environnement", ajouter une variable personnalisée:

*Appliquer* : ajouter au début
*Variable*  : PYTHONPATH
*Valeur*    : /home/glagaffe/7_LIB/tracklib



## How to Run the Code



### Input

A GNSS trace dataset in CSV format is required.


### Execution

Run this source code in the Python console. Execute MainWorkflow.py to start the creation scripts.





