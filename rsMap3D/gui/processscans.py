'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''
import os

import PyQt5.QtGui as qtGui
import PyQt5.QtCore as qtCore
import PyQt5.QtWidgets as qtWidgets

from rsMap3D.mappers.gridmapper import QGridMapper
from rsMap3D.gui.qtsignalstrings import CLICKED_SIGNAL, EDIT_FINISHED_SIGNAL
from rsMap3D.gui.rsmap3dsignals import CANCEL_PROCESS_SIGNAL,\
    UPDATE_PROGRESS_SIGNAL, SET_FILE_NAME_SIGNAL, PROCESS_SIGNAL,\
    PROCESS_ERROR_SIGNAL
from rsMap3D.gui.rsm3dcommonstrings import WARNING_STR, BROWSE_STR, X_STR, Y_STR,\
    CANCEL_STR, RUN_STR, Z_STR, VTI_FILTER_STR, SAVE_FILE_STR


class ProcessScans(qtWidgets.QDialog):
    '''
    This class presents a form to select to start analysis.  This display
    allows switching between Grid map and pole figure.
    '''
    def __init__(self, parent=None):
        '''
        Constructor - Layout widgets on the page & link up actions.
        '''
        super(ProcessScans, self).__init__(parent)
        self.Mapper = None
        layout = qtWidgets.QVBoxLayout()

        self.dataBox = self._createDataBox()
        controlBox = self._createControlBox()
        

        layout.addWidget(self.dataBox)
        layout.addWidget(controlBox)
        self.setLayout(layout)                    
        
        
        
    def _browseForOutputFile(self):
        '''
        Launch file browser to select the output file.  Checks are done to make
        sure the selected directory exists and that the selected file is 
        writable
        '''
        if self.outFileTxt.text() == "":
            fileName = str(qtWidgets.QFileDialog.getSaveFileName(None, \
                                               SAVE_FILE_STR, \
                                               filter=VTI_FILTER_STR))
        else:
            inFileName = str(self.outFileTxt.text())
            fileName = str(qtWidgets.QFileDialog.getSaveFileName(None, 
                                               SAVE_FILE_STR, 
                                               filter=VTI_FILTER_STR, \
                                               directory = inFileName))
        if fileName != "":
            if os.path.exists(os.path.dirname(str(fileName))):
                self.outFileTxt.setText(fileName)
                self.outputFileName = fileName
                self.outFileTxt.emit(qtCore.SIGNAL(EDIT_FINISHED_SIGNAL))
            else:
                message = qtWidgets.QMessageBox()
                message.warning(self, \
                             WARNING_STR, \
                             "The specified directory does not exist")
                self.outFileTxt.setText(fileName)
                self.outputFileName = fileName
                self.outFileTxt.emit(qtCore.SIGNAL(EDIT_FINISHED_SIGNAL))
            if not os.access(os.path.dirname(fileName), os.W_OK):
                message = qtWidgets.QMessageBox()
                message.warning(self, \
                             WARNING_STR, \
                             "The specified file is not writable")
            
    def _cancelProcess(self):
        '''
        Emit a signal to trigger the cancellation of processing.
        '''
        self.emit(qtCore.SIGNAL(CANCEL_PROCESS_SIGNAL))
        
    def _createControlBox(self):
        '''
        Create box wih the GUI controls Run & Cancel
        '''
        controlBox = qtWidgets.QGroupBox()
        controlLayout = qtWidgets.QGridLayout()
        row = 0
        self.progressBar = qtWidgets.QProgressBar()
        controlLayout.addWidget(self.progressBar,row, 1)

        self.runButton = qtWidgets.QPushButton(RUN_STR)
        controlLayout.addWidget(self.runButton, row, 3)

        self.cancelButton = qtWidgets.QPushButton(CANCEL_STR)
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
        '''
        Create Sub Layout for data gathering widgets
        '''
        dataBox = qtWidgets.QGroupBox()
        dataLayout = qtWidgets.QGridLayout()
        row = 0       

        label = qtWidgets.QLabel("Grid Dimensions")
        dataLayout.addWidget(label, row,0)
        row += 1
        label = qtWidgets.QLabel(X_STR)
        dataLayout.addWidget(label, row,0)
        self.xDimTxt = qtWidgets.QLineEdit()
        self.xDimTxt.setText("200")
        self.xDimValidator = qtGui.QIntValidator()
        self.xDimTxt.setValidator(self.xDimValidator)
        dataLayout.addWidget(self.xDimTxt, row,1)
        
        row += 1
        label = qtWidgets.QLabel(Y_STR)
        dataLayout.addWidget(label, row,0)
        self.yDimTxt = qtWidgets.QLineEdit()
        self.yDimTxt.setText("200")
        self.yDimValidator = qtGui.QIntValidator()
        self.yDimTxt.setValidator(self.yDimValidator)
        dataLayout.addWidget(self.yDimTxt, row,1)
        
        row += 1
        label = qtWidgets.QLabel(Z_STR)
        dataLayout.addWidget(label, row,0)
        self.zDimTxt = qtWidgets.QLineEdit()
        self.zDimTxt.setText("200")
        self.zDimValidator = qtGui.QIntValidator()
        self.zDimTxt.setValidator(self.zDimValidator)
        dataLayout.addWidget(self.zDimTxt, row,1)
        
        row += 1
        label = qtWidgets.QLabel("Output File")
        dataLayout.addWidget(label, row,0)
        self.outputFileName = ""
        self.outFileTxt = qtWidgets.QLineEdit()
        self.outFileTxt.setText(self.outputFileName)
        dataLayout.addWidget(self.outFileTxt, row,1)
        self.outputFileButton = qtWidgets.QPushButton(BROWSE_STR)
        dataLayout.addWidget(self.outputFileButton, row, 2)

        self.connect(self.outputFileButton, \
                     qtCore.SIGNAL(CLICKED_SIGNAL), 
                     self._browseForOutputFile)
        self.connect(self.outputFileButton, \
                     qtCore.SIGNAL(EDIT_FINISHED_SIGNAL), 
                     self._editFinishedOutputFile)
        self.connect(self.outFileTxt, \
                     qtCore.SIGNAL(EDIT_FINISHED_SIGNAL), \
                     self._editFinishedOutputFile)
        self.connect(self, qtCore.SIGNAL(SET_FILE_NAME_SIGNAL), 
                     self.outFileTxt.setText)
        
        dataBox.setLayout(dataLayout)
        return dataBox
        
    def _editFinishedOutputFile(self):
        '''
        When editing is finished the a check is done to make sure that the 
        directory exists and the file is writable
        '''
        fileName = str(self.outFileTxt.text())
        if fileName != "":
            if os.path.exists(os.path.dirname(fileName)):
                self.outputFileName = fileName
            else:
                if os.path.dirname(fileName) == "":
                    curDir = os.path.realpath(os.path.curdir)
                    fileName = str(os.path.join(curDir, fileName))
                else:
                    message = qtWidgets.QMessageBox()
                    message.warning(self, \
                                 WARNING_STR, \
                                 "The specified directory \n" + \
                                 str(os.path.dirname(fileName)) + \
                                 "\ndoes not exist")
                
