'''
Created on Sep 4, 2014

@author: hammonds
'''
import unittest
from rsMap3D.datasource.DetectorGeometry.detectorgeometrybase import DetectorGeometryBase
from rsMap3D.datasource.DetectorGeometry.detectorgeometryforescan import DetectorGeometryForEScan
from rsMap3D.exception.rsmap3dexception import DetectorConfigException
import os
import logging
import logging.handlers
import logging.config
from rsMap3D.config.rsmap3dlogging import LOGGER_NAME


THIS_DIR = os.path.dirname(os.path.abspath(__file__))

configDir = os.path.join(THIS_DIR, '../../../resources/config')
logConfigFile = os.path.join(configDir, LOGGER_NAME + 'Log.test.config')
print logConfigFile
logging.config.fileConfig(logConfigFile)
logger = logging.getLogger(LOGGER_NAME)


FILE_BASE_DIR = os.path.join(THIS_DIR, '../../../resources/34-id-escan/')
DETECTOR_NAME1 ='PE1621 723-3335'
DETECTOR_NAME2 ='PE0820 763-1807'
DETECTOR_NAME3 ='PE0820 763-1850'
DETECTOR_ROTATION1 = [-1.2016145, -1.21287345, -1.21811239]
DETECTOR_ROTATION2 = [-1.76567241, -0.73301327, -1.76022613]
DETECTOR_ROTATION3 = [-0.61389068, -1.50215054, -0.62140802]
DETECTOR_TRANSLATION1 = [25.316, -2.373, 510.741]
DETECTOR_TRANSLATION2 = [-142.590, -3.069, 411.840]
DETECTOR_TRANSLATION3 = [-143.033, -3.062, 417.152]
DUMMY_DETECTOR = "DUMMY"
SMALL_DETECTOR_PIXELS = [1024,1024]
BIG_DETECTOR_PIXELS = [2048,2048]
SMALL_DETECTOR_SIZE = [204.8, 204.8]
BIG_DETECTOR_SIZE = [409.6, 409.6]

NORMAL_FILE = FILE_BASE_DIR + 'geoN_for_Ptdots.xml'

class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testOpenFile(self):
        config = DetectorGeometryForEScan(NORMAL_FILE)
        if config <> None:
            pass
        else:
            self.assertFail()
            
    def testGetDetectors(self):
        config = DetectorGeometryForEScan(NORMAL_FILE)
        dets = config.getDetectors()
        self.assertNotEqual(dets, None, "Found no detectors")
        
    def testGetDetectorByID(self):
        config = DetectorGeometryForEScan(NORMAL_FILE)
        det1 = config.getDetectorById(DETECTOR_NAME1)
        self.assertNotEqual(det1, None, "Trouble finding detector 1")
        self.assertEqual(config.getDetectorID(det1), DETECTOR_NAME1, \
                         "Detector 1 returnend the wrong name")
        det2 = config.getDetectorById(DETECTOR_NAME2)
        self.assertNotEqual(det2, None, "Trouble finding detector 2")
        self.assertEqual(config.getDetectorID(det2), DETECTOR_NAME2, \
                         "Detector 2 returnend the wrong name")
        det3 = config.getDetectorById(DETECTOR_NAME3)
        self.assertNotEqual(det3, None, "Trouble finding detector 3")
        self.assertEqual(config.getDetectorID(det3), DETECTOR_NAME3, \
                         "Detector 3 returnend the wrong name")
        self.assertRaises(DetectorConfigException, \
            config.getDetectorById, DUMMY_DETECTOR)

    def testGetNPixels(self):
        config = DetectorGeometryForEScan(NORMAL_FILE)
        det1 = config.getDetectorById(DETECTOR_NAME1)
        self.assertNotEqual(det1, None, "Trouble finding detector 1")
        self.assertEqual(config.getNpixels(det1), BIG_DETECTOR_PIXELS, \
                         "Detector 1 returnend the number of pixels" + \
                         str(config.getNpixels(det1)))
        det2 = config.getDetectorById(DETECTOR_NAME2)
        self.assertNotEqual(det2, None, "Trouble finding detector 2")
        self.assertEqual(config.getNpixels(det2), SMALL_DETECTOR_PIXELS, \
                         "Detector 2 returnend the number of pixels" + \
                         str(config.getNpixels(det2)))
        det3 = config.getDetectorById(DETECTOR_NAME3)
        self.assertNotEqual(det3, None, "Trouble finding detector 3")
        self.assertEqual(config.getNpixels(det3), SMALL_DETECTOR_PIXELS, \
                         "Detector 3 returnend the wrong number of pixels" + \
                         str(config.getNpixels(det3)))
        self.assertRaises(DetectorConfigException, \
            config.getDetectorById, DUMMY_DETECTOR)

    def testGetSize(self):
        config = DetectorGeometryForEScan(NORMAL_FILE)
        det1 = config.getDetectorById(DETECTOR_NAME1)
        self.assertNotEqual(det1, None, "Trouble finding detector 1")
        self.assertEqual(config.getSize(det1), BIG_DETECTOR_SIZE, \
                         "Detector 1 returnend the wrong size" + \
                         str(config.getSize(det1)))
        det2 = config.getDetectorById(DETECTOR_NAME2)
        self.assertNotEqual(det2, None, "Trouble finding detector 2")
        self.assertEqual(config.getSize(det2), SMALL_DETECTOR_SIZE, \
                         "Detector 2 returnend the wrong size" + \
                         str(config.getSize(det2)))
        det3 = config.getDetectorById(DETECTOR_NAME3)
        self.assertNotEqual(det3, None, "Trouble finding detector 3")
        self.assertEqual(config.getSize(det3), SMALL_DETECTOR_SIZE, \
                         "Detector 3 returnend the wrong size" + \
                         str(config.getSize(det3)))
        self.assertRaises(DetectorConfigException, \
            config.getDetectorById, DUMMY_DETECTOR)

    def testGetTranslation(self):
        config = DetectorGeometryForEScan(NORMAL_FILE)
        det1 = config.getDetectorById(DETECTOR_NAME1)
        self.assertNotEqual(det1, None, "Trouble finding detector 1")
        self.assertEqual(config.getTranslation(det1), DETECTOR_TRANSLATION1, \
                         "Detector 1 returnend the wrong translation" + \
                         str(config.getTranslation(det1)))
        det2 = config.getDetectorById(DETECTOR_NAME2)
        self.assertNotEqual(det2, None, "Trouble finding detector 2")
        self.assertEqual(config.getTranslation(det2), DETECTOR_TRANSLATION2, \
                         "Detector 2 returnend the wrong translation" + \
                         str(config.getTranslation(det2)))
        det3 = config.getDetectorById(DETECTOR_NAME3)
        self.assertNotEqual(det3, None, "Trouble finding detector 3")
        self.assertEqual(config.getTranslation(det3), DETECTOR_TRANSLATION3, \
                         "Detector 3 returnend the wrong TRANSLATION" + \
                         str(config.getTranslation(det3)))
        self.assertRaises(DetectorConfigException, \
            config.getDetectorById, DUMMY_DETECTOR)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()