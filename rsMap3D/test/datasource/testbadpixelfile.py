'''
Created on May 28, 2014

@author: hammonds
'''
import unittest
from rsMap3D.datasource.pilatusbadpixelfile import PilatusBadPixelFile
import os

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

class Test(unittest.TestCase):



    def setUp(self):
        fileName = os.path.join(THIS_DIR,
                               "../../resources/badpixels.txt") 
        self.a = PilatusBadPixelFile(fileName)
        #


    def tearDown(self):
        pass


    def testGetNumPixels(self):
        numPixels = self.a.getNumPixels()
        self.assertEqual(numPixels, 29, "getNumPixels")

    def testGetBadPixels(self):
        bp = self.a.getBadPixels()
        badLoc = (309,79)
        self.assertEqual(bp[12].getBadLocation(), 
                         badLoc, \
                         "BadLocation: expected " + \
                         str(badLoc) + \
                         " got : " + \
                         str(bp[12].getBadLocation()))
        replaceLoc = (305,79)
        self.assertEqual(bp[12].getReplacementLocation(), 
                         replaceLoc, \
                         "BadLocation: expected " + \
                         str(replaceLoc) + \
                         " got : " + \
                         str(bp[12].getReplacementLocation()))
                         

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()