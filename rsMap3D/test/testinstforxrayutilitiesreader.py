'''
Created on Mar 28, 2014

@author: hammonds
'''
import unittest
from rsMap3D.datasource.InstForXrayutilitiesReader import \
    InstForXrayutilitiesReader

class Test(unittest.TestCase):


    def setUp(self):
        self.config = InstForXrayutilitiesReader( \
                     '../resources/33BM-instForXrayutilities.xml')
        self.config2 = InstForXrayutilitiesReader( \
                      '../resources/33BM-instForXrayutilities-noMonitor.xml')
        self.config3 = InstForXrayutilitiesReader( \
                      '../resources/33BM-instForXrayutilities-noCircles.xml')

    def tearDown(self):
        pass


    def testGetMonitorName(self):
        monitorName = self.config.getMonitorName()
        self.assertEquals(monitorName, "I0", "getMonitorName")

    def testGetMonitorNameNoMonitor(self):
        monitorName = self.config2.getMonitorName()
        self.assertEquals(monitorName, None, "getMonitorNameNoMonitor")

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
    
    
