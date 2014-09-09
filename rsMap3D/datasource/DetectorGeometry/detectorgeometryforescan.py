'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''
import string
from rsMap3D.datasource.DetectorGeometry.detectorgeometrybase \
    import DetectorGeometryBase
NAMESPACE = \
    '{http://sector34.xray.aps.anl.gov/34ide/geoN}'
    
    
class DetectorGeometryForEScan(DetectorGeometryBase):
    '''
    '''
    
    def __init__(self, filename):
        super(DetectorGeometryForEScan,self).__init__(filename, NAMESPACE)
        self.TRANSLATION = self.nameSpace + "P"
        self.ROTATION = self.nameSpace + "R"
        
    def getRotation(self, detector):
        '''
        :param detector: specifies the detector who's return value is requested
        :return: The size of the detector in millimeters
        '''
        vals = string.split(detector.find(self.ROTATION).text)
        return [float(vals[0]), float(vals[1]), float(vals[2])]

    def getTranslation(self, detector):
        '''
        :param detector: specifies the detector who's return value is requested
        :return: The size of the detector in millimeters
        '''
        vals = string.split(detector.find(self.TRANSLATION).text)
        return [float(vals[0]), float(vals[1]), float(vals[2])]
    