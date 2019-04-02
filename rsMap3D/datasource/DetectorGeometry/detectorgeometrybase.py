'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''
import logging
import xml.etree.ElementTree as ET
import string
from rsMap3D.exception.rsmap3dexception import DetectorConfigException
logger = logging.getLogger(__name__)

class DetectorGeometryBase(object):
    '''
    Base class for detector geometry XML configurations.  
    '''
    
    def __init__(self, filename, nameSpace):
        '''
        initialize the class and make sure the file seems to be valid XML
        '''        
        logger.debug("Enter")
        self._initXmlConstants(nameSpace)
        try:
            tree = ET.parse(filename)
        except IOError as ex:
            raise DetectorConfigException("Bad Detector Configuration File" + \
                                          str(ex))
        self.root = tree.getroot()
        logger.debug("Exit")
        
    def _initXmlConstants(self, nameSpace):
        logger.debug("Enter")
        self.nameSpace = nameSpace
        self.DETECTORS = nameSpace + "Detectors"
        self.DETECTOR = nameSpace + "Detector"
        self.DETECTOR_ID = nameSpace + "ID"
        self.PIXEL_DIRECTION1 = nameSpace + 'pixelDirection1'
        self.PIXEL_DIRECTION2 = nameSpace + 'pixelDirection2'
        self.CENTER_CHANNEL_PIXEL = nameSpace + 'centerChannelPixel'
        self.NUMBER_OF_PIXELS = nameSpace + 'Npixels'
        self.DETECTOR_SIZE = nameSpace + 'size'
        self.DETECTOR_DISTANCE = nameSpace + 'distance'
        logger.debug("Exit")
        
    
    def getDetectors(self):
        '''
        :return: a list of detectors in the configuration
        
        '''
        logger.debug("Enter")
        detectors = self.root.find(self.DETECTORS)
        if detectors is None:
            raise DetectorConfigException("No detectors found in detector " + \
                                          "config file")
        logger.debug("Exit")
        return detectors
    
    def getDetectorById(self, identifier):
        '''
        return a particular by specifying it's ID 
        :param identifier: the id of the specified detector 
        :return: The requested detector
        '''
        logger.debug("Enter")
        try:
            dets = self.getDetectors().findall(self.DETECTOR)
        except AttributeError:
            raise DetectorConfigException("No detectors found in detector " + \
                                          "config file")
        logger.debug(str(dets))
        for detector in dets:
            detId = detector.find(self.DETECTOR_ID)
            logger.debug("getDetectorById id found - " + str(self.getDetectorID(detector)))
     
            if detId.text == identifier:
                logger.debug("Exit")
                return detector
        logger.debug("Exit w Exception")
        raise DetectorConfigException("Detector " + 
                                      str(identifier) + 
                                      " not found in detector config file")

    def getDetectorID(self, detector):
        '''
        :param detector: specifies the detector who's return value is requested
        :return: The ID of the specified detector detector
        '''
        logger.debug("Enter")
        detID = detector.find(self.DETECTOR_ID).text
        logger.debug("Exit detID - " + str(detID) )
        return detID

    def getNpixels(self, detector):
        '''
        :param detector: specifies the detector who's return value is requested
        :return: A list with two elements specifying the size of the detector
        in pixels
        ''' 
        logger.debug("Enter")
        vals = detector.find(self.NUMBER_OF_PIXELS).text.split()
        retVal = [int(vals[0]), int(vals[1])]
        logger.debug("Exit" + str(retVal))
        return retVal
    
    def getSize(self, detector):
        '''
        :param detector: specifies the detector who's return value is requested
        :return: The size of the detector in millimeters
        '''
        logger.debug("Enter")
        vals = detector.find(self.DETECTOR_SIZE).text.split()
        retVal = [float(vals[0]), float(vals[1])]
        logger.debug("Exit " + str(retVal))
        return retVal
    