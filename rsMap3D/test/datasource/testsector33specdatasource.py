'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''
import unittest
import logging
import logging.config
from rsMap3D.datasource.Sector33SpecDataSource import Sector33SpecDataSource
import os
from rsMap3D.config.rsmap3dlogging import LOGGER_NAME
from rsMap3D.config.rsmap3dconfigparser import RSMap3DConfigParser

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(THIS_DIR, "../../resources/spec")
PROJECT_NAME = "CB_140303A_1"
PROJECT_EXT = ".spec"
INST_CONFIG_1 = os.path.join(THIS_DIR, 
                             "../../resources/33BM-instForXrayutilities.xml")
DET_CONFIG = os.path.join(THIS_DIR, "../../resources/33bmDetectorGeometry.xml")
CURRENT_DETECTOR = "Pilatus"
configDir = os.path.join(THIS_DIR, '../../resources/config')
logConfigFile = os.path.join(configDir, LOGGER_NAME + 'Log.test.config')
print logConfigFile
logging.config.fileConfig(logConfigFile)
logger = logging.getLogger(LOGGER_NAME)

class Test(unittest.TestCase):


    def setUp(self):
        appConfig = RSMap3DConfigParser()
        self.dataSource = Sector33SpecDataSource(PROJECT_DIR, \
                                                 PROJECT_NAME, \
                                                 PROJECT_EXT, \
                                                 INST_CONFIG_1, \
                                                 DET_CONFIG, \
                                                 appConfig=appConfig)
        self.dataSource.setCurrentDetector(CURRENT_DETECTOR)
        self.dataSource.loadSource()


    def tearDown(self):
        pass


    def testGetMonitorName(self):
        monitorName = self.dataSource.getMonitorName()
        self.assertEqual(monitorName, "I0", "getMonitorName")

    def testGetMonitorScaleFactor(self):
        scaleFactor = self.dataSource.getMonitorScaleFactor()
        self.assertEqual(scaleFactor, 20000, "getMonitorScaleFactor")

    def testGetFilterName(self):
        filterName = self.dataSource.getFilterName()
        self.assertEqual(filterName, "trans", "getFilterName")

    def testGetFilterScaleFactor(self):
        scaleFactor = self.dataSource.getFilterScaleFactor()
        self.assertEqual(scaleFactor, 1000000, "getFilterScaleFactor")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()