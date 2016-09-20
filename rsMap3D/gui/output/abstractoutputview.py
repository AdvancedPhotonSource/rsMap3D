'''
 Copyright (c) 2014, UChicago Argonne, LLC
 See LICENSE file.
'''

import PyQt4.QtGui as qtGui
import PyQt4.QtCore as qtCore
from rsMap3D.gui.rsm3dcommonstrings import RUN_STR, CANCEL_STR
from rsMap3D.gui.qtsignalstrings import CLICKED_SIGNAL
from rsMap3D.gui.rsmap3dsignals import UPDATE_PROGRESS_SIGNAL


class AbstractOutputView (qtGui.QDialog):
    
    def __init__(self, parent=None):
        super(AbstractOutputView,self).__init__(parent)
        
        
    def _createControlBox(self):
        '''
        Create box wih the GUI controls Run & Cancel
        '''
        controlBox = qtGui.QGroupBox()
        controlLayout = qtGui.QGridLayout()
        row = 0
        self.progressBar = qtGui.QProgressBar()
        controlLayout.addWidget(self.progressBar,row, 1)

        self.runButton = qtGui.QPushButton(RUN_STR)
        controlLayout.addWidget(self.runButton, row, 3)

        self.cancelButton = qtGui.QPushButton(CANCEL_STR)
        self.cancelButton.setDisabled(True)

        controlLayout.addWidget(self.cancelButton, row, 4)

        self.connect(self.runButton, \
                     qtCore.SIGNAL(CLICKED_SIGNAL), \
                     self._process)
        self.connect(self.cancelButton, \
                     qtCore.SIGNAL(CLICKED_SIGNAL), \
                     self._cancelProcess)
        self.connect(self, \
                     qtCore.SIGNAL(UPDATE_PROGRESS_SIGNAL), \
                     self.setProgress)
        controlBox.setLayout(controlLayout)
        return controlBox
    
    def _createDataBox(self):
        dataBox = qtGui.QGroupBox()
        dataLayout = qtGui.QGridLayout()
        dataBox.setLayout(dataLayout)
        return dataBox
    
    def setProgress(self, value):
        '''
        Set the value in the progress bar
        :param value: value to write to the progress bar
        '''
        self.progressBar.setValue(value)
        
    def setCancelOK(self):
        '''
        If Cancel is OK the run button is disabled and the cancel button is 
        enabled
        '''
        self.runButton.setDisabled(True)
        self.cancelButton.setDisabled(False)
        self.dataBox.setDisabled(True)

    def setProgressLimits(self, progressMin, progressMax):
        '''
        Set the limits on the progress bar.
        :param progressMin: Minimum value to store in the progress bar
        :param progressMax: Maximum value to store in the progress bar
        '''
        self.progressBar.setMinimum(progressMin)
        self.progressBar.setMaximum(progressMax)
        
    def setRunOK(self):
        '''
        If Run is OK the load button is enabled and the cancel button is 
        disabled
        '''
        self.runButton.setDisabled(False)
        self.cancelButton.setDisabled(True)
        self.dataBox.setDisabled(False)

    def updateProgress(self, value):
        '''
        Send signal to update the progress bar.
        :param value: value to be put on the progress bar.
        '''
        self.emit(qtCore.SIGNAL(UPDATE_PROGRESS_SIGNAL), value)
