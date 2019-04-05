'''
 Copyright (c) 2016, UChicago Argonne, LLC
 See LICENSE file.
'''
import PyQt5.QtGui as qtGui
import PyQt5.QtCore as qtCore
import PyQt5.QtWidgets as qtWidgets

from  PyQt5.QtCore import pyqtSignal as Signal
from  PyQt5.QtCore import pyqtSlot as Slot

from rsMap3D.gui.rsm3dcommonstrings import SAVE_FILE_STR, WARNING_STR,\
    BROWSE_STR
import os
from rsMap3D.gui.qtsignalstrings import EDIT_FINISHED_SIGNAL, CLICKED_SIGNAL
from rsMap3D.gui.rsmap3dsignals import SET_FILE_NAME_SIGNAL
from rsMap3D.mappers.xpcsgridlocationmapper import XPCSGridLocationMapper
from rsMap3D.gui.output.abstractgridoutputform import AbstractGridOutputForm
from rsMap3D.mappers.output.xpcsgridlocationwriter import XPCSGridLocationWriter


class ProcessXpcsGridLocationForm(AbstractGridOutputForm):
    '''
    Process and output only the grid locations (qx,qy,qz or H, K, L)
    for the detector.  For XPCS runs, only one location of the 
    detector so the output is three blocks, the size of the detector 
    for each of the grid axes. 
    '''
    FORM_TITLE= "XPCS Grid Locations"
    XPCS_GRID_LOCS_FILTER = "*.csv"
    
    @staticmethod
    def createInstance(parent=None, appConfig=None):
        '''
        A static method to create an instance of this class.  The UI selects which processor method to use 
        from a menu so this method allows creating an instance without knowing what to create ahead of time. 
        '''
        return ProcessXpcsGridLocationForm(parent=parent, appConfig=appConfig)
    
    def __init__(self, **kwargs):
        super(ProcessXpcsGridLocationForm, self).__init__(**kwargs)
        self.mapper = None
        layout = qtWidgets.QVBoxLayout()
        self.dataBox = self._createDataBox()
        controlBox = self._createControlBox()
        
        layout.addWidget(self.dataBox)
        layout.addWidget(controlBox)
        self.setLayout(layout)
        self.outFilter = self.XPCS_GRID_LOCS_FILTER
        self.gridWriter = XPCSGridLocationWriter()
        
    @Slot()
    def _browseForOutputFile(self):
        '''
        Launch file browser to select the output file.  Checks are done to make
        sure the selected directory exists and that the selected file is 
        writable
        '''
        if self.outFileTxt.text() == "":
            fileName = str(qtWidgets.QFileDialog.getSaveFileName(None, \
                                               SAVE_FILE_STR, \
                                               filter=self.outFilter)[0])
        else:
            inFileName = str(self.outFileTxt.text())
            fileName = str(qtWidgets.QFileDialog.getSaveFileName(None, 
                                               SAVE_FILE_STR, 
                                               filter=self.outFilter, \
                                               directory = inFileName)[0])
        if fileName != "":
            if os.path.exists(os.path.dirname(str(fileName))):
                self.outFileTxt.setText(fileName)
                self.outputFileName = fileName
                self.outFileTxt.editingFinished.emit()
            else:
                message = qtWidgets.QMessageBox()
                message.warning(self, \
                             WARNING_STR, \
                             "The specified directory does not exist")
                self.outFileTxt.setText(fileName)
                self.outputFileName = fileName
                self.outFileTxt.editingFinished.emit()
            if not os.access(os.path.dirname(fileName), os.W_OK):
                message = qtWidgets.QMessageBox()
                message.warning(self, \
                             WARNING_STR, \
                             "The specified file is not writable")
            
    def _createDataBox(self):
        dataBox = super(ProcessXpcsGridLocationForm,self)._createDataBox()
        layout = dataBox.layout()
        
        row = layout.rowCount()
        row += 1
        label = qtWidgets.QLabel("Output File")
        layout.addWidget(label, row,0)
        self.outputFileName = ""
        self.outFileTxt = qtWidgets.QLineEdit()
        self.outFileTxt.setText(self.outputFileName)
        layout.addWidget(self.outFileTxt, row,1)
        self.outputFileButton = qtWidgets.QPushButton(BROWSE_STR)
        layout.addWidget(self.outputFileButton, row, 2)

        self.outputFileButton.clicked.connect(self._browseForOutputFile)
#         self.connect(self.outputFileButton, \
#                      qtCore.SIGNAL(EDIT_FINISHED_SIGNAL), 
#                      self._editFinishedOutputFile)
        self.outFileTxt.editingFinished.connect(self._editFinishedOutputFile)
        self.setFileName[str].connect(self.outFileTxt.setText)

        return dataBox
    
    @Slot()
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
                self.setFileName.emit(fileName)
                
            if not os.access(os.path.dirname(fileName), os.W_OK):
                message = qtWidgets.QMessageBox()
                message.warning(self, \
                             WARNING_STR, \
                             "The specified file is not writable")

    def runMapper(self, dataSource, transform):
        self.dataSource = dataSource
        self.transform = transform
        
        nx = int(self.xDimTxt.text())
        ny = int(self.yDimTxt.text())
        nz = int(self.zDimTxt.text())
        
        self.outputFileName = self.getOutputFileName()

        if self.outputFileName == "":
            self.outputFileName = os.path.join(dataSource.projectDir,  \
                "%s%s" %(dataSource.projectName,self.gridWriter.FILE_EXTENSION) )
            self.setFileName.emit(self.outputFileName)
    
        if os.access(os.path.dirname(self.outputFileName), os.W_OK):
            self.mapper = XPCSGridLocationMapper(dataSource,
                                              self.outputFileName,
                                              nx=nx, ny=ny, nz=nz,
                                              transform = transform,
                                              gridWriter = self.gridWriter,
                                              appConfig = self.appConfig)
            self.mapper.setProgressUpdater(self._updateProgress)
            self.mapper.doMap()

    def stopMapper(self):
        '''
        Halt the mapping _process
        '''
        self.mapper.stopMap()
    