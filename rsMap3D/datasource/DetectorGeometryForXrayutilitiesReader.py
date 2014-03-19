'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''
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
    classdocs
    '''

    def __init__(self, filename):
        '''
        Constructor
        '''
        try:
            tree = ET.parse(filename)
        except IOError as ex:
            raise (IOError("Bad Detector Configuration File") + str(ex))
        self.root = tree.getroot()
        
        
    def getDetectors(self):
        return self.root.find(DETECTORS)
    
    def getDetectorById(self, id):
        dets = self.getDetectors().findall(DETECTOR)
        for detector in dets:
            detId = detector.find(DETECTOR_ID)
            print detId.text
            if detId.text == id:
                return detector
        return None

    def getPixelDirection1(self, detector):
        return detector.find(PIXEL_DIRECTION1).text

    def getPixelDirection2(self, detector):
        return detector.find(PIXEL_DIRECTION2).text

    def getCenterChannelPixel(self, detector):
        vals = string.split(detector.find(CENTER_CHANNEL_PIXEL).text)
        return [int(vals[0]), int(vals[1])]
    
    def getNpixels(self, detector):
        vals = string.split(detector.find(NUMBER_OF_PIXELS).text)
        return [int(vals[0]), int(vals[1])]
    
    def getSize(self, detector):
        vals = string.split(detector.find(DETECTOR_SIZE).text)
        return [float(vals[0]), float(vals[1])]
    
    def getDetectorID(self, detector):
        return detector.find(DETECTOR_ID).text

    def getDistance(self, detector):
        return float(detector.find(DETECTOR_DISTANCE).text)
    
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