# -*- coding: utf-8 -*-

import unittest

import os
import tracklib as tkl

from footprint2graph import prepareEnv, setupEnv
from footprint2graph import run_iteration


class TestZone1(unittest.TestCase):
    '''
    Test complet sur un jeu de traces simulées à partir d’un réseau.
    C'est le code du notebook dans la documentation
    '''


    def setUp (self):
        resource_path = os.path.join(os.path.split(__file__)[0], "..")

        self.RESPATH = os.path.join(resource_path, './test/result1/')

        prepareEnv(self.RESPATH)

        iteration_index = 1
        setupEnv(self.RESPATH, iteration_index)

        #  Import du réseau
        netpath = os.path.join(resource_path, 'data/network2.csv')
        fmt = tkl.NetworkFormat({
               "pos_edge_id": 1,
               "pos_source": 2,
               "pos_target": 3,
               "pos_wkt": 0,
               "srid": "ENU",
               "separator": ";",
               "header": 1})

        self.network = tkl.NetworkReader.readFromFile(netpath, fmt, verbose=False)

        # Génération des traces réalistes synthétiques
        tkl.stochastics.seed(333)
        noiser = tkl.NoiseProcess(amps=2.5, kernels=tkl.ExponentialKernel(80))


        # generate simulated trajectories from the network
        collection = tkl.generateTracksOnNetwork(self.network, N=100, p_round_trip=0.05, p_cplx_trip=0.10, resolution=1, noiser=noiser)
        # add 3 attributes
        for idx, track in enumerate(collection):
            track.createAnalyticalFeature('TID', idx+1)
            track.createAnalyticalFeature('MID', idx+1)

        self.collection = collection


    
    def testPipeline(self):

        self.assertEqual(len(self.network.EDGES), 7, 'Number of edges=')
        self.assertEqual(len(self.network.NODES), 8 ,'Number of nodes')


        pipeline_idx = 1
        run_iteration(pipeline_idx, self.RESPATH, self.collection)



        # =====================================================================
        # On teste quelques résultats intermédiaires

        # nombre de traces en point d'entrée
        fmt = tkl.TrackFormat({'ext': 'CSV',
                               'srid': 'ENU',
                               'id_E': 1,'id_N': 0, 'id_U': 3,'id_T': 2,
                               'separator': ';',
                               'header': 1,
                               'read_all': True})
        resampledtracespath = self.RESPATH + 'resample_grid' + '/'
        tracks = tkl.TrackReader.readFromFile(resampledtracespath, fmt, verbose=False)
        self.assertEqual(len(tracks), 91, 'Number of tracks after segmentation=')






if __name__ == '__main__':
    suite = unittest.TestSuite()

    suite.addTest(TestZone1("testPipeline"))

    runner = unittest.TextTestRunner()
    runner.run(suite)
