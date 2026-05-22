# -*- coding: utf-8 -*-

import unittest



class TestZone1(unittest.TestCase):
    


    def setUp (self):
        pass

        
    
    def testCircle(self):
        print ("OK")





if __name__ == '__main__':
    suite = unittest.TestSuite()

    suite.addTest(TestZone1("testCircle"))

    runner = unittest.TextTestRunner()
    runner.run(suite)
