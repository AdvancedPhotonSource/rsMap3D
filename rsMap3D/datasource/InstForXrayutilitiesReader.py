'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''
import xml.etree.ElementTree as ET
from rsMap3D.exception.rsmap3dexception import InstConfigException

NAMESPACE = '{https://subversion.xray.aps.anl.gov/RSM/instForXrayutils}'
#Element Names
DETECTOR_CIRCLES = NAMESPACE + 'detectorCircles'   
FILTER_NAME = NAMESPACE + 'filterName'   
INPLANE_REFERENCE_DIRECTION = NAMESPACE + 'inplaneReferenceDirection'   
MONITOR_NAME = NAMESPACE + 'monitorName'   
PRIMARY_ANGLE = NAMESPACE + 'primaryAngle'   
PRIMARY_BEAM_DIRECTION = NAMESPACE + 'primaryBeamDirection'
PROJECTION_DIRECTION = NAMESPACE + 'projectionDirection'
REFERENCE_ANGLE = NAMESPACE + 'referenceAngle'
SAMPLE_CIRCLES = NAMESPACE + 'sampleCircles'   
SAMPLE_SURFACE_NORMAL_DIRECTION = NAMESPACE + 'sampleSurfaceNormalDirection'
SAMPLE_ANGLE_MAP_FUNCTION = NAMESPACE + 'sampleAngleMapFunction'   
#Attribute Names
ALWAYS_FIX = 'alwaysFix'
AXIS_NUMBER = 'number'
DIRECTION_AXIS = 'directionAxis'
NAME = 'name'
NUM_CIRCLES = 'numCircles'
REFERENCE_AXIS = NAMESPACE + 'axis'
SCALE_FACTOR = 'scaleFactor'
SPEC_MOTOR_NAME = 'specMotorName'
CALC_ON_SCANNED_REF = 'calcOnScannedRef'
SAMPLE_ANGLE_MAP_MODULE = 'module'

