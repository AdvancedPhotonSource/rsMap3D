'''
 Copyright (c) 2016, UChicago Argonne, LLC
 See LICENSE file.
'''
import PyQt5.QtGui as qtGui
import PyQt5.QtCore as qtCore
import PyQt5.QtWidgets as qtWidgets

from  PyQt5.QtCore import pyqtSlot as Slot

from rsMap3D.gui.output.abstractgridoutputform import AbstractGridOutputForm
from rsMap3D.gui.rsm3dcommonstrings import BROWSE_STR, SAVE_DIR_STR, WARNING_STR,\
    BINARY_OUTPUT
import os
from rsMap3D.mappers.output.imagestackwriter import ImageStackWriter

class ProcessImageStackForm(AbstractGridOutputForm):
    '''
    Process grid data and output a stack of TIFF images.
    '''
    FORM_TITLE = "Image Stack Output"
    
    @staticmethod
    def createInstance(parent=None, appConfig=None):
        '''
        A static method to create an instance of this class.  The UI selects which processor method to use 
        from a menu so this method allows creating an instance without knowing what to create ahead of time. 
        '''
        return ProcessImageStackForm(parent=parent, appConfig=appConfig)

    def __init__(self, **kwargs):
        '''
        Constructor.  Typically instances should be created by createInstance method.
        '''
        super(ProcessImageStackForm, self).__init__(**kwargs)
        self.gridWriter = ImageStackWriter()
        layout = qtWidgets.QVBoxLayout()
        self.dataBox = self._createDataBox()
        controlBox = self._createControlBox()
        
        layout.addWidget(self.dataBox)
        layout.addWidget(controlBox)
        self.setLayout(layout)
        self.outputType = BINARY_OUTPUT
        
    @Slot()
    def _browseForOutputDirectory(self):
        '''
        Launch file browser to find location to write image files.
        '''
        if self.outputDirTxt.text() == "":
            dirName = str(qtWidgets.QFileDialog.getExistingDirectory(None, 
                                                              SAVE_DIR_STR)[0])
        else:
            curName = str(self.outputDirTxt.text())
            dirName = str(qtWidgets.QFileDialog.getExistingDirectory(None, 
                                                              SAVE_DIR_STR,
                                                              directory = curName)[0])
            
        if dirName != "":
            if os.path.exists(str(dirName)):
                self.outputDirTxt.setText(dirName)
                self.outputDirName = dirName
                self.outputDirTxt.editingFinished.emit()
            else:
                message = qtWidgets.QMessageBox()
                message.warning(self, 
                                WARNING_STR, 
                                "The specified directory does not exist")
                self.outputDirTxt.setText(dirName)
                self.outputDirName = dirName
                self.outputDirTxt.editingFinished.emit()
            if not os.access(dirName, os.W_OK):
                message = qtWidgets.QMessageBox()
                message.warning(self,
                                WARNING_STR,
                                "The specified directory is not writable")
                
    def _createDataBox(self):
        dataBox = super(ProcessImageStackForm, self)._createDataBox()
        layout = dataBox.layout()
        
        row = layout.rowCount()
        row += 1

        label = qtWidgets.QLabel("Output Directory")
        layout.addWidget(label, row,0)
        self.outputDirName = ""
        self.outputDirTxt = qtWidgets.QLineEdit()
        self.outputDirTxt.setText(self.outputDirName)
        layout.addWidget(self.outputDirTxt, row,1)
        self.outputDirButton = qtWidgets.QPushButton(BROWSE_STR)
        layout.addWidget(self.outputDirButton, row, 2)

        row += 1
        label = qtWidgets.QLabel("Image File Prefix")
        layout.addWidget(label, row, 0)
        self.imageFilePrefix = ""
        self.imageFilePrefixTxt = qtWidgets.QLineEdit()
        self.imageFilePrefixTxt.setText(self.imageFilePrefix)
        layout.addWidget(self.imageFilePrefixTxt, row,1)
        
        row += 1
        label = qtWidgets.QLabel("Slice Axis")
        layout.addWidget(label, row, 0)
        self.axisChoices = ["0", "1", "2"]
        self.axisSelector = qtWidgets.QComboBox()
        self.axisSelector.addItems(self.axisChoices)
        self.axisSelector.setCurrentIndex(self.gridWriter.getSliceIndex())
        layout.addWidget(self.axisSelector)
        
        #Connect signals for this class        
        self.outputDirButton.clicked.connect(self._browseForOutputDirectory)
#         self.connect(self.outputDirButton, \
#                      qtCore.SIGNAL(EDIT_FINISHED_SIGNAL), 
#                      self._editFinishedOutputDir)
        self.outputDirTxt.editingFinished.connect(self._editFinishedOutputDir)
        self.setFileName[str].connect(self.outputDirTxt.setText)
        self.imageFilePrefixTxt.editingFinished.connect(
            self._editFinishedOutputDir)
        self.axisSelector.currentIndexChanged[int].connect(self.updateSliceAxis)

        
        return dataBox
    
    @Slot()
    def _editFinishedOutputDir(self):
        '''
        Process output directory name as inputs are completed.
        '''
        dirName = str(self.outputDirTxt.text())
        imageFilePrefix = str(self.imageFilePrefixTxt.text())
        
        "process directory"
        if dirName != "":
            if os.path.exists(dirName):    #use specified dir if it exists
                self.outputDirName = dirName
            else:                          #use current path
                if dirName == "":
                    dirName = os.path.realpath(os.path.curdir)
                else:
                    message = qtWidgets.QMessageBox()
                    message.warning(self,
                                    WARNING_STR,
                                    "The specified directory \n" +
                                    str(dirName) + 
                                    "\ndoes not exist")
        
        "process file prefix"
        if imageFilePrefix != "":
            for badChar in ['\\', '/', ':', '*', '?', '<', '>', '|']:
                if badChar in imageFilePrefix:
                    message = qtWidgets.QMessageBox()
                    message.warning(self,
                                    WARNING_STR,
                                    "The specified imagePrefix conatins one " +
                                    "of the following invalid characters \/:*?<>|")
            else:
                self.imageFilePrefix = imageFilePrefix
                
    def getOutputFileName(self):
        '''
        Override from base class.  In this case return a join of two of the inputs.  This is used to 
        provide info during runMapper method.
        '''
        return os.path.join(self.outputDirName, self.imageFilePrefix)
    
                
    @Slot(int)
    def updateSliceAxis(self, index):
        '''
        record changes as the axis for slicing is changed
        '''
        self.gridWriter.setSliceIndex(index)