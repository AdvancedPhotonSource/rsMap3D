'''
 Copyright (c) 2016, UChicago Argonne, LLC
 See LICENSE file.
'''
import PyQt4.QtGui as qtGui
import PyQt4.QtCore as qtCore
from rsMap3D.gui.output.abstractoutputview import AbstractOutputView
from rsMap3D.gui.rsm3dcommonstrings import X_STR, Y_STR, Z_STR, BROWSE_STR,\
    WARNING_STR, SAVE_FILE_STR, VTI_FILTER_STR, BINARY_OUTPUT, ASCII_OUTPUT
from rsMap3D.gui.qtsignalstrings import CLICKED_SIGNAL, EDIT_FINISHED_SIGNAL,\
    CURRENT_INDEX_CHANGED_SIGNAL
from rsMap3D.gui.rsmap3dsignals import SET_FILE_NAME_SIGNAL, PROCESS_SIGNAL,\
    CANCEL_PROCESS_SIGNAL, PROCESS_ERROR_SIGNAL
import os
from rsMap3D.mappers.gridmapper import QGridMapper
from rsMap3D.mappers.output.vtigridwriter import VTIGridWriter
from PyQt4.Qt import QComboBox

class ProcessVTIOutputForm(AbstractOutputView):
    FORM_TITLE = "VTI Grid Output"
    
    @staticmethod
    def createInstance(parent=None):
        return ProcessVTIOutputForm()
    
    def __init__(self, parent=None):
        super(ProcessVTIOutputForm, self).__init__(parent)
        self.mapper = None
        layout = qtGui.QVBoxLayout()
        self.dataBox = self._createDataBox()
        controlBox = self._createControlBox()
        
        layout.addWidget(self.dataBox)
        layout.addWidget(controlBox)
        self.setLayout(layout)
        self.outputType = BINARY_OUTPUT
        
    def _browseForOutputFile(self):
        '''
        Launch file browser to select the output file.  Checks are done to make
        sure the selected directory exists and that the selected file is 
        writable
        '''
        if self.outFileTxt.text() == "":
            fileName = str(qtGui.QFileDialog.getSaveFileName(None, \
                                               SAVE_FILE_STR, \
                                               filter=VTI_FILTER_STR))
        else:
            inFileName = str(self.outFileTxt.text())
            fileName = str(qtGui.QFileDialog.getSaveFileName(None, 
                                               SAVE_FILE_STR, 
                                               filter=VTI_FILTER_STR, \
                                               directory = inFileName))
        if fileName != "":
            if os.path.exists(os.path.dirname(str(fileName))):
                self.outFileTxt.setText(fileName)
                self.outputFileName = fileName
                self.outFileTxt.emit(qtCore.SIGNAL(EDIT_FINISHED_SIGNAL))
            else:
                message = qtGui.QMessageBox()
                message.warning(self, \
                             WARNING_STR, \
                             "The specified directory does not exist")
                self.outFileTxt.setText(fileName)
                self.outputFileName = fileName
                self.outFileTxt.emit(qtCore.SIGNAL(EDIT_FINISHED_SIGNAL))
            if not os.access(os.path.dirname(fileName), os.W_OK):
                message = qtGui.QMessageBox()
                message.warning(self, \
                             WARNING_STR, \
                             "The specified file is not writable")
            
    def _cancelProcess(self):
        '''
        Emit a signal to trigger the cancellation of processing.
        '''
        self.emit(qtCore.SIGNAL(CANCEL_PROCESS_SIGNAL))
        

    def _createDataBox(self):
        '''
        Create Widgets to collect output info
        '''
        dataBox = super(ProcessVTIOutputForm, self)._createDataBox()
        dataLayout = dataBox.layout()
        row = dataLayout.rowCount()
        
        label = qtGui.QLabel("Grid Dimensions")
        dataLayout.addWidget(label, row,0)
        row += 1
        label = qtGui.QLabel(X_STR)
        dataLayout.addWidget(label, row,0)
        self.xDimTxt = qtGui.QLineEdit()
        self.xDimTxt.setText("200")
        self.xDimValidator = qtGui.QIntValidator()
        self.xDimTxt.setValidator(self.xDimValidator)
        dataLayout.addWidget(self.xDimTxt, row,1)
        
        row += 1
        label = qtGui.QLabel(Y_STR)
        dataLayout.addWidget(label, row,0)
        self.yDimTxt = qtGui.QLineEdit()
        self.yDimTxt.setText("200")
        self.yDimValidator = qtGui.QIntValidator()
        self.yDimTxt.setValidator(self.yDimValidator)
        dataLayout.addWidget(self.yDimTxt, row,1)
        
        row += 1
        label = qtGui.QLabel(Z_STR)
        dataLayout.addWidget(label, row,0)
        self.zDimTxt = qtGui.QLineEdit()
        self.zDimTxt.setText("200")
        self.zDimValidator = qtGui.QIntValidator()
        self.zDimTxt.setValidator(self.zDimValidator)
        dataLayout.addWidget(self.zDimTxt, row,1)
        
        row += 1
        label = qtGui.QLabel("Output File")
        dataLayout.addWidget(label, row,0)
        self.outputFileName = ""
        self.outFileTxt = qtGui.QLineEdit()
        self.outFileTxt.setText(self.outputFileName)
        dataLayout.addWidget(self.outFileTxt, row,1)
        self.outputFileButton = qtGui.QPushButton(BROWSE_STR)
        dataLayout.addWidget(self.outputFileButton, row, 2)

        row += 1
        label = qtGui.QLabel("Output Type")
        dataLayout.addWidget(label, row, 0)
        self.outputTypeSelect = QComboBox()
        self.outputTypeSelect.addItem(BINARY_OUTPUT)
        self.outputTypeSelect.addItem(ASCII_OUTPUT)
        dataLayout.addWidget(self.outputTypeSelect, row, 2)
        
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
        self.connect(self.outputTypeSelect, \
                     qtCore.SIGNAL(CURRENT_INDEX_CHANGED_SIGNAL),
                     self._selectedTypeChanged)
        
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
                    message = qtGui.QMessageBox()
                    message.warning(self, \
                                 WARNING_STR, \
                                 "The specified directory \n" + \
                                 str(os.path.dirname(fileName)) + \
                                 "\ndoes not exist")
                
