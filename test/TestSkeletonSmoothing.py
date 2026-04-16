# -*- coding: utf-8 -*-

# skeleton_smoothing

import fiona
from shapely.geometry import shape

import matplotlib.pyplot as plt
import progressbar
from ofnp import skeleton_smoothing, deleteSmallEdge

import tracklib as tkl




prefix = 'PT'
RESPATH = r'/home/md_vandamme/4_RESEAU/ZTEMP/'

fmt = tkl.NetworkFormat({
       "pos_edge_id": 0,
       "pos_source": 1,
       "pos_target": 2,
       "pos_wkt": 3,
       "srid": "ENU",
       "separator": ",",
       "header": 1})



output_file = str(RESPATH) + 'network/squelette_topology_' + str(prefix) + '.csv'
network = tkl.NetworkReader.readFromFile(output_file, fmt, verbose=False)

network.simplify(0, tkl.MODE_SIMPLIFY_REM_POS_DUP, verbose=False)

for idx in progressbar.progressbar(network.getEdgesId()):
    network.getEdge(idx).geom = skeleton_smoothing(
        network.getEdge(idx).geom, 5, 10) # 5-10

network.simplify(5, tkl.MODE_SIMPLIFY_DOUGLAS_PEUCKER, verbose=False)


# On reconstruit un réseau

input_file = str(RESPATH) + 'network/edgegeom2.csv'
with open(input_file, "w") as f:
    for edge in network:
        f.write(edge.geom.toWKT() + "\n")
output_file = str(RESPATH) + 'network/squelette_topology_' + str(prefix) + '2.csv'
tkl.Topology.create_topology(input_file, '2154', output_file)

network = tkl.NetworkReader.readFromFile(output_file, fmt, verbose=False)
network.plot('k-', nodes='ko', size=0.8)
plt.show()




# On enlève les petits arcs

DIST_MIN_ARC = 20
nb = deleteSmallEdge(network, DIST_MIN_ARC)
print ('    nb arcs supprimés: ', nb)
network.plot('k-', nodes='ko', size=0.8)
plt.show()

'''
cpt = 0
nb = 1000
while nb > 10 and cpt < 10:
    nb = deleteSmallEdge(network, DIST_MIN_ARC)
    print ('    nb arcs supprimés: ', nb)
    cpt += 1




'''




