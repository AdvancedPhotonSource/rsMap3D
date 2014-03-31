'''
Created on Mar 31, 2014

@author: hammonds
'''
import unittest
from rsMap3D.datasource.Sector33SpecDataSource import Sector33SpecDataSource

PROJECT_DIR = "../../resources/spec"
PROJECT_NAME = "CB_140303A_1"
PROJECT_EXT = ".spec"
INST_CONFIG_1 = "../../resources/33BM-instForXrayutilities.xml"
DET_CONFIG = "../../resources/33bmDetectorGeometry.xml"


class Test(unittest.TestCase):


    def setUp(self):
        self.dataSource = Sector33SpecDataSource(PROJECT_DIR, \
                                                 PROJECT_NAME, \
                                                 PROJECT_EXT, \
                                                 INST_CONFIG_1, \
                                                 DET_CONFIG) 
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