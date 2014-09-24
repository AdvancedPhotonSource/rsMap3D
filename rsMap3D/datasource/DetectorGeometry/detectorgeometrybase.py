'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''
import xml.etree.ElementTree as ET
import string
from rsMap3D.exception.rsmap3dexception import DetectorConfigException

class DetectorGeometryBase(object):
    '''
    Base class for detector geometry XML configurations.  
    '''
    
    def __init__(self, filename, nameSpace):
        '''
        initialize the class and make sure the file seems to be valid XML
        '''        
        self._initXmlConstants(nameSpace)
        try:
            tree = ET.parse(filename)
        except IOError as ex:
            raise DetectorConfigException("Bad Detector Configuration File" + \
                                          str(ex))
        self.root = tree.getroot()
        
    def _initXmlConstants(self, nameSpace):
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
        
    
    def getDetectors(self):
        '''
        :return: a list of detectors in the configuration
        
        '''
        detectors = self.root.find(self.DETECTORS)
        if detectors == None:
            raise DetectorConfigException("No detectors found in detector " + \
                                          "config file")
        return detectors
    
    def getDetectorById(self, identifier):
        '''
        return a particular by specifying it's ID 
        :param identifier: the id of the specified detector 
        :return: The requested detector
        '''
        try:
            dets = self.getDetectors().findall(self.DETECTOR)
        except AttributeError:
            raise DetectorConfigException("No detectors found in detector " + \
                                          "config file")
        for detector in dets:
            detId = detector.find(self.DETECTOR_ID)
            if detId.text == identifier:
                return detector
        raise DetectorConfigException("Detector " + 
                                      identifier + 
                                      " not found in detector config file")

    def getDetectorID(self, detector):
        '''
        :param detector: specifies the detector who's return value is requested
        :return: The ID of the specified detector detector
        '''
        return detector.find(self.DETECTOR_ID).text

    def getNpixels(self, detector):
        '''
        :param detector: specifies the detector who's return value is requested
        :return: A list with two elements specifying the size of the detector
        in pixels
        ''' 
        vals = string.split(detector.find(self.NUMBER_OF_PIXELS).text)
        return [int(vals[0]), int(vals[1])]
    
    def getSize(self, detector):
        '''
        :param detector: specifies the detector who's return value is requested
        :return: The size of the detector in millimeters
        '''
        vals = string.split(detector.find(self.DETECTOR_SIZE).text)
        return [float(vals[0]), float(vals[1])]
    