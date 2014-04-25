'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''
from rsMap3D.exception.rsmap3dexception import DetectorConfigException
NAMESPACE = \
    '{https://subversion.xray.aps.anl.gov/RSM/detectorGeometryForXrayutils}'
DETECTORS = NAMESPACE + "Detectors"
DETECTOR = NAMESPACE + "Detector"
DETECTOR_ID = NAMESPACE + "ID"
PIXEL_DIRECTION1 = NAMESPACE + 'pixelDirection1'
PIXEL_DIRECTION2 = NAMESPACE + 'pixelDirection2'
CENTER_CHANNEL_PIXEL = NAMESPACE + 'centerChannelPixel'
NUMBER_OF_PIXELS = NAMESPACE + 'Npixels'
DETECTOR_SIZE = NAMESPACE + 'size'
DETECTOR_DISTANCE = NAMESPACE + 'distance'

import xml.etree.ElementTree as ET
import string

class DetectorGeometryForXrayutilitiesReader(object):
    '''
    This class is for reading detecor geometry XML file for use with 
    xrayutilities
    '''

    def __init__(self, filename):
        '''
        Constructor
        '''
        try:
            tree = ET.parse(filename)
        except IOError as ex:
            raise DetectorConfigException("Bad Detector Configuration File" + \
                                          str(ex))
        self.root = tree.getroot()
        
        
    def getCenterChannelPixel(self, detector):
        '''
        Return a list with two elements specifying the location of the center
        pixel
        ''' 
        try:
            centerPix = detector.find(CENTER_CHANNEL_PIXEL).text
        except AttributeError:
            raise DetectorConfigException(CENTER_CHANNEL_PIXEL + 
                                          " not found in detector config " + \
                                          "file")
        vals = string.split(centerPix)
        return [int(vals[0]), int(vals[1])]
    
    def getDetectors(self):
        '''
        Return a list of detectors in the configuration
        '''
        return self.root.find(DETECTORS)
    
    def getDetectorById(self, id):
        '''
        return a particular by specifying it's ID 
        '''
        try:
            dets = self.getDetectors().findall(DETECTOR)
        except AttributeError:
            raise DetectorConfigException("No detectors found in detector " + \
                                          "config file")
        for detector in dets:
            detId = detector.find(DETECTOR_ID)
            if detId.text == id:
                return detector
        return None

    def getDetectorID(self, detector):
        '''
        return the detecor ID
        '''
        return detector.find(DETECTOR_ID).text

    def getDistance(self, detector):
        '''
        return the sample to detector distance
        '''
        return float(detector.find(DETECTOR_DISTANCE).text)
    
    def getPixelDirection1(self, detector):
        '''
        Return the direction for increasing the first pixel dimension (x+ 
        specifies the first dimension increases in the positive x direction)
        '''
        return detector.find(PIXEL_DIRECTION1).text

    def getNpixels(self, detector):
        '''
        Return a list with two elements specifying the size of the detector
        in pixels
        ''' 
        vals = string.split(detector.find(NUMBER_OF_PIXELS).text)
        return [int(vals[0]), int(vals[1])]
    
    def getPixelDirection2(self, detector):
        '''
        Return the direction for increasing the second pixel dimension (y- 
        specifies the second dimension increases in the negative y direction)
        '''
        return detector.find(PIXEL_DIRECTION2).text

    def getSize(self, detector):
        '''
        Return the size of the detector in millimeters
        '''
        vals = string.split(detector.find(DETECTOR_SIZE).text)
        return [float(vals[0]), float(vals[1])]
    
if __name__ == '__main__':
    config = DetectorGeometryForXrayutilitiesReader('33bmDetectorGeometry.xml')
    print config
    print config.getDetectors()
    detector = config.getDetectorById('Pilatus')
    print detector
    print detector.find(DETECTOR_ID).text
    print config.getDetectorById('Nonsense')
    print config.getPixelDirection1(detector)
    print config.getPixelDirection2(detector)
    print config.getCenterChannelPixel(detector)
    print config.getNpixels(detector)
    print config.getSize(detector)
    print config.getDetectorID(detector)
    print config.getDistance(detector)