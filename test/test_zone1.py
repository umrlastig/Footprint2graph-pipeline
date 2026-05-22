# -*- coding: utf-8 -*-

import unittest



class TestZone1(unittest.TestCase):
    


    def setUp (self):
        #RESPATH = r'/home/md_vandamme/4_RESEAU/ZTEMPZ1/'
        pass

        
    
    def testCircle(self):
        self.assertTrue("1=1", "premier test")
        print ("OK")





if __name__ == '__main__':
    suite = unittest.TestSuite()

    suite.addTest(TestZone1("testCircle"))

    runner = unittest.TextTestRunner()
    runner.run(suite)
