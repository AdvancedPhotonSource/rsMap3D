'''
 Copyright (c) 2014, UChicago Argonne, LLC
 See LICENSE file.
'''
import PyQt5.QtGui as qtGui
import PyQt5.QtCore as qtCore
import PyQt5.QtWidgets as qtWidgets

from rsMap3D.gui.rsm3dcommonstrings import CANCEL_STR, LOAD_STR, OK_TO_LOAD
from rsMap3D.gui.rsmap3dsignals import LOAD_FILE_SIGNAL, CANCEL_LOAD_FILE_SIGNAL,\
    UPDATE_PROGRESS_SIGNAL
from rsMap3D.exception.rsmap3dexception import RSMap3DException
import logging
from rsMap3D.config.rsmap3dlogging import METHOD_ENTER_STR, METHOD_EXIT_STR
logger = logging.getLogger(__name__)

class AbstractFileView(qtWidgets.QDialog):
    '''
    classdocs
    '''
    POLE_MAP_STR = "Stereographic Projection"
    SIMPLE_GRID_MAP_STR = "qx,qy,qz Map"

    #Set up Signals that are created in this class
    cancelLoadFile = qtCore.pyqtSignal(name=CANCEL_LOAD_FILE_SIGNAL)
    loadFile = qtCore.pyqtSignal(name=LOAD_FILE_SIGNAL)
    okToLoad = qtCore.pyqtSignal(bool, name=OK_TO_LOAD)
    updateProgressSignal = qtCore.pyqtSignal(float, float, \
                                      name=UPDATE_PROGRESS_SIGNAL)
    

    def __init__(self, parent=None, appConfig=None, *kwargs):
        '''
        Constructor
        '''
        logger.debug(METHOD_ENTER_STR  % str(parent) + " " + str(appConfig))        
        super(AbstractFileView, self).__init__(parent)
        self.layout = qtWidgets.QVBoxLayout()
        self.appConfig = appConfig
        if not (appConfig is None):
            self.appConfig = appConfig
        else:
            raise RSMap3DException("no AppConfig object received.")
        logger.debug(METHOD_EXIT_STR)
        

    @qtCore.pyqtSlot()
    def _cancelLoadFile(self):
        ''' Send signal to cancel a file load'''
        self.cancelLoadFile.emit()
        
    def _createControlBox(self):
        '''
        Create Layout holding controls widgets
        '''
        controlBox = qtWidgets.QGroupBox()
        self.controlLayout = qtWidgets.QGridLayout()       
        row =0
        self.progressBar = qtWidgets.QProgressBar()
        self.progressBar.setTextVisible(True)
        self.controlLayout.addWidget(self.progressBar, row, 1)
        
        row += 1
        self.loadButton = qtWidgets.QPushButton(LOAD_STR)        
        self.loadButton.setDisabled(True)
        self.controlLayout.addWidget(self.loadButton, row, 1)
        self.cancelButton = qtWidgets.QPushButton(CANCEL_STR)        
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
        dataBox = qtWidgets.QGroupBox()
        dataLayout = qtWidgets.QGridLayout()

        dataBox.setLayout(dataLayout)
        return dataBox
    
    @qtCore.pyqtSlot()
    def _loadFile(self):
        '''
        Emit a signal to start loading data
        '''
        self.loadFile.emit()

    @qtCore.pyqtSlot(bool)
    def processOkToLoad(self, okToLoad):
        if okToLoad:
            self.loadButton.setEnabled(True)
        else:
            self.loadButton.setDisabled(True)
            
    @qtCore.pyqtSlot(float, float)
    def setProgress(self, value, maxValue):
        '''
        Set the value to be displayed in the progress bar.
        '''
        logger.debug(METHOD_ENTER_STR % str((value,maxValue)))
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
        
    @qtCore.pyqtSlot()
    def setCancelOK(self):
        '''
        If Cancel is OK the load button is disabled and the cancel button is 
        enabled
        '''
        self.loadButton.setDisabled(True)
        self.cancelButton.setDisabled(False)
        self.dataBox.setDisabled(True)

    @qtCore.pyqtSlot()
    def setLoadOK(self):
        '''
        If Load is OK the load button is enabled and the cancel button is 
        disabled
        '''
        self.loadButton.setDisabled(False)
        self.cancelButton.setDisabled(True)
        self.dataBox.setDisabled(False)