class InstForXrayutilitiesReader():
    '''
    Class to read instrument config file associated with xrayutilities and spec
    file
    '''

    def __init__(self, filename):
        '''
        '''
        self.root = None
        try:
            tree = ET.parse(filename)
        except IOError as ex:
            raise (InstConfigException("Bad Instrument Configuration File" + str(ex)))
        self.root = tree.getroot()
        
    def getCircleAxisNumber(self, circle):
        '''
        :param circle: specifies the detector who's return value is requested
        :return: The axis number for the given circle
        '''
        try:
            axisNumberStr = circle.attrib[AXIS_NUMBER]
        except KeyError:
            raise InstConfigException("Axis number is empty in \n" + \
                                      ET.tostring(circle) + \
                                      "\nIn the instrument config file")
        return int(axisNumberStr)
        
    def getDetectorCircleDirections(self):
        '''
        :return: Circle directions for the detector circles 
        '''
        return self._makeCircleDirections(self.getDetectorCircles())
        
    def getDetectorCircles(self):
        '''
        :return: The detector children as and element list.  If detector circles 
        is not included in the file raise an InstConfigException
        '''
        circles = self.root.find(DETECTOR_CIRCLES)
        if circles is None:
            raise InstConfigException("Instrument configuration has no " +\
                                      "Detector Circles")
        return self.root.find(DETECTOR_CIRCLES).getchildren()
        
    def getDetectorCircleNames(self):
        '''
        :return the name of the detector circles
        '''
        return self._makeCircleNames(self.getDetectorCircles())
        
    def getFilterName(self):
        '''
        :return: The filterName if included in config file.  Returns None if it
        is not present. 
        '''
        name = self.root.find(FILTER_NAME)
        if name is None:
            return None
        else:
            if name.text is None or name.text.strip() == "":
                return None
            else:
                return str(name.text.strip())
    
    def getFilterScaleFactor(self):
        '''
        :return: The scale factor to be used with filterName if included in 
        config file.  Returns 1 if it is not present. 
        '''
        name = self.root.find(FILTER_NAME)
        if name is None:
            return 1
        else:
            try:
                return float(name.attrib[SCALE_FACTOR])
            except KeyError:
                return 1
    
    def getInplaneReferenceDirection(self):
        '''
        :return: The In-plane reference direction
        '''
        direction = \
            self.root.find(INPLANE_REFERENCE_DIRECTION)
        if direction is None:
            raise InstConfigException("Missing in-plane reference direction " + \
                                      "in instrument config file")
        return self._makeReferenceDirection(direction )
        
    def getMonitorName(self):
        '''
        :return: the monitorName if included in config file.  Returns None if it
        is not present or if the text string is empty
        '''
        name = self.root.find(MONITOR_NAME)
        if name is None:
            return None
        else:
            if name.text is None or name.text.strip() == "":
                return None
            else:
                return str(name.text.strip())
    
    def getMonitorScaleFactor(self):
        '''
        :return: The scale factor to be used with monitorName if included in 
        config file.  Returns 1 if it is not present. 
        '''
        name = self.root.find(MONITOR_NAME)
        if name is None:
            return 1
        else:
            try:
                return float(name.attrib[SCALE_FACTOR])
            except KeyError:
                return 1
    
    def getNumDetectorCircles(self):
        '''
        :return: the number of circles associated with the detector
        '''
        return int(self.root.find(DETECTOR_CIRCLES).attrib[NUM_CIRCLES])
    
    def getNumSampleCircles(self):
        '''
        :return: the number of circles associated with the sample
        '''
        return int(self.root.find(SAMPLE_CIRCLES).attrib[NUM_CIRCLES])
    
    def getPrimaryBeamDirection(self):
        '''
        :return: The direction of primary beam
        '''
        direction = \
            self.root.find(PRIMARY_BEAM_DIRECTION)
        if direction is None:
            raise InstConfigException("Missing primary beam direction " + \
                                      "in instrument config file")
        return self._makeReferenceDirection(direction )
        
    def getProjectionDirection(self):
        '''
        :return: The direction to be used for constructing Stereographic 
        projections.
        '''
        
        direction = \
            self.root.find(PROJECTION_DIRECTION)
        if direction is None:
            message = PROJECTION_DIRECTION + \
                      " was not found in the instrument config file"
            raise InstConfigException(message)
        return self._makeReferenceDirection(direction )
        
    def getSampleAngleMappingCalcOnScannedRef(self):
        '''
        :return: true to run mapping function only when a reference angle is 
        scanned 
        '''
        function = self.root.find(SAMPLE_ANGLE_MAP_FUNCTION)
        if function is None:
            raise InstConfigException("No Mapping function defined in " + \
                             "instrument config file")
        if function.attrib[CALC_ON_SCANNED_REF] is None:
            return False
        else:
            if function.attrib[CALC_ON_SCANNED_REF].lower() in \
                ['true', '1', 'yes']:
                return True
            elif function.attrib[CALC_ON_SCANNED_REF].lower() in \
                ['false', '0', 'no']:
                return False
            else:
                raise InstConfigException("Error reading value for " + \
                                 "'calcOnScannedRef' from Instrument " + \
                                 "Config : " + \
                                 str(function.attrib[CALC_ON_SCANNED_REF]))
                
                
    def getSampleAngleMappingFunctionName(self):
        '''
        :return: The name of a function to be used in mapping 
        '''
        function = self.root.find(SAMPLE_ANGLE_MAP_FUNCTION)
        if function is None:
            return ""
        else:
            return function.attrib[NAME]

    def getSampleAngleMappingFunctionModule(self):
        '''
        :return: The name of a function to be used in mapping 
        '''
        function = self.root.find(SAMPLE_ANGLE_MAP_FUNCTION)
        if function is None:
            raise InstConfigException("No Mapping function defined in " +\
                                      "instrument config file")
        try:
            module = function.attrib[SAMPLE_ANGLE_MAP_MODULE]
        except KeyError:
            module = None
        if module != None and module != "":
            print ("Found Module %s" % module)
            return module
        else:
            return None


    def getSampleAngleMappingParameter(self, name):
        '''
        Return a named parameter to be used by the mapping function.  This 
        parameter is unique to the mapping function.  This method returns a 
        string parameter which must be properly cast by the mapping function.
        Mapping function needs to deal with error cases.  None is returned if 
        the named parameter is not defined.
        :param: name Name of the defined parameter
        :return: Parameter defined by the XML element 'name'
        
        '''
        function = self.root.find(SAMPLE_ANGLE_MAP_FUNCTION)
        if function is None:
            raise InstConfigException("No Mapping function defined in " +\
                                      "instrument config file")
        param = function.find(NAMESPACE + name)
        if param != None and param.text != "":
            return param.text
        else:
            return None
    
    def getSampleAngleMappingPrimaryAngles(self):
        '''
        :return: The name of a function to be used in mapping 
        '''
        function = self.root.find(SAMPLE_ANGLE_MAP_FUNCTION)
        if function is None:
            raise InstConfigException("No Mapping function defined in " +\
                                      "instrument config file")
        angles = []
        primaryAngles = function.findall(PRIMARY_ANGLE)
        if primaryAngles is None:
            raise InstConfigException("No primaryAngle members in " + \
            "sampleAngleMapFunction in instrument config")
        for angle in primaryAngles:
            angles.append(int(angle.attrib[AXIS_NUMBER]))
        angles.sort()
        return angles
    
    def getSampleAngleMappingReferenceAngleAttrib(self, \
                                                number=None, \
                                                attribName=None):
        attribValue = None
        function = self.root.find(SAMPLE_ANGLE_MAP_FUNCTION)
        if function is None:
            raise InstConfigException("No Mapping function defined in " +\
                                      "instrument config file")
        refAngles = function.findall(REFERENCE_ANGLE)
        for angle in refAngles:
            if angle.attrib[SPEC_MOTOR_NAME] == str(number):
                attribValue = angle.attrib[attribName]
        if (attribValue is None):
            raise(AttributeError("Angle " + str(number) +
                                 " does not have a value for " +
                                 str(attribName)))
        return attribValue

    def getSampleAngleMappingReferenceAngles(self):
        '''
          '''
        function = self.root.find(SAMPLE_ANGLE_MAP_FUNCTION)
        if function is None:
            raise InstConfigException("No Mapping function defined in " + \
                             "instrument config file")
        angles = {}
        angleList = []
        referenceAngles = function.findall(REFERENCE_ANGLE)
        if referenceAngles is None:
            raise InstConfigException("No referenceAngle members in " + \
            "sampleAngleMapFunction in instrument config")
        for angle in referenceAngles:
            angles[int(angle.attrib[AXIS_NUMBER])] = \
                angle.attrib[SPEC_MOTOR_NAME]
        for i in  angles.keys():
            angleList.append(angles[i])
        return angleList

    def getSampleAngleMappingAlwaysFix(self):
        function =  self.root.find(SAMPLE_ANGLE_MAP_FUNCTION)
        
        if function is None:
            raise InstConfigException("No Mapping function defined in " + \
                             "instrument config file")
        alwaysFix = None
        try:
            alwaysFix = function.attrib[ALWAYS_FIX]
            if alwaysFix is None:
                return False
        except KeyError:
            alwaysFix = False
        return bool(alwaysFix)
        
    def getSampleCircleDirections(self):
        '''
        :return: The sample circle directions
        '''
        return self._makeCircleDirections(self.getSampleCircles())
        
    def getSampleCircles(self):
        '''
        :return: The sample children as and element list.  If sample circles 
        is not included in the file raise an InstConfigException
        '''
        circles = self.root.find(SAMPLE_CIRCLES)
        if circles is None:
            raise InstConfigException("Instrument configuration has no Sample" +
                                      " Circles")
        return circles.getchildren()

    def getSampleCircleNames(self):
        '''
        :return: the Names of the sample circles
        '''
        return self._makeCircleNames(self.getSampleCircles())
        
    def getSampleSurfaceNormalDirection(self):
        '''
        :return: The sample surface normal direction as a list of 3 numbers
        '''
        direction = \
            self.root.find(SAMPLE_SURFACE_NORMAL_DIRECTION)
        if direction is None:
            raise InstConfigException("Missing sample surface normal " + \
                                      "direction in instrument config file")
        return self._makeReferenceDirection(direction )
        
    def _makeCircleDirections(self, circles):
        '''
        Create a list of circle directions from the XML
        :param circles: the XML representation of the circles
        '''
        data = []
        for circle in circles:
            try:
                axisNum = circle.attrib[AXIS_NUMBER]
                directionAxis = circle.attrib[DIRECTION_AXIS]
            except KeyError:
                raise InstConfigException("missing axis number or " + \
                                          "axis direction in\n" + \
                                          ET.tostring(circle) + \
                                          "\nIn the instrument config file")
            data.append((int(axisNum), \
                            directionAxis))
        data.sort()
        directions = []
        for dataum in data:
            directions.append(dataum[1])
        return directions
    
    def _makeCircleNames(self, circles):
        '''
        Create a list of circle names from the XML
        :param circles: the XML representation of the circles
        '''
        data = []
        for circle in circles:
            try:
                motorName = circle.attrib[SPEC_MOTOR_NAME]
                axisNumber = circle.attrib[AXIS_NUMBER]
            except KeyError:
                raise InstConfigException("missing axis number or " + \
                                          "motorName in\n" + \
                                          ET.tostring(circle) + \
                                          "\nIn the instrument config file")
            data.append((int(axisNumber), \
                            motorName))
        data.sort()
        names = []
        for dataum in data:
            names.append(dataum[1])
        return names
    
    def _makeReferenceDirection(self, direction):
        '''
        Create a list of reference directions from the XML
        :param direction: the XML representation of the circle
        '''
        axes = direction.findall(REFERENCE_AXIS)
        
        if len(axes) != 3:
            raise InstConfigException("Axes not defined properly in \n" + \
                                      ET.tostring(direction) + \
                                      "\nin instrument config file")
                  
        refAxis = {}
        for axis in axes:
            try:
                refAxis[int(axis.attrib[AXIS_NUMBER])] = int(axis.text)
            except ValueError:
                raise InstConfigException("Values and axis numbers in " + \
                                           ET.tostring(direction) + \
                                           " in instrument configuration file")
                                            
        return [refAxis[1], refAxis[2], refAxis[3]]
    

        
