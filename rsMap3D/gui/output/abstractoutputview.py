'''
 Copyright (c) 2016, UChicago Argonne, LLC
 See LICENSE file.
'''

import PyQt4.QtGui as qtGui
import PyQt4.QtCore as qtCore
from rsMap3D.gui.rsm3dcommonstrings import RUN_STR, CANCEL_STR
from rsMap3D.gui.qtsignalstrings import CLICKED_SIGNAL
from rsMap3D.gui.rsmap3dsignals import UPDATE_PROGRESS_SIGNAL, PROCESS_SIGNAL,\
    CANCEL_PROCESS_SIGNAL


class AbstractOutputView (qtGui.QDialog):
    '''
    Abstract class to create a base form for providing input for processing the
    output of reciprocal space map
    '''
    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(AbstractOutputView,self).__init__(parent)
        self.dataBox = None
        
    def _cancelProcess(self):
        '''
        Emit a signal to trigger the cancellation of processing.
        '''
        self.emit(qtCore.SIGNAL(CANCEL_PROCESS_SIGNAL))
        
        
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
        controlBox = qtGui.QGroupBox()
        controlLayout = qtGui.QGridLayout()
        
        # Add progress bar
        row = 0
        self.progressBar = qtGui.QProgressBar()
        self.progressBar.setTextVisible(True)
        controlLayout.addWidget(self.progressBar,row, 1)

        # Add run button
        self.runButton = qtGui.QPushButton(RUN_STR)
        controlLayout.addWidget(self.runButton, row, 3)

        # Add cancel button
        self.cancelButton = qtGui.QPushButton(CANCEL_STR)
        self.cancelButton.setDisabled(True)
        controlLayout.addWidget(self.cancelButton, row, 4)

        # Connect signals to the controls
        self.connect(self.runButton, \
                     qtCore.SIGNAL(CLICKED_SIGNAL), \
                     self._process)
        self.connect(self.cancelButton, \
                     qtCore.SIGNAL(CLICKED_SIGNAL), \
                     self._cancelProcess)
        self.connect(self, \
                     qtCore.SIGNAL(UPDATE_PROGRESS_SIGNAL), \
                     self.setProgress)
        # Finalize the layout
        controlBox.setLayout(controlLayout)
        return controlBox
    
    def _createDataBox(self):
        '''
        Add an empty container for input of processing parameters.  Since this
        class is mostly abstract, this is empty and needs an override
        '''
        dataBox = qtGui.QGroupBox()
        dataLayout = qtGui.QGridLayout()
        dataBox.setLayout(dataLayout)
        return dataBox
    
    def _process(self):
        '''
        Emit a signal to trigger the start of processing.
        '''
        self.emit(qtCore.SIGNAL(PROCESS_SIGNAL))
        
        
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
