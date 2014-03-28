'''
Created on Mar 28, 2014

@author: hammonds
'''
import unittest
from rsMap3D.datasource.InstForXrayutilitiesReader import \
    InstForXrayutilitiesReader

class Test(unittest.TestCase):


    def setUp(self):
        self.config = InstForXrayutilitiesReader('../resources/33BM-instForXrayutilities.xml')
        #self.config2 = 

    def tearDown(self):
        pass


    def testGetMonitorName(self):
        monitorName = self.config.getMonitorName()
        self.assertEquals(monitorName, "I0", "getMonitorName")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testGetMonitorName']
    unittest.main()
    
    
