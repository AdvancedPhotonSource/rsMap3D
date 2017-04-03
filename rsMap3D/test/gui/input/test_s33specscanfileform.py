'''
 Copyright (c) 2017, UChicago Argonne, LLC
 See LICENSE file.
'''
import sys
import unittest
import PyQt4.QtGui as qtGui
import PyQt4.QtCore as qtCore
import PyQt4.QtTest as qtTest
from rsMap3D.gui.input.s33specscanfileform import S33SpecScanFileForm
from rsMap3D.config.rsmap3dconfigparser import RSMap3DConfigParser

app = qtGui.QApplication(sys.argv)


class TestS33SpecScanFileForm(unittest.TestCase):


    def setUp(self):
        self.appConfig = RSMap3DConfigParser()


    def tearDown(self):
        form = None
        form = S33SpecScanFileForm.createInstance(parent=None, appConfig=self.appConfig)
        self.assertIsNot(form, None)

    def testCreateForm(self):
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()