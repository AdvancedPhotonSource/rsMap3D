'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''
import unittest
from rsMap3D.datasource.Sector33SpecDataSource import Sector33SpecDataSource
import os

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(THIS_DIR, "../../resources/spec")
PROJECT_NAME = "CB_140303A_1"
PROJECT_EXT = ".spec"
INST_CONFIG_1 = os.path.join(THIS_DIR, 
                             "../../resources/33BM-instForXrayutilities.xml")
DET_CONFIG = os.path.join(THIS_DIR, "../../resources/33bmDetectorGeometry.xml")
CURRENT_DETECTOR = "Pilatus"

class Test(unittest.TestCase):


    def setUp(self):
        self.dataSource = Sector33SpecDataSource(PROJECT_DIR, \
                                                 PROJECT_NAME, \
                                                 PROJECT_EXT, \
                                                 INST_CONFIG_1, \
                                                 DET_CONFIG) 
        self.dataSource.setCurrentDetector(CURRENT_DETECTOR)
        self.dataSource.loadSource()


    def tearDown(self):
        pass


    def testGetMonitorName(self):
        monitorName = self.dataSource.getMonitorName()
        self.assertEqual(monitorName, "I0", "getMonitorName")

    def testGetMonitorScaleFactor(self):
        scaleFactor = self.dataSource.getMonitorScaleFactor()
        self.assertEqual(scaleFactor, 20000, "getMonitorScaleFactor")

    def testGetFilterName(self):
        filterName = self.dataSource.getFilterName()
        self.assertEqual(filterName, "trans", "getFilterName")

    def testGetFilterScaleFactor(self):
        scaleFactor = self.dataSource.getFilterScaleFactor()
        self.assertEqual(scaleFactor, 1000000, "getFilterScaleFactor")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()