'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''
import xml.etree.ElementTree as ET

NAMESPACE = '{https://subversion.xray.aps.anl.gov/RSM/instForXrayutils}'
SAMPLE_CIRCLES = NAMESPACE + 'sampleCircles'   
DETECTOR_CIRCLES = NAMESPACE + 'detectorCircles'   
PRIMARY_BEAM_DIRECTION = NAMESPACE + 'primaryBeamDirection'   
INPLANE_REFERENCE_DIRECTION = NAMESPACE + 'inplaneReferenceDirection'   
SAMPLE_SURFACE_NORMAL_DIRECTION = NAMESPACE + 'sampleSurfaceNormalDirection'   
MONITOR_NAME = NAMESPACE + 'monitorName'   
NUM_CIRCLES = 'numCircles'
SPEC_MOTOR_NAME = 'specMotorName'
AXIS_NUMBER = 'number'
REFERENCE_AXIS = NAMESPACE + 'axis'
DIRECTION_AXIS = 'directionAxis'
SCALE_FACTOR = 'scaleFactor'

class InstForXrayutilitiesReader():
    '''
    '''

    def __init__(self, filename):
        '''
        '''
        self.root = None
        try:
            tree = ET.parse(filename)
        except IOError as ex:
            raise (IOError("Bad Instrument Configuration File" + str(ex)))
        self.root = tree.getroot()
        
    def getCircleAxisNumber(self, circle):
        '''
        '''
        return int(circle.attrib[AXIS_NUMBER])
        
    def getCircleDirection(self, circle):
        '''
        '''
        return circle.text
    
    def getDetectorCircleDirections(self):
        '''
        '''
        return self.makeCircleDirections(self.getDetectorCircles())
        
    def getCircleSpecMotorName(self, circle):
        '''
        '''
        return circle.attrib[SPEC_MOTOR_NAME]
    
    def getDetectorCircles(self):
        '''
        Return the detectpr childer as and element list.  If detector circles 
        is not included in the file raise an IOError
        '''
        circles = self.root.find(DETECTOR_CIRCLES)
        if circles == None:
            raise IOError("Instrument configuration has no Detector Circles")
        return self.root.find(DETECTOR_CIRCLES).getchildren()
        
    def getDetectorCircleNames(self):
        '''
        '''
        return self.makeCircleNames(self.getDetectorCircles())
        
    def getInplaneReferenceDirection(self):
        '''
        '''
        direction = \
            self.root.find(INPLANE_REFERENCE_DIRECTION)
        return self.makeReferenceDirection(direction )
        
    def getMonitorName(self):
        '''
        Return the monitorName if included in config file.  Returns None if it
        is not present. 
        '''
        name = self.root.find(MONITOR_NAME)
        if name == None:
            return None
        else:
            return str(name.text)
    
    def getMonitorScaleFactor(self):
        '''
        Return the monitorName if included in config file.  Returns None if it
        is not present. 
        '''
        name = self.root.find(MONITOR_NAME)
        if name == None:
            return 1
        else:
            if name.attrib[SCALE_FACTOR] != None:
                return float(name.attrib[SCALE_FACTOR])
            else:
                return 1
    
    def getNumDetectorCircles(self):
        '''
        '''
        return int(self.root.find(DETECTOR_CIRCLES).attrib[NUM_CIRCLES])
    
    def getNumSampleCircles(self):
        '''
        '''
        return int(self.root.find(SAMPLE_CIRCLES).attrib[NUM_CIRCLES])
    
    def getPrimaryBeamDirection(self):
        '''
        '''
        direction = \
            self.root.find(PRIMARY_BEAM_DIRECTION)
        return self.makeReferenceDirection(direction )
        
    def getSampleCircleDirections(self):
        '''
        '''
        return self.makeCircleDirections(self.getSampleCircles())
        
    def getSampleCircles(self):
        '''
        Return the detectpr childer as and element list.  If detector circles 
        is not included in the file raise an IOError
        '''
        circles = self.root.find(SAMPLE_CIRCLES)
        if circles == None:
            raise IOError("Instrument configuration has no Sample Circles")
        return circles.getchildren()

    def getSampleCircleNames(self):
        '''
        '''
        return self.makeCircleNames(self.getSampleCircles())
        
    def getSampleSurfaceNormalDirection(self):
        '''
        '''
        direction = \
            self.root.find(SAMPLE_SURFACE_NORMAL_DIRECTION)
        return self.makeReferenceDirection(direction )
        
    def makeCircleDirections(self, circles):
        '''
        '''
        data = []
        for circle in circles:
            data.append((int(circle.attrib[AXIS_NUMBER]), \
                            circle.attrib[SPEC_MOTOR_NAME], \
                            circle.attrib[DIRECTION_AXIS]))
        data.sort()
        directions = []
        for dataum in data:
            directions.append(dataum[2])
        return directions
    
    def makeCircleNames(self, circles):
        '''
        '''
        data = []
        for circle in circles:
            data.append((int(circle.attrib[AXIS_NUMBER]), \
                            circle.attrib[SPEC_MOTOR_NAME], \
                            circle.attrib[DIRECTION_AXIS]))
        data.sort()
        names = []
        for dataum in data:
            names.append(dataum[1])
        return names
    
    def makeReferenceDirection(self, direction):
        '''
        '''
        axes = direction.findall(REFERENCE_AXIS)
        refAxis = {}
        for axis in axes:
            refAxis[int(axis.attrib[AXIS_NUMBER])] = int(axis.text)
        return [refAxis[1], refAxis[2], refAxis[3]]
        
if __name__ == '__main__':
    config = InstForXrayutilitiesReader('33BM-instForXrayutilities.xml')
    print config
    print config.getSampleCircles()
    print config.getDetectorCircles()
    print '====Sample Circles ' + str(config.getNumSampleCircles())
    for circle in config.getSampleCircles():
        print config.getCircleAxisNumber(circle)
        print config.getCircleSpecMotorName(circle)
        print config.getCircleDirection(circle)
    print '====Detector Circles ' + str(config.getNumDetectorCircles())
    for circle in config.getDetectorCircles():
        print config.getCircleAxisNumber(circle)
        print config.getCircleSpecMotorName(circle)
        print config.getCircleDirection(circle)

    print config.getPrimaryBeamDirection()
    print config.getInplaneReferenceDirection()
    print config.getSampleSurfaceNormalDirection()
    
    print config.getSampleCircleDirections()
    print config.getSampleCircleNames()
    print config.getDetectorCircleDirections()
    print config.getDetectorCircleNames()