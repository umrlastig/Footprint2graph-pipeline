# -*- coding: utf-8 -*-

import unittest

import tracklib as tkl

class TestZone1(unittest.TestCase):
    


    def setUp (self):
        #RESPATH = r'/home/md_vandamme/4_RESEAU/ZTEMPZ1/'
        pass

        
    
    def testPipeline(self):
        print ("OK")
        fmt = tkl.TrackFormat({'ext': 'CSV',
                               'srid': 'ENU',
                               'id_E': 1, 'id_N': 0, 'id_U': 3, 'id_T': 2,
                               'time_fmt': '2D/2M/4Y 2h:2m:2s',
                               'separator': ';',
                               'header': 0,
                               'cmt': '#',
                               'read_all': True})
        self.assertTrue("1=1", "premier test")






if __name__ == '__main__':
    suite = unittest.TestSuite()

    suite.addTest(TestZone1("testPipeline"))

    runner = unittest.TextTestRunner()
    runner.run(suite)
