'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''
import unittest
from rsMap3D.datasource.AbstractXrayUtilitiesDataSource import \
    AbstractXrayutilitiesDataSource

SPEC_FILE = "../../resources/spec/CB_140303A_1.spec"
INST_CONFIG_1 = "../../resources/33BM-instForXrayutilities.xml"
DET_CONFIG = "../../resources/33BMDetectorGeometry.xml"

class Test(unittest.TestCase):


    def setUp(self):
        self.dataSource = TestDataSource(SPEC_FILE, \
                                         INST_CONFIG_1, \
                                         DET_CONFIG) 
                                                    


    def tearDown(self):
        pass


    def testGetMonitorName(self):
        monitorName = self.dataSource.getMonitorName()
        self.assertEqual(monitorName, None, "getMonitorName")

    def testGetMonitorScaleFactor(self):
        scaleFactor = self.dataSource.getMonitorScaleFactor()
        self.assertEqual(scaleFactor, 1, "getMonitorScaleFactor")

    def testGetFilterName(self):
        filterName = self.dataSource.getFilterName()
        self.assertEqual(filterName, None, "getFilterName")

    def testGetFilterScaleFactor(self):
        scaleFactor = self.dataSource.getFilterScaleFactor()
        self.assertEqual(scaleFactor, 1, "getFilterScaleFactor")


class TestDataSource(AbstractXrayutilitiesDataSource):
    def loadSource(self):
        return
        
    def getImage(self):
        return
    
    def getReferenceNames(self):
        return AbstractXrayutilitiesDataSource.getReferenceNames(self)
    
    def getReferenceValues(self):
        return AbstractXrayutilitiesDataSource.getReferenceValues(self)
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()