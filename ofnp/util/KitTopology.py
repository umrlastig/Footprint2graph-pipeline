# -*- coding: utf-8 -*-

'''

Functions to prepare 
- createNetwork



'''


from tracklib import Network, Node
from tracklib import compare, MODE_COMPARISON_HAUSDORFF
import tracklib as tkl
import sys


def createNetwork(collection, threshold):
    '''
    function to create a network from a collection of tracks.


    Parameters
    ----------
    collection : TrackCollection
        collection of tracks where track represents geometry of edges.
    threshold : float
        threshold to find candidates for nodes in fusion.

    Returns
    -------
    network : tracklib.Network
        network with edges and nodes.

    '''

    network = tkl.Network()
    cptNode = 1

    for track in collection:
        edge_id = tkl.NetworkReader.counter
        track.tid = edge_id
        tkl.NetworkReader.counter = tkl.NetworkReader.counter + 1

        edge = tkl.Edge(edge_id, track)
        edge.orientation = tkl.Edge.DOUBLE_SENS
        edge.weight = track.length()


        # On cherche si les noeuds n'existent pas déjà et si c'est le cas
        #   on change aussi la géométrie des premiers et derniers noeuds

        # Source node
        p1 = track.getFirstObs().position
        candidates1 = tkl.selectNodes(network, tkl.Node(-1, p1), threshold)
        if len(candidates1) == 1:
            noeudIni = candidates1[0]
            edge.geom.setObs(0, tkl.Obs(noeudIni.coord, tkl.ObsTime()))
        elif len(candidates1) > 1:
            # plusieurs, on prend le plus proche
            d = sys.float_info.max
            for c in candidates1:
                if c.coord.distance2DTo(p1) <= d:
                    noeudIni = c
                    edge.geom.setObs(0, tkl.Obs(c.coord, tkl.ObsTime()))
                    d = c.coord.distance2DTo(p1)
        else:
            noeudIni = tkl.Node(cptNode, p1)
            cptNode += 1

        # Target node
        p2 = track.getLastObs().position
        candidates2 = tkl.selectNodes(network, tkl.Node(-2, p2), threshold)
        if noeudIni in candidates2:
            candidates2.remove(noeudIni)

        if len(candidates2) == 1:
            noeudFin = candidates2[0]
            edge.geom.setObs(edge.geom.size()-1, tkl.Obs(noeudFin.coord, tkl.ObsTime()))
        elif len(candidates2) > 1:
            d = sys.float_info.max
            for c in candidates2:
                if c.coord.distance2DTo(p2) < d:
                    noeudFin = c
                    edge.geom.setObs(edge.geom.size()-1, tkl.Obs(c.coord, tkl.ObsTime()))
                    d = c.coord.distance2DTo(p2)
        else:
            noeudFin = tkl.Node(cptNode, p2)
            cptNode += 1


        #
        '''
        existant = False
        for edge2 in network:
            if edge.id == edge2.id:
                continue
            track2 = edge2.geom
            track1 = edge.geom
            mode=tkl.MODE_COMPARISON_POINTWISE
            p=1
            dim=2
            d = tkl.compare(track1, track2, mode, p, dim)
            if d < 0.1:
                existant = True
            else:
                t3 = track2.reverse()
                d = tkl.compare(track1, t3, mode, p, dim)
                if d < 0.1:
                    existant = True

        if not existant:
        '''
        network.addEdge(edge, noeudIni, noeudFin)


    return network





    if len(noeudsElimines) > 0:
        # print (NoeudsASupprimer)
        for nid in noeudsElimines:
            node = network.NODES[nid]
            network.removeNode(node)





def selectNodes(network, node, distance):
    """Selection des autres noeuds dans le cercle dont node.coord est le centre,
    de rayon distance

    :param node: le centre du cercle de recherche.
    :param distance: le rayon du cercle de recherche.

    :return: tableau de NODES liste des noeuds dans le cercle
    """
    NODES = []

    if network.spatial_index is None:
        for key in network.getIndexNodes():
            n = network.NODES[key]
            if n.coord.distance2DTo(node.coord) <= distance:
                NODES.append(n)
    else:
        print ('INDEX !!!!!!')
        vicinity_edges = network.spatial_index.neighborhood(node.coord, unit=1)
        for e in vicinity_edges:
            source = network.EDGES[network.getEdgeId(e)].source
            target = network.EDGES[network.getEdgeId(e)].target
            if source.coord.distance2DTo(node.coord) <= distance:
                NODES.append(source)
            if target.coord.distance2DTo(node.coord) <= distance:
                NODES.append(target)

    return NODES


