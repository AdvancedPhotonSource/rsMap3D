'''
 Copyright (c) 2017 UChicago Argonne, LLC
 See LICENSE file.
'''
import sys
import unittest
import PyQt5.QtGui as qtGui
import PyQt5.QtCore as qtCore
import PyQt5.QtWidgets as qtWidgets
import PyQt5.QtTest as qtTest

from rsMap3D.gui.output.abstractoutputview import AbstractOutputView as AOutView

app = qtWidgets.QApplication(sys.argv)

class TestAbstractOutputView(unittest.TestCase):
    def setUp(self):
        self.form = TestFileView(parent=None)

    def test_defaults(self):
        print (dir(self.form))
        self.assertEqual(self.form.runButton.isEnabled(), True)
        self.assertEqual(self.form.cancelButton.isEnabled(), False)
        self.assertEqual(self.form.progressBar.value(), 0)
        self.assertEqual(self.form.progressBar.minimum(), 0)
        self.assertEqual(self.form.progressBar.value(), 0)
        
    def test_setCancelOK(self):
        self.form.setCancelOK()
        self.assertEqual(self.form.runButton.isEnabled(), False)
        self.assertEqual(self.form.cancelButton.isEnabled(), True)
        self.assertEqual(self.form.dataBox.isEnabled(), False)
        
    def test_setRunOK(self):
        self.form.setRunOK()
        self.assertEqual(self.form.runButton.isEnabled(), True)
        self.assertEqual(self.form.cancelButton.isEnabled(), False)
        self.assertEqual(self.form.dataBox.isEnabled(), True)
        
    def test_setClickRunWithRunOK(self):
        self.form.setRunOK()
        runButton = self.form.runButton
        qtTest.QTest.mouseClick(runButton, qtCore.Qt.LeftButton)
        # When using version 5 add test with QSignalSpy.    
        
    def test_setClickRunWithCancelOK(self):
        self.form.setCancelOK()
        runButton = self.form.runButton
        qtTest.QTest.mouseClick(runButton, qtCore.Qt.LeftButton)
        # When using version 5 add test with QSignalSpy.    
        
    def test_setClickCancelWithRunOK(self):
        self.form.setRunOK()
        cancelButton = self.form.cancelButton
        qtTest.QTest.mouseClick(cancelButton, qtCore.Qt.LeftButton)
        # When using version 5 add test with QSignalSpy.    
        
    def test_setClickCancelWithCancelOK(self):
        self.form.setCancelOK()
        cancelButton = self.form.cancelButton
        qtTest.QTest.mouseClick(cancelButton, qtCore.Qt.LeftButton)
        # When using version 5 add test with QSignalSpy.    

    def test_setProgressLimits(self):
        progressMin1 = 0
        progressMax1 = 100
        progressMin2 = 10
        progressMax2 = 1000
        progressMin3 = 100
        progressMax3 = 50
        
        self.form.setProgressLimits(progressMin1, progressMax1)
        self.assertEqual(self.form.progressBar.minimum(), progressMin1)
        self.assertEqual(self.form.progressBar.maximum(), progressMax1)

        self.form.setProgressLimits(progressMin2, progressMax2)
        self.assertEqual(self.form.progressBar.minimum(), progressMin2)
        self.assertEqual(self.form.progressBar.maximum(), progressMax2)

        self.form.setProgressLimits(progressMin3, progressMax3)
        self.assertEqual(self.form.progressBar.minimum(), progressMin3)
        self.assertEqual(self.form.progressBar.maximum(), progressMin3)

    def test_setProgress(self):
        progressMin1 = 0
        progressMax1 = 100
        progressMin2 = 10
        progressMax2 = 1000
        progressMin3 = 100
        progressMax3 = 50
        progress1 = 3
        progress2 = 50
        progress3 = 101
        progress4 = 3.0
        
        
        self.form.setProgressLimits(progressMin1, progressMax1)
        self.form.setProgress(progress1)
        self.assertEqual(self.form.progressBar.value(), progress1)
        self.form.setProgress(progress2)
        self.assertEqual(self.form.progressBar.value(), progress2)
        self.form.setProgress(progress3)
        self.assertEqual(self.form.progressBar.value(), progress2)
        self.form.setProgress(progress4)
        self.assertEqual(self.form.progressBar.value(), progress1)

        self.form.setProgressLimits(progressMin2, progressMax2)
        self.assertEqual(self.form.progressBar.minimum(), progressMin2)
        self.assertEqual(self.form.progressBar.maximum(), progressMax2)

        self.form.setProgressLimits(progressMin3, progressMax3)
        self.assertEqual(self.form.progressBar.minimum(), progressMin3)
        self.assertEqual(self.form.progressBar.maximum(), progressMin3)
        
class TestFileView(AOutView):
    def __init__(self, parent=None):
        super(TestFileView,self).__init__(parent)
        layout = qtWidgets.QVBoxLayout()
        self.dataBox = self._createDataBox()
        controlBox = self._createControlBox()
        
        layout.addWidget(self.dataBox)
        layout.addWidget(controlBox)
        self.setLayout(layout)
        
    
if __name__ == "__main__":
    unittest.main()
