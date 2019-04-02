'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''
from rsMap3D.exception.rsmap3dexception import DetectorConfigException
import logging
from rsMap3D.config.rsmap3dlogging import METHOD_ENTER_STR, METHOD_EXIT_STR
from rsMap3D.datasource.DetectorGeometry.detectorgeometrybase \
    import DetectorGeometryBase
nameSpace = \
    '{https://subversion.xray.aps.anl.gov/RSM/detectorGeometryForXrayutils}'

import xml.etree.ElementTree as ET
import string
logger = logging.getLogger(__name__)

class DetectorGeometryForXrayutilitiesReader(DetectorGeometryBase):
    '''
    This class is for reading detector geometry XML file for use with 
    xrayutilities
    :members:
    '''

    def __init__(self, filename):
        '''
        Constructor
        :param filename: name of the XML file holding the detector geomery
        '''
        super(DetectorGeometryForXrayutilitiesReader, self).__init__(filename, nameSpace)
        logger.debug(METHOD_ENTER_STR)
#         self.DETECTORS = nameSpace + "Detectors"
#         self.DETECTOR = nameSpace + "Detector"
#         self.DETECTOR_ID = nameSpace + "ID"
        self.PIXEL_DIRECTION1 = nameSpace + 'pixelDirection1'
        self.PIXEL_DIRECTION2 = nameSpace + 'pixelDirection2'
        self.CENTER_CHANNEL_PIXEL = nameSpace + 'centerChannelPixel'
#         self.NUMBER_OF_PIXELS = nameSpace + 'Npixels'
#         self.DETECTOR_SIZE = nameSpace + 'size'
        self.DETECTOR_DISTANCE = nameSpace + 'distance'
        try:
            tree = ET.parse(filename)
        except IOError as ex:
            raise DetectorConfigException("Bad Detector Configuration File" + \
                                          str(ex))
        self.root = tree.getroot()
        logger.debug(METHOD_EXIT_STR)
        
        
    def getCenterChannelPixel(self, detector):
        '''
        Return a list with two elements specifying the location of the center
        pixel
        :param detector: specifies the detector who's return value is requested
        :return: The location of the detector's center pixel 
        ''' 
        logger.debug(METHOD_ENTER_STR)
        try:
            centerPix = detector.find(self.CENTER_CHANNEL_PIXEL).text
        except AttributeError:
            raise DetectorConfigException(self.CENTER_CHANNEL_PIXEL + 
                                          " not found in detector config " + \
                                          "file")
        vals = centerPix.split()
        logger.debug(METHOD_EXIT_STR + str([int(vals[0]), int(vals[1])]) )
        return [int(vals[0]), int(vals[1])]
    
    def getDistance(self, detector):
        '''
        :param detector: specifies the detector who's return value is requested
        :return: The sample to detector distance
        '''
        logger.debug(METHOD_ENTER_STR)
        detectorDistance = float(detector.find(self.DETECTOR_DISTANCE).text)
        logger.debug(METHOD_EXIT_STR + str(detectorDistance))
        return detectorDistance
    
    def getPixelDirection1(self, detector):
        '''
        :param detector: specifies the detector who's return value is requested
        :return: The direction for increasing the first pixel dimension (x+ 
        specifies the first dimension increases in the positive x direction)
        '''
        logger.debug(METHOD_ENTER_STR)
        pixelDirection1 = detector.find(self.PIXEL_DIRECTION1).text
        logger.debug(METHOD_EXIT_STR + str(pixelDirection1))
        return pixelDirection1

    def getPixelDirection2(self, detector):
        '''
        :param detector: specifies the detector who's return value is requested
        :return:  The direction for increasing the second pixel dimension (y- 
        specifies the second dimension increases in the negative y direction)
        '''
        logger.debug(METHOD_ENTER_STR)
        pixelDirection2 = detector.find(self.PIXEL_DIRECTION2).text
        logger.debug(METHOD_EXIT_STR + str(pixelDirection2))
        return pixelDirection2
