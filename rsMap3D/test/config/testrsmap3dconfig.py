'''
Created on May 22, 2014

@author: hammonds
'''
import os
import unittest
from rsMap3D.config.rsmap3dconfig import RSMap3DConfig
from rsMap3D.exception.rsmap3dexception import RSMap3DException

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
BAD_FILE_DIRECTORY = os.path.join(THIS_DIR,
                                  "../../resources/problemFilesForTesting/")
GOOD_FILE_DIRECTORY = os.path.join(THIS_DIR, "../../resources/")
class Test(unittest.TestCase):


    def setUp(self):
        print(THIS_DIR)
        print(os.getcwd())
        self.config = RSMap3DConfig(fileName=GOOD_FILE_DIRECTORY + ".rsMap3D")


    def tearDown(self):
        pass


    def testGetMaxImageMemory(self):
        maxMem = self.config.getMaxImageMemory()
        self.assertEqual(maxMem, 100000000, "testGetMaxImageMemory")

    def testGetMaxImageMemoryNoMaxImageMem(self):
        config2 = RSMap3DConfig(fileName= \
            BAD_FILE_DIRECTORY + "rsmapConfigNoMaxImageMemory.xml")
        self.assertRaises(RSMap3DException, config2.getMaxImageMemory)

    def testGetMaxImageMemoryEmptyMaxImageMem(self):
        config3 = RSMap3DConfig(fileName= \
            BAD_FILE_DIRECTORY + "rsmapConfigEmptyMaxImageMemory.xml")
        self.assertRaises(RSMap3DException, config3.getMaxImageMemory)
    def testGetMaxImageMemoryBadCharacters(self):
        config4 = RSMap3DConfig(fileName= \
            BAD_FILE_DIRECTORY + "rsmapConfigMaxImageMemBadCharacters.xml")
        self.assertRaises(RSMap3DException, config4.getMaxImageMemory)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()