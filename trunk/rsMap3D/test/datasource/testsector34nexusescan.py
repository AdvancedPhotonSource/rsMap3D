'''
Created on Sep 5, 2014

@author: hammonds
'''
import unittest
from rsMap3D.datasource.sector34nexusescansource import Sector34NexusEscanSource

FILE_BASE_DIR = '../../resources/34-id-escan/'
DETECTOR_CONFIG_FILE = FILE_BASE_DIR + 'geoN_for_Ptdots.xml'

class Test(unittest.TestCase):


    def setUp(self):
        self.projectDir = "/home/oxygen/HAMMONDS/test_data_Escan_RSM"
        self.projectName = "Escan_Pt_dotB_-15V"
        self.projectExtension = ".h5"
        self.detConfigFile = DETECTOR_CONFIG_FILE


    def tearDown(self):
        pass


    def testLoadSource(self):
        dataSource = Sector34NexusEscanSource(self.projectDir, \
                                              self.projectName, \
                                              self.projectExtension, \
                                              self.detConfigFile)
        dataSource.loadSource()
        print dataSource.rho
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()