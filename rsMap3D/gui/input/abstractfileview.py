'''
 Copyright (c) 2014, UChicago Argonne, LLC
 See LICENSE file.
'''
import PyQt4.QtGui as qtGui
import PyQt4.QtCore as qtCore
from rsMap3D.gui.qtsignalstrings import CLICKED_SIGNAL
from rsMap3D.gui.rsm3dcommonstrings import CANCEL_STR, LOAD_STR
from rsMap3D.gui.rsmap3dsignals import LOAD_FILE_SIGNAL, CANCEL_LOAD_FILE_SIGNAL,\
    UPDATE_PROGRESS_SIGNAL

class AbstractFileView(qtGui.QDialog):
    '''
    classdocs
    '''
    POLE_MAP_STR = "Stereographic Projection"
    SIMPLE_GRID_MAP_STR = "qx,qy,qz Map"


    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(AbstractFileView, self).__init__(parent)
        self.layout = qtGui.QVBoxLayout()

    def _cancelLoadFile(self):
        ''' Send signal to cancel a file load'''
        self.emit(qtCore.SIGNAL(CANCEL_LOAD_FILE_SIGNAL))
        
    def _createControlBox(self):
        '''
        Create Layout holding controls widgets
        '''
        controlBox = qtGui.QGroupBox()
        self.controlLayout = qtGui.QGridLayout()       
        row =0
        self.progressBar = qtGui.QProgressBar()
        self.progressBar.setTextVisible(True)
        self.controlLayout.addWidget(self.progressBar, row, 1)
        
        row += 1
        self.loadButton = qtGui.QPushButton(LOAD_STR)        
        self.loadButton.setDisabled(True)
        self.controlLayout.addWidget(self.loadButton, row, 1)
        self.cancelButton = qtGui.QPushButton(CANCEL_STR)        
        self.cancelButton.setDisabled(True)
        self.controlLayout.addWidget(self.cancelButton, row, 2)

        self.connect(self.loadButton, \
                     qtCore.SIGNAL(CLICKED_SIGNAL), \
                     self._loadFile)
        self.connect(self.cancelButton, \
                     qtCore.SIGNAL(CLICKED_SIGNAL), \
                     self._cancelLoadFile)
        self.connect(self, \
                     qtCore.SIGNAL(UPDATE_PROGRESS_SIGNAL), \
                     self.setProgress)

        controlBox.setLayout(self.controlLayout)
        return controlBox

    def _createDataBox(self):
        '''
        Create widgets for collecting data
        '''
        dataBox = qtGui.QGroupBox()
        dataLayout = qtGui.QGridLayout()

        dataBox.setLayout(dataLayout)
        return dataBox
        
    
    def _loadFile(self):
        '''
        Emit a signal to start loading data
        '''
        self.emit(qtCore.SIGNAL(LOAD_FILE_SIGNAL))

    def setProgress(self, value, maxValue):
        '''
        Set the value to be displayed in the progress bar.
        '''
        self.progressBar.setMinimum(1)
        self.progressBar.setMaximum(maxValue)
        self.progressBar.setValue(value)
        
    def setProgressLimits(self, minVal, maxVal):
        '''
        Set the limits on the progress bar
        '''
        self.progressBar.setMinimum(minVal)
        self.progressBar.setMaximum(maxVal)
        
    def updateProgress(self, value, maxValue):
        '''
        Emit a signal to update the progress bar
        '''
        self.emit(qtCore.SIGNAL(UPDATE_PROGRESS_SIGNAL), value, maxValue)
        
    def setCancelOK(self):
        '''
        If Cancel is OK the load button is disabled and the cancel button is 
        enabled
        '''
        self.loadButton.setDisabled(True)
        self.cancelButton.setDisabled(False)
        self.dataBox.setDisabled(True)

    def setLoadOK(self):
        '''
        If Load is OK the load button is enabled and the cancel button is 
        disabled
        '''
        self.loadButton.setDisabled(False)
        self.cancelButton.setDisabled(True)
        self.dataBox.setDisabled(False)

