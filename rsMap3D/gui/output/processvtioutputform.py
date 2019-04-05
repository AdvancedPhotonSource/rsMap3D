'''
 Copyright (c) 2016, UChicago Argonne, LLC
 See LICENSE file.
'''
import logging
import PyQt5.QtGui as qtGui
import PyQt5.QtWidgets as qtWidgets

from  PyQt5.QtCore import pyqtSlot as Slot

from rsMap3D.gui.output.abstractoutputview import AbstractOutputView
from rsMap3D.gui.rsm3dcommonstrings import X_STR, Y_STR, Z_STR, BROWSE_STR,\
    WARNING_STR, SAVE_FILE_STR, VTI_FILTER_STR, BINARY_OUTPUT, ASCII_OUTPUT,\
    EMPTY_STR
import os
from rsMap3D.mappers.gridmapper import QGridMapper
from rsMap3D.mappers.output.vtigridwriter import VTIGridWriter
#from PyQt4.Qt import QComboBox
from rsMap3D.config.rsmap3dlogging import METHOD_ENTER_STR, METHOD_EXIT_STR
logger = logging.getLogger(__name__)

class ProcessVTIOutputForm(AbstractOutputView):
    FORM_TITLE = "VTI Grid Output"
    
    @staticmethod
    def createInstance(parent=None, appConfig=None):
        return ProcessVTIOutputForm(parent=parent, appConfig=appConfig)
    
    def __init__(self, **kwargs):
        super(ProcessVTIOutputForm, self).__init__(**kwargs)
        logger.debug(METHOD_ENTER_STR)
        self.mapper = None
        layout = qtWidgets.QVBoxLayout()
        self.dataBox = self._createDataBox()
        controlBox = self._createControlBox()
        
        layout.addWidget(self.dataBox)
        layout.addWidget(controlBox)
        self.setLayout(layout)
        self.outputType = BINARY_OUTPUT
        logger.debug(METHOD_EXIT_STR)
        
    @Slot()
    def _browseForOutputFile(self):
        '''
        Launch file browser to select the output file.  Checks are done to make
        sure the selected directory exists and that the selected file is 
        writable
        '''
        logger.debug(METHOD_ENTER_STR)
        if self.outFileTxt.text() == EMPTY_STR:
            fileName = str(qtWidgets.QFileDialog.getSaveFileName(None, \
                                               SAVE_FILE_STR, \
                                               filter=VTI_FILTER_STR)[0])
        else:
            inFileName = str(self.outFileTxt.text())
            fileName = str(qtWidgets.QFileDialog.getSaveFileName(None, 
                                               SAVE_FILE_STR, 
                                               filter=VTI_FILTER_STR, \
                                               directory = inFileName)[0])
        if fileName != EMPTY_STR:
            if os.path.exists(os.path.dirname(str(fileName))):
                self.outFileTxt.setText(fileName)
                self.outputFileName = fileName
                self.outFileTxt.editingFinished.emit()
                self.setRunOK()
                if not os.access(os.path.dirname(fileName), os.W_OK):
                    message = qtWidgets.QMessageBox()
                    message.warning(self, \
                                 WARNING_STR, \
                                 "The specified file is not writable")
                    self.setRunInfoCorrupt()
            else:
                message = qtWidgets.QMessageBox()
                message.warning(self, \
                             WARNING_STR, \
                             "The specified directory does not exist")
                #self.outFileTxt.setText(fileName)
                self.outputFileName = fileName
                #self.outFileTxt.editingFinished.emit()
                self.setRunInfoCorrupt()
        else:
            self.outputFileName = EMPTY_STR
            self.setOutFileText(EMPTY_STR)
            self.setRunOK()
        logger.debug(METHOD_EXIT_STR)
#     @Slot()
#     def _cancelProcess(self):
#         '''
#         Emit a signal to trigger the cancellation of processing.
#         '''
#         self.cancel.emit(qtCore.SIGNAL(CANCEL_PROCESS_SIGNAL))
        

    def _createDataBox(self):
        '''
        Create Widgets to collect output info
        '''
        logger.debug(METHOD_ENTER_STR)
        dataBox = super(ProcessVTIOutputForm, self)._createDataBox()
        dataLayout = dataBox.layout()
        row = dataLayout.rowCount()
        
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

        row += 1
        label = qtWidgets.QLabel("Output Type")
        dataLayout.addWidget(label, row, 0)
        self.outputTypeSelect = qtWidgets.QComboBox()
        self.outputTypeSelect.addItem(BINARY_OUTPUT)
        self.outputTypeSelect.addItem(ASCII_OUTPUT)
        dataLayout.addWidget(self.outputTypeSelect, row, 2)
        
        self.outputFileButton.clicked.connect(self._browseForOutputFile)
