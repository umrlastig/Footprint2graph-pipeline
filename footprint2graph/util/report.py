# -*- coding: utf-8 -*-


import json
# import os



def log_event(RESPATH, event):
    path = RESPATH
    with open(path, "a") as f:
        f.write(json.dumps(event) + "\n")



def reportfile():
    print ('-----------------------------------------------------------------')
    print ('                  PIPELINE REPORT FILE                           ')
    print ('-----------------------------------------------------------------')

    

'''
print ('==================================================================================')
print ('                          PIPELINE REPORT INFORMATION                             ')
print ('==================================================================================')
print ('')

print ('----------------------------------------------------------------------------------')
print ('#  Environment information')
print ('')
print ('Date : ' + str(tkl.ObsTime.now()))
try:
    print ('User : ' + os.getlogin())
    print ('System : ' + platform.system() + '-' + platform.processor()) 
    print ('Python version : ' + platform.python_version())
    memory_bytes = process.memory_info().rss
    memory_mb = memory_bytes / (1024 * 1024)
    print ('Heap memory : ' + str(round(memory_mb)) + ' Mo')
except:
    print ('ERROR')
print ('')


print ('----------------------------------------------------------------------------------')
print ('#  INPUT DATA')
print ('')
print ('* Input tracks ')
print ('Number of tracks = ' + str(collection.size))
print ('Number of points = '+ str(10000))


print ('* Input network')
print ('Taille du réseau:')
print ('Number of edges = ' + str(len(network.EDGES))) 
print ('Number of nodes = ' + str(len(network.NODES))) 


print ('Emprise spatiale:')
print ('')


print ('==================================================================================')
print ('#  Images')
print ('')
print ('')



print ('==================================================================================')
print ('#  Topologie: du squelette au squelette simplifié')
print ('')
print ('')


print ('==================================================================================')
print ('#  Candidatures')
print ('')
print ('')

print ('==================================================================================')
print ('#  Map-matching')
print ('')
print ('Search radius = ' + str(SEARCH) + ' m')
percentMM = (nbmm / trace.size() * 100)
print ('')
print ('Number of map-matched points = ' + str(nbmm) + ' (' + str(round(percentMM, 2)) + ' %)')
percentHP = (nbhp / trace.size() * 100)
print ('Number of off-road = '+ str(nbhp) + ' (' + str(round(percentHP, 2)) + ' %)') 
print ('')
##    rmse = round(math.sqrt(d/nbmm),2)
##    print ('GPS standard error = ' + str(rmse) + ' m')
print ('')

print ('==================================================================================')
print ('#  Fusion')
print ('')
print ('')

print ('==================================================================================')
print ('#  Raccord')
print ('')

print ('==================================================================================')
print ('#  Qualité')
print ('')
print ('GINI:')
print ('')
'''