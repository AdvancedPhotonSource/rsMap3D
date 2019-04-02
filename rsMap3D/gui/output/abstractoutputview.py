'''
 Copyright (c) 2016, 2017 UChicago Argonne, LLC
 See LICENSE file.
'''

import PyQt5.QtGui as qtGui
import PyQt5.QtWidgets as qtWidgets

from  PyQt5.QtCore import pyqtSignal as Signal
from  PyQt5.QtCore import pyqtSlot as Slot

from rsMap3D.gui.rsm3dcommonstrings import RUN_STR, CANCEL_STR
from rsMap3D.gui.rsmap3dsignals import UPDATE_PROGRESS_SIGNAL, PROCESS_SIGNAL,\
    CANCEL_PROCESS_SIGNAL, PROCESS_ERROR_SIGNAL, SET_FILE_NAME_SIGNAL


class AbstractOutputView (qtWidgets.QDialog):
    '''
    Abstract class to create a base form for providing input for processing the
    output of reciprocal space map
    '''
    #define signals to be sent from this class
    process = Signal(name=PROCESS_SIGNAL)
    cancel = Signal(name=CANCEL_PROCESS_SIGNAL)
    updateProgress = Signal(float, name=UPDATE_PROGRESS_SIGNAL)
    setFileName = Signal(str, name=SET_FILE_NAME_SIGNAL)
#     processError = Signal(str, name = PROCESS_ERROR_SIGNAL)
        
    def __init__(self, appConfig = None, **kwargs):
        '''
        Constructor
        '''
        super(AbstractOutputView,self).__init__(**kwargs)
        self.appConfig = appConfig
        self.dataBox = None
        
    @Slot()
    def _cancelProcess(self):
        '''
        Emit a signal to trigger the cancellation of processing.
        '''
        self.cancel.emit()
        
        
    def _createControlBox(self):
        '''
        Create box with the GUI controls Run & Cancel
        This provides:
            - A progress bar to track processing
            - A run button to start processing
            - A cancel button to halt processing
            Signals from the controls emit signals for container classes that 
            control the overall processing
        '''
        controlBox = qtWidgets.QGroupBox()
        controlLayout = qtWidgets.QGridLayout()
        
        # Add progress bar
        row = 0
        self.progressBar = qtWidgets.QProgressBar()
        self.progressBar.setTextVisible(True)
        self.progressBar.setValue(0)
        controlLayout.addWidget(self.progressBar,row, 1)

        # Add run button
        self.runButton = qtWidgets.QPushButton(RUN_STR)
        controlLayout.addWidget(self.runButton, row, 3)

        # Add cancel button
        self.cancelButton = qtWidgets.QPushButton(CANCEL_STR)
        self.cancelButton.setDisabled(True)
        controlLayout.addWidget(self.cancelButton, row, 4)

        # Connect signals to the controls
        self.runButton.clicked.connect(self._process)
        self.cancelButton.clicked.connect(self._cancelProcess)
        self.updateProgress.connect(self.setProgress)
#         self.processError[str].connect(self._showProcessError)
        # Finalize the layout
        controlBox.setLayout(controlLayout)
        return controlBox
    
    def _createDataBox(self):
        '''
        Add an empty container for input of processing parameters.  Since this
        class is mostly abstract, this is empty and needs an override
        '''
        dataBox = qtWidgets.QGroupBox()
        dataLayout = qtWidgets.QGridLayout()
        dataBox.setLayout(dataLayout)
        return dataBox
    
    @Slot()
    def _process(self):
        '''
        Emit a signal to trigger the start of processing.
            '''
        self.process.emit()
        
    @Slot(str)
    def _showProcessError(self, error):
        '''
        Show any errors from file processing in a message dialog.  When done, 
        toggle Load and Cancel buttons in file tab to Load Active/Cancel 
        inactive
        '''
        message = qtWidgets.QMessageBox()
        message.warning(self, \
                            "Processing Scan File Warning", \
                             str(error))
        self.processScans.setProcessRunOK.emit()
              
    @Slot(float)    
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
        self.progressBar.setRange(progressMin, progressMax)
#         self.progressBar.setMinimum(progressMin)
#         self.progressBar.setMaximum(progressMax)
        
    def setRunOK(self):
        '''
        If Run is OK the load button is enabled and the cancel button is 
        disabled
        '''
        self.runButton.setDisabled(False)
        self.cancelButton.setDisabled(True)
        self.dataBox.setDisabled(False)

    
    def setRunInfoCorrupt(self):
        '''
        If Run is OK the load button is enabled and the cancel button is 
        disabled
        '''
        self.runButton.setDisabled(True)
        self.cancelButton.setDisabled(True)
        self.dataBox.setDisabled(False)

    
    def _updateProgress(self, value):
        '''
        Send signal to update the progress bar.
        :param value: value to be put on the progress bar.
        '''
        self.updateProgress[float].emit( value)
