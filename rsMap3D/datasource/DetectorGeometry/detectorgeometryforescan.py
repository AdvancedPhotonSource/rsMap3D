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
    Detector geometry file to get information for Energy scans how they are done 
    in Sector 34
    '''
    
    def __init__(self, filename):
        '''
        Constructor, load superclass init and set up a couple
        of constants used for location data in the XML file.
        '''
        super(DetectorGeometryForEScan,self).__init__(filename, NAMESPACE)
        self.TRANSLATION = self.nameSpace + "P"
        self.ROTATION = self.nameSpace + "R"
        
    def getRotation(self, detector):
        '''
        :param detector: specifies the detector who's return value is requested
        :return: The size of the detector in millimeters
        '''
        vals = detector.find(self.ROTATION).text.split()
        return [float(vals[0]), float(vals[1]), float(vals[2])]

    def getTranslation(self, detector):
        '''
        :param detector: specifies the detector who's return value is requested
        :return: The size of the detector in millimeters
        '''
        vals = detector.find(self.TRANSLATION).text.split()
        return [float(vals[0]), float(vals[1]), float(vals[2])]
    