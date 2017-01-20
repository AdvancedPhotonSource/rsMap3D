'''
 Copyright (c) 2014, UChicago Argonne, LLC
 See LICENSE file.
'''
import PyQt4.QtGui as qtGui
from PyQt4.QtCore import pyqtSignal, pyqtSlot

from rsMap3D.gui.rsm3dcommonstrings import CANCEL_STR, LOAD_STR, OK_TO_LOAD
from rsMap3D.gui.rsmap3dsignals import LOAD_FILE_SIGNAL, CANCEL_LOAD_FILE_SIGNAL,\
    UPDATE_PROGRESS_SIGNAL

class AbstractFileView(qtGui.QDialog):
    '''
    classdocs
    '''
    POLE_MAP_STR = "Stereographic Projection"
    SIMPLE_GRID_MAP_STR = "qx,qy,qz Map"

    #Set up Signals that are created in this class
    cancelLoadFile = pyqtSignal(name=CANCEL_LOAD_FILE_SIGNAL)
    loadFile = pyqtSignal(name=LOAD_FILE_SIGNAL)
    okToLoad = pyqtSignal(bool, name=OK_TO_LOAD)
    updateProgressSignal = pyqtSignal(float, float, \
                                      name=UPDATE_PROGRESS_SIGNAL)
    

    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(AbstractFileView, self).__init__(parent)
        self.layout = qtGui.QVBoxLayout()

    @pyqtSlot()
    def _cancelLoadFile(self):
        ''' Send signal to cancel a file load'''
        self.cancelLoadFile.emit()
        
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

        self.loadButton.clicked.connect(self._loadFile)
        self.cancelButton.clicked.connect(self._cancelLoadFile)
        self.updateProgressSignal.connect(self.setProgress)
        self.okToLoad.connect(self.processOkToLoad)

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
    
    @pyqtSlot()
    def _loadFile(self):
        '''
        Emit a signal to start loading data
        '''
        print "_loadFile emitting loadFile signal"
        self.loadFile.emit()

    @pyqtSlot(bool)
    def processOkToLoad(self, okToLoad):
        if okToLoad:
            self.loadButton.setEnabled(True)
        else:
            self.loadButton.setDisabled(True)
            
    @pyqtSlot(float, float)
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
        self.updateProgressSignal.emit(value, maxValue)
        
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