#         self.connect(self.outputFileButton, \
#                      qtCore.SIGNAL(EDIT_FINISHED_SIGNAL), 
#                      self._editFinishedOutputFile)
        self.outFileTxt.editingFinished.connect(self._editFinishedOutputFile)
        self.setFileName[str].connect( self.setOutFileText)
        self.outputTypeSelect.currentIndexChanged[str]. \
            connect(self._selectedTypeChanged)
        logger.debug(METHOD_EXIT_STR)
        return dataBox
        
    @Slot()
    def _editFinishedOutputFile(self):
        '''
        When editing is finished the a check is done to make sure that the 
        directory exists and the file is writable
        '''
        logger.debug(METHOD_ENTER_STR)
        fileName = str(self.outFileTxt.text())
        if fileName != EMPTY_STR:
            if os.path.exists(os.path.dirname(fileName)):
                self.outputFileName = fileName
            else:
                if os.path.dirname(fileName) == EMPTY_STR:
                    curDir = os.path.realpath(os.path.curdir)
                    fileName = str(os.path.join(curDir, fileName))
                    self.setFileName.emit(fileName)
                    self.setRunOK()
                else:
                    self.setRunInfoCorrupt()
                    message = qtWidgets.QMessageBox()
                    message.warning(self, \
                                 WARNING_STR, \
                                 "The specified directory \n" + \
                                 str(os.path.dirname(fileName)) + \
                                 "\ndoes not exist")
                    logger.debug.warning("The specified directory \n" + \
                                 str(os.path.dirname(fileName)) + \
                                 "\ndoes not exist")
                    return
#               self.outputFileName = fileName
                
            if not os.access(os.path.dirname(fileName), os.W_OK):
                message = qtWidgets.QMessageBox()
                message.warning(self, \
                             WARNING_STR, \
                             "The specified file is not writable")
        else:
            self.outputFileName = EMPTY_STR
            self.outFileTxt.setText(EMPTY_STR)
            self.setRunOK()
        logger.debug(METHOD_EXIT_STR)
#     @Slot()
#     def _process(self):
#         '''
#         Emit a signal to trigger the start of processing.
#         '''
#         self.emit(qtCore.SIGNAL(PROCESS_SIGNAL))
        
    def runMapper(self, dataSource, transform, gridWriter=None):
        '''
        Run the selected mapper
        '''
        logger.debug(METHOD_ENTER_STR)
        self.dataSource = dataSource
        nx = int(self.xDimTxt.text())
        ny = int(self.yDimTxt.text())
        nz = int(self.zDimTxt.text())
        logger.debug( "nx,ny,nz %d,%d,%d" % (nx, ny, nz))
        outType = self.outputType
        if self.outputFileName == "":
            self.outputFileName = os.path.join(dataSource.projectDir,  \
                                               "%s.vti" %dataSource.projectName)
            self.setFileName[str].emit(self.outputFileName)
        if os.access(os.path.dirname(self.outputFileName), os.W_OK):
            self.mapper = QGridMapper(dataSource, \
                                     self.outputFileName, \
                                     outType, \
                                     nx=nx, ny=ny, nz=nz, \
                                     transform = transform, \
                                     gridWriter = gridWriter,
                                     appConfig=self.appConfig)
            self.mapper.setGridWriter(VTIGridWriter())
            self.mapper.setProgressUpdater(self._updateProgress)
            self.mapper.doMap()
        else:
            self.processError.emit("The specified directory \n" + \
                                   str(os.path.dirname(self.outputFileName)) + \
                                   "\nis not writable")
        logger.debug(METHOD_EXIT_STR)
        
    @Slot(str)
    def _selectedTypeChanged(self, typeStr):
        logger.debug(METHOD_ENTER_STR)
        self.outputType = str(typeStr)
        logger.debug(METHOD_EXIT_STR)
        
    @Slot(str)
    def setOutFileText(self, outFile):
        logger.debug(METHOD_ENTER_STR)
        self.outFileTxt.setText(outFile)
        self.outFileTxt.editingFinished.emit()
        
    def _stopMapper(self):
        '''
        Halt the mapping _process
        '''
        logger.debug(METHOD_ENTER_STR)
        self.mapper.stopMap()
        logger.debug(METHOD_EXIT_STR)
        
        