#               self.outputFileName = fileName
                self.emit(qtCore.SIGNAL(SET_FILE_NAME_SIGNAL), fileName)
                
            if not os.access(os.path.dirname(fileName), os.W_OK):
                message = qtWidgets.QMessageBox()
                message.warning(self, \
                             WARNING_STR, \
                             "The specified file is not writable")

    def _process(self):
        '''
        Emit a signal to trigger the start of processing.
        '''
        self.emit(qtCore.SIGNAL(PROCESS_SIGNAL))
        
    def runMapper(self, dataSource, transform):
        '''
        Run the selected mapper
        '''
        self.dataSource = dataSource
        nx = int(self.xDimTxt.text())
        ny = int(self.yDimTxt.text())
        nz = int(self.zDimTxt.text())
        if self.outputFileName == "":
            self.outputFileName = os.path.join(dataSource.projectDir,  \
                                               "%s.vti" %dataSource.projectName)
            self.emit(qtCore.SIGNAL(SET_FILE_NAME_SIGNAL), self.outputFileName)
        if os.access(os.path.dirname(self.outputFileName), os.W_OK):
            self.mapper = QGridMapper(dataSource, \
                                     self.outputFileName, \
                                     nx=nx, ny=ny, nz=nz,
                                     transform = transform,
                                     appConfig=self.appConfig)
            self.mapper.setProgressUpdater(self.updateProgress)
            self.mapper.doMap()
        else:
            self.emit(qtCore.SIGNAL(PROCESS_ERROR_SIGNAL), \
                         "The specified directory \n" + \
                         str(os.path.dirname(self.outputFileName)) + \
                         "\nis not writable")

    def setCancelOK(self):
        '''
        If Cancel is OK the run button is disabled and the cancel button is 
        enabled
        '''
        self.runButton.setDisabled(True)
        self.cancelButton.setDisabled(False)
        self.dataBox.setDisabled(True)

    def setOutFileName(self, name):
        '''
        Write a filename to the text widget and to the stored output file name
        :param name: Name of output file
        '''
        self.outFileTxt.setText(name)
        self.outputFileName = name
        
    def setProgress(self, value):
        '''
        Set the value in the progress bar
        :param value: value to write to the progress bar
        '''
        self.progressBar.setValue(value)
        
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
        
    def _stopMapper(self):
        '''
        Halt the mapping _process
        '''
        self.mapper.stopMap()
        
    def updateProgress(self, value):
        '''
        Send signal to update the progress bar.
        :param value: value to be put on the progress bar.
        '''
        self.emit(qtCore.SIGNAL(UPDATE_PROGRESS_SIGNAL), value)
        