'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''
import unittest
import xml.etree.ElementTree as ET
from rsMap3D.datasource.InstForXrayutilitiesReader import \
    InstForXrayutilitiesReader
from rsMap3D.exception.rsmap3dexception import InstConfigException
import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))

PROBLEM_FILES_DIR = os.path.join(THIS_DIR,  
                                 '../../resources/problemFilesForTesting/')

class Test(unittest.TestCase):


    def setUp(self):
        self.config = InstForXrayutilitiesReader( \
                 os.path.join(THIS_DIR, 
                              '../../resources/33BM-instForXrayutilities.xml'))
        self.config2 = InstForXrayutilitiesReader( \
                 os.path.join(THIS_DIR, 
                      '../../resources/33BM-instForXrayutilities-noMonitor.xml'))
        self.config3 = InstForXrayutilitiesReader( \
                 os.path.join(THIS_DIR, 
                      '../../resources/33BM-instForXrayutilities-noCircles.xml'))
        self.config4 = InstForXrayutilitiesReader( \
                 os.path.join(THIS_DIR, 
                      '../../resources/33BM-instForXrayutilities-noScalingFactor.xml'))
        self.config5 = InstForXrayutilitiesReader( \
                 os.path.join(THIS_DIR, 
                      '../../resources/13BMC_Instrument.xml'))
        self.config6 = InstForXrayutilitiesReader( \
                 os.path.join(THIS_DIR, 
                      '../../resources/7IDC-instForXrayutilitiesFixWrongValuesChiPhi.xml'))

    def tearDown(self):
        pass


    def testGetAxisNumber(self):
        sampleCircles = self.config.getSampleCircles()
        axisList = []
        for circle in sampleCircles:
            axisList.append(self.config.getCircleAxisNumber(circle))
        axisList.sort()
        refList = [1,2,3]
        self.assertEqual(axisList, refList, "GetAxisList" + \
                         str(axisList) + " vs " + str(refList))
        
    def testGetAxisNumberNoAxis(self):
        config = InstForXrayutilitiesReader( PROBLEM_FILES_DIR + \
                      'instNoSampleAxisNumber.xml')
        sampleCircles = config.getSampleCircles()
        for circle in sampleCircles:
            self.assertRaises(InstConfigException, \
                              config.getCircleAxisNumber, circle)

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

    def testGetMonitorNameEmptyName(self):
        config = InstForXrayutilitiesReader( PROBLEM_FILES_DIR + \
                      'instEmptyMonitorAndFilter.xml')
        monitorName = config.getMonitorName()
        self.assertEquals(monitorName, None, 
                          "testGetMonitorNameEmptyName: expecting: " +\
                          str(None) + \
                          ", got: " + \
                          str(monitorName) )

    def testGetMonitorNameWhiteSpace(self):
        config = InstForXrayutilitiesReader( PROBLEM_FILES_DIR + \
                      'instWhiteSpaceMonitorAndFilter.xml')
        monitorName = config.getMonitorName()
        self.assertEquals(monitorName, None, 
                          "testGetMonitorNameWhiteSpace: expecting: " +\
                          str(None) + \
                          ", got: " + \
                          str(monitorName) )

    def testGetMonitorScaleFactorNoScaleFactor(self):
        monitorName = self.config4.getMonitorScaleFactor()
        self.assertEquals(monitorName, 1, "getMonitorScaleFactorNoScaleFactor")

    def testGetFiterName(self):
        filterName = self.config.getFilterName()
        self.assertEqual(filterName, "trans", "getFilterName")

    def testGetFilterNameNoMonitor(self):
        filterName = self.config2.getFilterName()
        self.assertEquals(filterName, None, "getFilterNameNoMonitor")

    def testGetFilterNameEmptyName(self):
        config = InstForXrayutilitiesReader( PROBLEM_FILES_DIR + \
                      'instEmptyMonitorAndFilter.xml')
        filterName = config.getFilterName()
        self.assertEquals(filterName, None, 
                          "getFilterNameEmptyName: expecting: " +\
                          str(None) + \
                          ", got: " + \
                          str(filterName) )

    def testGetFilterNameWhiteSpace(self):
        config = InstForXrayutilitiesReader( PROBLEM_FILES_DIR + \
                      'instWhiteSpaceMonitorAndFilter.xml')
        filterName = config.getFilterName()
        self.assertEquals(filterName, None, 
                          "getFilterNameWhiteSpace: expecting: " +\
                          str(None) + \
                          ", got: " + \
                          str(filterName) )

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
        self.assertRaises(InstConfigException, self.config3.getDetectorCircles)
        
    def testGetInplaneReferenceDirectionNoDirection(self):
        config = InstForXrayutilitiesReader( PROBLEM_FILES_DIR + \
                      'instNoReferenceDirections.xml')
        self.assertRaises(InstConfigException, \
                          config.getInplaneReferenceDirection)
        
    def testGetInplaneReferenceDirectionValueNotANumber(self):
        config = InstForXrayutilitiesReader( PROBLEM_FILES_DIR + \
                      'instAxisValuesNotANumber.xml')
        self.assertRaises(InstConfigException, 
                          config.getInplaneReferenceDirection)
        
    def testGetPrimaryBeamDirectionNoDirection(self):
        config = InstForXrayutilitiesReader( PROBLEM_FILES_DIR + \
                      'instNoReferenceDirections.xml')
        self.assertRaises(InstConfigException, \
                          config.getPrimaryBeamDirection)
        
    def testGetPrimaryBeamDirectionNoAxes(self):
        config = InstForXrayutilitiesReader( PROBLEM_FILES_DIR + \
                      'instNoAxesOnReferenceAxes.xml')
        self.assertRaises(InstConfigException, \
                          config.getPrimaryBeamDirection)
        
    def testGetPrimaryBeamDirectionValueNotANumber(self):
        config = InstForXrayutilitiesReader( PROBLEM_FILES_DIR + \
                      'instAxisValuesNotANumber.xml')
        self.assertRaises(InstConfigException, 
                          config.getPrimaryBeamDirection)
        
    def testGetProjectionDirection(self):
        direction = self.config.getProjectionDirection()
        refDirection = [0, 0, 1]
        self.assertEqual(direction, refDirection, \
                         "getProjectionDirection " + str(direction) + " vs "\
                         + str(refDirection) )
        
    def testGetProjectionDirection2(self):
        direction = self.config5.getProjectionDirection()
        refDirection = [0, 0, -1]
        self.assertEqual(direction, refDirection, \
                         "getProjectionDirection " + str(direction) + " vs "\
                         + str(refDirection) )

    def testGetProjectionDirectionNoDirection(self):
        self.assertRaises(InstConfigException, 
                          self.config3.getProjectionDirection)
        
    def testGetProjectionDirectionValueNotANumber(self):
        config = InstForXrayutilitiesReader( PROBLEM_FILES_DIR + \
                      'instAxisValuesNotANumber.xml')
        self.assertRaises(InstConfigException, 
                          config.getProjectionDirection)
        
    def testGetSampleCircleDirections(self):
        directions = self.config.getSampleCircleDirections()
        refDirections = ["z-", "y+", "z-"]
        self.assertEqual(directions, refDirections, 
                         "getSampleCircleDirections " + \
                         str(directions) + " vs " +
                         str(refDirections))

    def testGetSampleCircleDirectionsNoAxisNumber(self):
        config = InstForXrayutilitiesReader( PROBLEM_FILES_DIR + \
                      'instNoSampleAxisNumber.xml')
        self.assertRaises(InstConfigException, \
                         config.getSampleCircleDirections)
        
    def testGetSampleCircleNames(self):
        names = self.config.getSampleCircleNames()
        refNames = ["theta", "chi", "phi"]
        self.assertEqual(names, refNames, 
                         "getSampleCircleNames " + \
                         str(names) + " vs " +
                         str(refNames))

    def testGetSampleCircleNamesNoAxisNumber(self):
        config = InstForXrayutilitiesReader( PROBLEM_FILES_DIR + \
                      'instNoSampleAxisNumber.xml')
        self.assertRaises(InstConfigException, \
                         config.getSampleCircleNames)
        
    def testGetSampleCircleNamesNoMotorName(self):
        config = InstForXrayutilitiesReader( PROBLEM_FILES_DIR + \
                      'instNoSampleAxisMotorName.xml')
        self.assertRaises(InstConfigException, \
                         config.getSampleCircleNames)
        
    def testGetSampleCircleDirectionsNoAxisDirection(self):
        config = InstForXrayutilitiesReader( PROBLEM_FILES_DIR + \
                      'instNoSampleAxisDirection.xml')
        self.assertRaises(InstConfigException, \
                         config.getSampleCircleDirections)
        
    def testGetSampleCircles(self):
        circles = self.config.getSampleCircles()
        self.assertEqual(len(circles), 3, "getSampleCircles")
        
    def testGetSampleCirclesNoCircle(self):
        self.assertRaises(InstConfigException, self.config3.getSampleCircles)
        
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
        self.assertRaises(InstConfigException, 
                          self.config4.getSampleAngleMappingCalcOnScannedRef)
        
    def testGetSampleAngleMappingPrimaryAngles(self):
        angles = self.config5.getSampleAngleMappingPrimaryAngles()
        self.assertEquals(angles, \
                          [2,3,4], \
                          "getSampleAngleMappingPrimaryAngles: " + str(angles))

    def testGetSampleAngleMappingParameter(self):
        param = self.config5.getSampleAngleMappingParameter('kappa')
        kappa = 49.9945
        self.assertEqual(param, str(kappa), \
                         "testGetSampleAngleMappingParameter Expecting: " + \
                         str(kappa) + \
                         " got back: " + \
                         str(param))
        param = self.config5.getSampleAngleMappingParameter('kappaInverted')
        kappaInverted = True
        self.assertEqual(param, str(kappaInverted), \
                         "testGetSampleAngleMappingParameter Expecting: " + \
                         str(kappaInverted) + \
                         " got back: " + \
                         str(param))
        
    def testGetSampleAngleMappingFunctionPrimaryAnglesNoMap(self):
        self.assertRaises(InstConfigException, 
                          self.config4.getSampleAngleMappingPrimaryAngles)
        
    def testGetSampleAngleMappingRefereceAngles(self):
        angles = self.config5.getSampleAngleMappingReferenceAngles()
        self.assertEquals(angles, \
                          ['keta', "kap", "kphi"], \
                          "getSampleAngleMappingReferenceAngles: " + str(angles))

    def testGetSampleAngleMappingFunctionReferenceAnglesNoMap(self):
        self.assertRaises(InstConfigException, 
                          self.config4.getSampleAngleMappingReferenceAngles)

    def testGetSampleSurfaceNormalDirectionNoDirection(self):
        config = InstForXrayutilitiesReader( PROBLEM_FILES_DIR + \
                      'instNoReferenceDirections.xml')
        self.assertRaises(InstConfigException, \
                          config.getSampleSurfaceNormalDirection)
        
    def testGetSampleSurfaceNormalDirectionValueNotANumber(self):
        config = InstForXrayutilitiesReader( PROBLEM_FILES_DIR + \
                      'instAxisValuesNotANumber.xml')
        self.assertRaises(InstConfigException, 
                          config.getSampleSurfaceNormalDirection)
 
#     def testGetSampleAngleMappingPrimaryAngleAttrib(self):
#         config = self.config6
#         replaceVal = config.getSampleAngleMappingPrimaryAngleAttrib('2', "replaceValue")
#         self.assertEqual(replaceVal,  
#                          '45.0', 
#                          config.getSampleAngleMappingPrimaryAngleAttrib.__name__)
#         replaceVal = config.getSampleAngleMappingPrimaryAngleAttrib('3', "replaceValue")
#         self.assertEqual(replaceVal,  
#                          '32.0', 
#                          config.getSampleAngleMappingPrimaryAngleAttrib.__name__)
#         self.assertRaises(AttributeError,config.getSampleAngleMappingPrimaryAngleAttrib,('1', "replaceValue"))
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testGetMonitorName']
    unittest.main()
    
    
