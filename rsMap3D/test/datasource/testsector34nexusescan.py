'''
Created on Sep 5, 2014

@author: hammonds
'''
import os
import unittest
from rsMap3D.datasource.sector34nexusescansource import Sector34NexusEscanSource
from rsMap3D.config.rsmap3dconfigparser import RSMap3DConfigParser

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

FILE_BASE_DIR = os.path.join(THIS_DIR,'../../resources/34-id-escan/')
DETECTOR_CONFIG_FILE = FILE_BASE_DIR + 'geoN_for_Ptdots.xml'

class Test(unittest.TestCase):


#     def setUp(self):
#         self.projectDir = "/home/oxygen/HAMMONDS/test_data_Escan_RSM"
#         self.projectName = "Escan_Pt_dotB_-15V"
#         self.projectExtension = ".h5"
#         self.detConfigFile = DETECTOR_CONFIG_FILE
# 
# 
#     def tearDown(self):
#         pass
# 
# 
#     def testLoadSource(self):
#         dataSource = Sector34NexusEscanSource(self.projectDir, \
#                                               self.projectName, \
#                                               self.projectExtension, \
#                                               self.detConfigFile)
#         dataSource.loadSource()
#         print dataSource.rho
#         pass

    def testComparePixel2XYZ(self):
        self.projectDir = os.path.join(THIS_DIR, 
                                       "../..resources/34-id-escan-compare")
        self.projectName = ""
        self.projectExtension = ".h5"
        self.detConfigFile = os.path.join(THIS_DIR,
          "../../resources/34-id-escan-compare/geoN_2016-02-17_18-11-38.xml")
        appConfig = RSMap3DConfigParser()
        self.datasource = Sector34NexusEscanSource(self.projectDir, \
                                              self.projectName, \
                                              self.projectExtension, \
                                              self.detConfigFile, \
                                              appConfig=appConfig)
        
        self.datasource.loadDetectorConfig()
        self.datasource.detectorROI= [1,2048, 1, 2048]
        print self.datasource.rho
        print "+++++++++++++"
        print self.datasource.rho[0]
        print self.datasource.rho[1]
        print self.datasource.rho[2]
        print "+++++++++++++"
        print self.datasource.rho[:,0]
        print self.datasource.rho[:,1]
        print self.datasource.rho[:,2]
        
        print self.datasource.detectorROI
        xIndexArray = range(self.datasource.detectorROI[0], self.datasource.detectorROI[1] +1)
        yIndexArray = range(self.datasource.detectorROI[2], self.datasource.detectorROI[3] +1)

        import numpy as np
        print "calculate from mesh"
        indexMesh = np.meshgrid(xIndexArray, yIndexArray)
        qpxyz = self.datasource.pixel2q_2(indexMesh, None)
        print "qpxyz.shape"
        print qpxyz.shape
        print "qpxyz[0]"
        print qpxyz[0]
        print qpxyz[0].shape
        print "qpxyz[1]"
        print qpxyz[1]
        print qpxyz[1].shape
        print "qpxyz[2]"
        print qpxyz[2]
        print qpxyz[2].shape
        
        arraySize = [len(xIndexArray), len(yIndexArray)]
       
        print "calculate from loop"
        self.qpx =np.zeros(arraySize)
        self.qpy =np.zeros(arraySize)
        self.qpz =np.zeros(arraySize)
        for row in yIndexArray:
            for column in xIndexArray:
                startX = self.datasource.detectorROI[0]
                startY = self.datasource.detectorROI[2]
                qForPixel = self.datasource.pixel2q(column, row, None)
                self.qpx[row-startX, column-startY] = qForPixel[0]
                self.qpy[row-startX, column-startY] = qForPixel[1]
                self.qpz[row-startX, column-startY] = qForPixel[2]

        print "qpx"
        print self.qpx
        print self.qpx.shape
        print "qpy"
        print self.qpy
        print self.qpy.shape
        print "qpz"
        print self.qpz
        print self.qpz.shape

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()