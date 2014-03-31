'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''
import unittest
from rsMap3D.datasource.InstForXrayutilitiesReader import \
    InstForXrayutilitiesReader

class Test(unittest.TestCase):


    def setUp(self):
        self.config = InstForXrayutilitiesReader( \
                     '../../resources/33BM-instForXrayutilities.xml')
        self.config2 = InstForXrayutilitiesReader( \
                      '../../resources/33BM-instForXrayutilities-noMonitor.xml')
        self.config3 = InstForXrayutilitiesReader( \
                      '../../resources/33BM-instForXrayutilities-noCircles.xml')
        self.config4 = InstForXrayutilitiesReader( \
                      '../../resources/33BM-instForXrayutilities-noScalingFactor.xml')

    def tearDown(self):
        pass


    def testGetMonitorName(self):
        monitorName = self.config.getMonitorName()
        self.assertEquals(monitorName, "I0", "getMonitorName")

    def testGetMonitorNameNoMonitor(self):
        monitorName = self.config2.getMonitorName()
        self.assertEquals(monitorName, None, "getMonitorNameNoMonitor")

    def testGetMonitorScaleFactor(self):
        scaleFactor = self.config.getMonitorScaleFactor()
        self.assertEquals(scaleFactor, 20000, "getMonitorScaleFactor")

    def testGetMonitorScaleFactorNoMonitor(self):
        monitorName = self.config2.getMonitorScaleFactor()
        self.assertEquals(monitorName, 1, "getMonitorScaleFactorNoMonitor")

    def testGetMonitorScaleFactorNoScaleFactor(self):
        monitorName = self.config4.getMonitorScaleFactor()
        self.assertEquals(monitorName, 1, "getMonitorScaleFactorNoScaleFactor")

    def testGetFiterName(self):
        filterName = self.config.getFilterName()
        self.assertEqual(filterName, "trans", "getFilterName")

    def testGetFilterNameNoMonitor(self):
        filterName = self.config2.getFilterName()
        self.assertEquals(filterName, None, "getFilterNameNoMonitor")

    def testGetFilterScaleFactor(self):
        scaleFactor = self.config.getFilterScaleFactor()
        self.assertEquals(scaleFactor, 1000000, "getFilterScaleFactor")

    def testGetFilterScaleFactorNoFilter(self):
        scaleFactor = self.config2.getFilterScaleFactor()
        self.assertEquals(scaleFactor, 1, "getFilterScaleFactorNoFilter")

    def testGetFilterScaleFactorNoScaleFactor(self):
        scaleFactor = self.config4.getFilterScaleFactor()
        self.assertEquals(scaleFactor, 1, "getFilterScaleFactorNoScaleFactor")

    def testGetDetectorCircles(self):
        circles = self.config.getDetectorCircles()
        self.assertEqual(len(circles), 1, "getDetectorCircles")
        
    def testGetDetectorCirclesNoCircle(self):
        self.assertRaises(IOError, self.config3.getDetectorCircles)
        
    def testGetSampleCircles(self):
        circles = self.config.getSampleCircles()
        self.assertEqual(len(circles), 3, "getSampleCircles")
        
    def testGetSampleCirclesNoCircle(self):
        self.assertRaises(IOError, self.config3.getSampleCircles)
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testGetMonitorName']
    unittest.main()
    
    
