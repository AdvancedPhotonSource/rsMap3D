'''
Created on May 28, 2014

@author: hammonds
'''
import unittest
from rsMap3D.datasource.pilatusbadpixelfile import PilatusBadPixelFile


class Test(unittest.TestCase):


    def setUp(self):
        self.a = PilatusBadPixelFile("../../resources/badpixels.txt")
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