#               self.outputFileName = fileName
                self.emit(qtCore.SIGNAL(SET_FILE_NAME_SIGNAL), fileName)
                
            if not os.access(os.path.dirname(fileName), os.W_OK):
                message = qtGui.QMessageBox()
                message.warning(self, \
                             WARNING_STR, \
                             "The specified file is not writable")

    def _process(self):
        '''
        Emit a signal to trigger the start of processing.
        '''
        self.emit(qtCore.SIGNAL(PROCESS_SIGNAL))
        
    def runMapper(self, dataSource, transform, gridWriter=None):
        '''
        Run the selected mapper
        '''
        self.dataSource = dataSource
        nx = int(self.xDimTxt.text())
        ny = int(self.yDimTxt.text())
        nz = int(self.zDimTxt.text())
        outType = self.outputType
        if self.outputFileName == "":
            self.outputFileName = os.path.join(dataSource.projectDir,  \
                                               "%s.vti" %dataSource.projectName)
            self.emit(qtCore.SIGNAL(SET_FILE_NAME_SIGNAL), self.outputFileName)
        if os.access(os.path.dirname(self.outputFileName), os.W_OK):
            self.mapper = QGridMapper(dataSource, \
                                     self.outputFileName, \
                                     outType, \
                                     nx=nx, ny=ny, nz=nz, \
                                     transform = transform, \
                                     gridWriter = gridWriter)
            self.mapper.setGridWriter(VTIGridWriter())
            self.mapper.setProgressUpdater(self.updateProgress)
            self.mapper.doMap()
        else:
            self.emit(qtCore.SIGNAL(PROCESS_ERROR_SIGNAL), \
                         "The specified directory \n" + \
                         str(os.path.dirname(self.outputFileName)) + \
                         "\nis not writable")

    def _selectedTypeChanged(self, typeStr):
        self.outputType = str(typeStr)
        
    def _stopMapper(self):
        '''
        Halt the mapping _process
        '''
        self.mapper.stopMap()
        
        