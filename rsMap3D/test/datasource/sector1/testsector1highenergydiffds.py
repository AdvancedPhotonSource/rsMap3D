'''
 Copyright (c) 2017, UChicago Argonne, LLC
 See LICENSE file.
'''
import os
import logging
import logging.config
import unittest
from rsMap3D.datasource.s1highenergydiffractionds import S1ParameterFile,\
    S1HighEnergyDiffractionDS
from rsMap3D.config.rsmap3dlogging import LOGGER_NAME
from rsMap3D.transforms.unitytransform3d import UnityTransform3D
from rsMap3D.config.rsmap3dconfigparser import RSMap3DConfigParser

GOOD_FILE_NUM_LINES = 8

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

configDir = os.path.join(THIS_DIR, '../../../resources/config')
logConfigFile = os.path.join(configDir, LOGGER_NAME + 'Log.test.config')
print logConfigFile
logging.config.fileConfig(logConfigFile)
logger = logging.getLogger(LOGGER_NAME)
PAR_FILE1 = os.path.join(THIS_DIR, \
                         "../../../resources/1-idscan/fastpar_startup_oct16_FF1.par")
PAR_FILE2 = os.path.join(THIS_DIR, \
                         "../../../resources/1-idscan/fastpar_startup_oct16_FF1_with_comments.par")
PAR_FILE3 = os.path.join(THIS_DIR, \
                         "../../../resources/1-idscan/fastpar_startup_oct16_FF1_with_blanks.par")

class Test(unittest.TestCase):

    def testParameterFileSimpleFile(self):
        parFile = S1ParameterFile(PAR_FILE1)
        numLines = parFile.getNumOfLines()
        self.assertEqual(GOOD_FILE_NUM_LINES, numLines, 
                         "Testing read of number Of lines")
        
    def testParameterFileWithComments(self):
        parFile = S1ParameterFile(PAR_FILE2)
        numLines = parFile.getNumOfLines()
        self.assertEqual(GOOD_FILE_NUM_LINES, numLines, 
                         "Testing read of number Of lines")
         
    def testParameterFileWithBlankLines(self):
        parFile = S1ParameterFile(PAR_FILE3)
        numLines = parFile.getNumOfLines()
        self.assertEqual(GOOD_FILE_NUM_LINES, numLines, 
                         "Testing read of number Of lines " + \
                         str(GOOD_FILE_NUM_LINES) + "Expected, " +
                         str(numLines) + " Read")
        
    def testS1HighEnergyDiffractionDS(self):
        projectDir = os.path.join(configDir, "../1-idscan")
        projectName = "fastpar_startup_oct16_FF1"
        projectExtension = ".par"
        instConfig = os.path.join(projectDir, "1-ID-E_AeroTable.xml")
        detConfig = os.path.join(projectDir, "1-ID-GE.xml")
        transform = UnityTransform3D()
        pixelsToAverage = [1,1]
        scanList = [3,]
        detRoi = [1,2048,1,2048]
        imageDirName = ""         #fake since not used here.
        appConfig = RSMap3DConfigParser()
        ds = S1HighEnergyDiffractionDS(str(projectDir),
                                       str(projectName),
                                       str(projectExtension),
                                       str(instConfig),
                                       str(detConfig),
                                       imageDirName,
                                       transform=transform,
                                       scanList=scanList,
                                       pixelsToAverage= pixelsToAverage,
                                       badPixelFile=None,
                                       flatFieldFile=None,
                                       appConfig=appConfig)
        ds.setCurrentDetector('ge3')
        ds.loadSource()
        availableScans = ds.getAvailableScans()
        self.assertEquals(availableScans, [3,])
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()