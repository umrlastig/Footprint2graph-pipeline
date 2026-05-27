# -*- coding: utf-8 -*-


import os
import platform
import psutil
import shutil
import time

from . import log_event


def prepareEnv(respath, iteration_index = None):
    '''
    On supprime tous les répertoires
    '''
    if iteration_index is None or int(iteration_index) <= 0:
        for filename in os.listdir(respath):
            file_path = os.path.join(respath, filename)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
    else:
        idx = int (iteration_index)




def setupEnv(respath, iteration_index = -1):
    """ =================================================================== """
    """     Preparation de l'environnement pour une itération               """
    """   - création des répertoires si nécessaire                          """
    """                                                                     """
    """ =================================================================== """

    idx = int (iteration_index)

    if idx == 1:
        if not os.path.exists(respath + 'decoup'):
            os.makedirs(respath + 'decoup')
        if not os.path.exists(respath + 'resample_grid'):
            os.makedirs(respath + 'resample_grid')
        if not os.path.exists(respath + 'resample_fusion'):
            os.makedirs(respath + 'resample_fusion')
        if not os.path.exists(respath + 'image'):
            os.makedirs(respath + 'image')
        if not os.path.exists(respath + 'network'):
            os.makedirs(respath + 'network')
        if not os.path.exists(respath + 'mapmatch'):
            os.makedirs(respath + 'mapmatch')
        if not os.path.exists(respath + 'mapmatch/tmm'):
            os.makedirs(respath + 'mapmatch/tmm')
        if not os.path.exists(respath + 'geometry'):
            os.makedirs(respath + 'geometry')
        if not os.path.exists(respath + 'geometry/fusion'):
            os.makedirs(respath + 'geometry/fusion')
        if not os.path.exists(respath + 'geometry/raccord'):
            os.makedirs(respath + 'geometry/raccord')

    '''
    
    
    if not os.path.exists(RESPATH + 'mapmatch/tmm1'):
        os.makedirs(RESPATH + 'mapmatch/tmm1')
        if not os.path.exists(RESPATH + 'mapmatch/tmm2'):
            os.makedirs(RESPATH + 'mapmatch/tmm2')

    if not os.path.exists(RESPATH + 'geometry/fusion1'):
        os.makedirs(RESPATH + 'geometry/fusion1')
    if not os.path.exists(RESPATH + 'geometry/fusion2'):
        os.makedirs(RESPATH + 'geometry/fusion2')

    
    if not os.path.exists(RESPATH + 'geometry/raccord1'):
        os.makedirs(RESPATH + 'geometry/raccord1')
    if not os.path.exists(RESPATH + 'geometry/raccord2'):
        os.makedirs(RESPATH + 'geometry/raccord2')

    if not os.path.exists(RESPATH + 'points_not_mm_1'):
        os.makedirs(RESPATH + 'points_not_mm_1')
    if not os.path.exists(RESPATH + 'points_not_mm_2'):
        os.makedirs(RESPATH + 'points_not_mm_2')
    '''


def logEnv(RESPATH):
    try:
        user = os.getlogin()
        system = platform.system() + '-' + platform.processor()
        pythonversion = platform.python_version()
        process = psutil.Process(os.getpid())
        memory_bytes = process.memory_info().rss
        memory_mb = memory_bytes / (1024 * 1024)

        log_event(RESPATH + "env.json", {
            "User": user,
            "System": system,
            "Python version": pythonversion,
            "Heap memory": round(memory_mb), # ' Mo'
            "ts": time.time()
        })
    except Exception as e:
        print (e)
        print ('ERROR in Environment Information.')



def STEnv(RESPATH, collection):
    try:
        bbox = collection.bbox()
        log_event(RESPATH + "stac.json", {
            "bbox": "bbox"
        })
    except Exception as e:
        print (e)
        print ('ERROR in Environment Information.')



'''
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
'''