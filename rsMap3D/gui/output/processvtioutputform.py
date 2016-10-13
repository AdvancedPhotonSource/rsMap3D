'''
 Copyright (c) 2016, UChicago Argonne, LLC
 See LICENSE file.
'''
import PyQt4.QtGui as qtGui
import PyQt4.QtCore as qtCore
from rsMap3D.gui.rsm3dcommonstrings import BROWSE_STR, WARNING_STR, \
    SAVE_FILE_STR, VTI_FILTER_STR
from rsMap3D.gui.qtsignalstrings import CLICKED_SIGNAL, EDIT_FINISHED_SIGNAL
from rsMap3D.gui.rsmap3dsignals import SET_FILE_NAME_SIGNAL, PROCESS_ERROR_SIGNAL
import os
from rsMap3D.mappers.gridmapper import QGridMapper
from rsMap3D.mappers.output.vtigridwriter import VTIGridWriter
from rsMap3D.gui.output.abstractgridoutputform import AbstractGridOutputForm

class ProcessVTIOutputForm(AbstractGridOutputForm):
    '''
    Process Grid data into a .vti file.  This class uses VTIGridWriter class.  
    '''
    FORM_TITLE = "VTI Grid Output"
    
    @staticmethod
    def createInstance(parent=None):
        '''
        A static method to create an instance of this class.  The UI selects which processor method to use 
        from a menu so this method allows creating an instance without knowing what to create ahead of time. 
        '''
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
            

    def _createDataBox(self):
        '''
        Create Widgets to collect output info
        '''
        dataBox = super(ProcessVTIOutputForm, self)._createDataBox()
        layout = dataBox.layout()

#         row = layout.rowCount()
#         row += 1
#         self._createGridDimensionInput(layout, row)        

        row = layout.rowCount()
        row += 1
        label = qtGui.QLabel("Output File")
        layout.addWidget(label, row,0)
        self.outputFileName = ""
        self.outFileTxt = qtGui.QLineEdit()
        self.outFileTxt.setText(self.outputFileName)
        layout.addWidget(self.outFileTxt, row,1)
        self.outputFileButton = qtGui.QPushButton(BROWSE_STR)
        layout.addWidget(self.outputFileButton, row, 2)

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

