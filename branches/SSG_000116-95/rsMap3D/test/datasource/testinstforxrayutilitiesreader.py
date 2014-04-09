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
        self.config5 = InstForXrayutilitiesReader( \
                      '../../resources/13BMC_Instrument.xml')

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
        
    def testGetSampleAngleMappingFunctionName(self):
        name = self.config5.getSampleAngleMappingFunctionName()
        self.assertEquals(name, \
                          "_calc_eulerian_from_kappa", \
                          "getSampleAngleMappingFunction: " + name)
        
    def testGetSampleAngleMappingFunctionNameNoMap(self):
        name = self.config4.getSampleAngleMappingFunctionName()
        self.assertEquals(name, \
                          "", \
                          "getSampleAngleMappingFunction: " + name)

    def testGetSampleAngleMappingCalcOnScannedRef(self):
        calc = self.config5.getSampleAngleMappingCalcOnScannedRef()
        self.assertEquals(calc, \
                          True, \
                          "getSampleAngleMappingCalcOnScannedRef: " + str(calc))
        
    def testGetSampleAngleMappingFunctionCalcOnScannedRefNoMap(self):
        self.assertRaises(ValueError, 
                          self.config4.getSampleAngleMappingCalcOnScannedRef)
        
    def testGetSampleAngleMappingPrimaryAngles(self):
        angles = self.config5.getSampleAngleMappingPrimaryAngles()
        self.assertEquals(angles, \
                          [2,3,4], \
                          "getSampleAngleMappingPrimaryAngles: " + str(angles))

    def testGetSampleAngleMappingFunctionPrimaryAnglesNoMap(self):
        self.assertRaises(ValueError, 
                          self.config4.getSampleAngleMappingPrimaryAngles)
        
    def testGetSampleAngleMappingRefereceAngles(self):
        angles = self.config5.getSampleAngleMappingReferenceAngles()
        self.assertEquals(angles, \
                          {1:'keta', 2:"kap", 3:"kphi"}, \
                          "getSampleAngleMappingReferenceAngles: " + str(angles))

    def testGetSampleAngleMappingFunctionReferenceAnglesNoMap(self):
        self.assertRaises(ValueError, 
                          self.config4.getSampleAngleMappingReferenceAngles)
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testGetMonitorName']
    unittest.main()
    
    
