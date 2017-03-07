'''
Created on Apr 24, 2014

@author: hammonds
'''
import unittest
from rsMap3D.datasource.DetectorGeometryForXrayutilitiesReader import DetectorGeometryForXrayutilitiesReader
from rsMap3D.exception.rsmap3dexception import DetectorConfigException
import os

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_BASE_DIR = os.path.join(THIS_DIR, '../../resources/')
BAD_FILE_DIR = FILE_BASE_DIR + 'problemFilesForTesting/'
BAD_FILE_NO_DETECTOR_LIST = BAD_FILE_DIR + 'detectorGeometryNoDetectorList.xml'
BAD_FILE_NO_DETECTOR = BAD_FILE_DIR + 'detectorGeometryNoDetector.xml'
DETECTOR_NAME = 'Pilatus'
GOOD_FILE_NAME = FILE_BASE_DIR + '33bmDetectorGeometry.xml'
import logging
import logging.handlers

from rsMap3D.gui.rsm3dcommonstrings import LOGGER_NAME, LOGGER_FORMAT
logger = logging.getLogger(LOGGER_NAME)
userDir = os.path.expanduser("~")
logger.setLevel(logging.INFO)
logFile = os.path.join(userDir, LOGGER_NAME + '.log')
fh = logging.handlers.RotatingFileHandler(logFile, delay=0, maxBytes=6000000, \
                                          backupCount=5)
fh.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter(LOGGER_FORMAT)
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)


class Test(unittest.TestCase):
    

    def testGetCenterChannelPixel(self):
        config = DetectorGeometryForXrayutilitiesReader( \
                     GOOD_FILE_NAME)
        detector = config.getDetectorById("Pilatus")
        centerPix = config.getCenterChannelPixel(detector)
        pix = [210, 85]
        self.assertEqual(centerPix, pix, "getCenterChannelPixel " + 
                         str(centerPix) + " vs " + str(pix))

    def testGetDetectors(self):
        config = DetectorGeometryForXrayutilitiesReader( \
                     GOOD_FILE_NAME)
        detectors = config.getDetectors()
        self.assertNotEqual(detectors, None, "getDetector")
            
    def testGetDetectorsNoDetectors(self):
        config = DetectorGeometryForXrayutilitiesReader( \
                     BAD_FILE_NO_DETECTOR_LIST)
        self.assertRaises(DetectorConfigException, config.getDetectors)
        
    def testGetDetectorsById(self):
        config = DetectorGeometryForXrayutilitiesReader( \
                     GOOD_FILE_NAME)
        detector = config.getDetectorById(DETECTOR_NAME)
        self.assertNotEquals(detector, None, "getDetectorById")

    def testGetDetectorByIdNoDetectorList(self):
        config = DetectorGeometryForXrayutilitiesReader( \
                     BAD_FILE_NO_DETECTOR_LIST)
        self.assertRaises(DetectorConfigException, \
                          config.getDetectorById, \
                          DETECTOR_NAME)
        
    def testGetDetectorByIdNoDetector(self):
        config = DetectorGeometryForXrayutilitiesReader( \
                     BAD_FILE_NO_DETECTOR)
        self.assertRaises(DetectorConfigException, \
                          config.getDetectorById, \
                          DETECTOR_NAME)
        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()