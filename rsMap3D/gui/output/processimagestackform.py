'''
 Copyright (c) 2016, UChicago Argonne, LLC
 See LICENSE file.
'''
import PyQt4.QtGui as qtGui
import PyQt4.QtCore as qtCore

from rsMap3D.gui.output.abstractgridoutputform import AbstractGridOutputForm
from rsMap3D.gui.rsm3dcommonstrings import BROWSE_STR, SAVE_DIR_STR, WARNING_STR
from rsMap3D.gui.qtsignalstrings import CLICKED_SIGNAL, EDIT_FINISHED_SIGNAL,\
    CURRENT_INDEX_CHANGED_SIGNAL
from rsMap3D.gui.rsmap3dsignals import SET_FILE_NAME_SIGNAL
import os
from rsMap3D.mappers.output.imagestackwriter import ImageStackWriter

class ProcessImageStackForm(AbstractGridOutputForm):
    '''
    Process grid data and output a stack of TIFF images.
    '''
    FORM_TITLE = "Image Stack Output"
    
    @staticmethod
    def createInstance(parent=None):
        '''
        A static method to create an instance of this class.  The UI selects which processor method to use 
        from a menu so this method allows creating an instance without knowing what to create ahead of time. 
        '''
        return ProcessImageStackForm(parent)
    
    def __init__(self,parent=None):
        '''
        Constructor.  Typically instances should be created by createInstance method.
        '''
        super(ProcessImageStackForm, self).__init__(parent)
        self.gridWriter = ImageStackWriter()
        layout = qtGui.QVBoxLayout()
        self.dataBox = self._createDataBox()
        controlBox = self._createControlBox()
        
        layout.addWidget(self.dataBox)
        layout.addWidget(controlBox)
        self.setLayout(layout)
        
    def _browseForOutputDirectory(self):
        '''
        Launch file browser to find location to write image files.
        '''
        if self.outputDirTxt.text() == "":
            dirName = str(qtGui.QFileDialog.getExistingDirectory(None, 
                                                              SAVE_DIR_STR))
        else:
            curName = str(self.outputDirTxt.text())
            dirName = str(qtGui.QFileDialog.getExistingDirectory(None, 
                                                              SAVE_DIR_STR,
                                                              directory = curName))
            
        if dirName != "":
            if os.path.exists(str(dirName)):
                self.outputDirTxt.setText(dirName)
                self.outputDirName = dirName
                self.outputDirTxt.emit(qtCore.SIGNAL(EDIT_FINISHED_SIGNAL))
            else:
                message = qtGui.QMessageBox()
                message.warning(self, 
                                WARNING_STR, 
                                "The specified directory does not exist")
                self.outputDirTxt.setText(dirName)
                self.outputDirName = dirName
                self.outputDirTxt.emit(qtCore.SIGNAL(EDIT_FINISHED_SIGNAL))
            if not os.access(dirName, os.W_OK):
                message = qtGui.QMessageBox()
                message.warning(self,
                                WARNING_STR,
                                "The specified directory is not writable")
                
    def _createDataBox(self):
        dataBox = super(ProcessImageStackForm, self)._createDataBox()
        layout = dataBox.layout()
        
        row = layout.rowCount()
        row += 1

        label = qtGui.QLabel("Output Directory")
        layout.addWidget(label, row,0)
        self.outputDirName = ""
        self.outputDirTxt = qtGui.QLineEdit()
        self.outputDirTxt.setText(self.outputDirName)
        layout.addWidget(self.outputDirTxt, row,1)
        self.outputDirButton = qtGui.QPushButton(BROWSE_STR)
        layout.addWidget(self.outputDirButton, row, 2)

        row += 1
        label = qtGui.QLabel("Image File Prefix")
        layout.addWidget(label, row, 0)
        self.imageFilePrefix = ""
        self.imageFilePrefixTxt = qtGui.QLineEdit()
        self.imageFilePrefixTxt.setText(self.imageFilePrefix)
        layout.addWidget(self.imageFilePrefixTxt, row,1)
        
        row += 1
        label = qtGui.QLabel("Slice Axis")
        layout.addWidget(label, row, 0)
        self.axisChoices = ["0", "1", "2"]
        self.axisSelector = qtGui.QComboBox()
        self.axisSelector.addItems(self.axisChoices)
        self.axisSelector.setCurrentIndex(self.gridWriter.getSliceIndex())
        layout.addWidget(self.axisSelector)
        
        
        self.connect(self.outputDirButton, \
                     qtCore.SIGNAL(CLICKED_SIGNAL), 
                     self._browseForOutputDirectory)
        self.connect(self.outputDirButton, \
                     qtCore.SIGNAL(EDIT_FINISHED_SIGNAL), 
                     self._editFinishedOutputDir)
        self.connect(self.outputDirTxt, \
                     qtCore.SIGNAL(EDIT_FINISHED_SIGNAL), \
                     self._editFinishedOutputDir)
        self.connect(self, qtCore.SIGNAL(SET_FILE_NAME_SIGNAL), 
                     self.outputDirTxt.setText)
        self.connect(self.imageFilePrefixTxt, \
                     qtCore.SIGNAL(EDIT_FINISHED_SIGNAL), \
                     self._editFinishedOutputDir)
        self.connect(self.axisSelector,
                     qtCore.SIGNAL(CURRENT_INDEX_CHANGED_SIGNAL),
                     self.updateSliceAxis)

        
        return dataBox
    
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
                    message = qtGui.QMessageBox()
                    message.warning(self,
                                    WARNING_STR,
                                    "The specified directory \n" +
                                    str(dirName) + 
                                    "\ndoes not exist")
        
        "process file prefix"
        if imageFilePrefix != "":
            for badChar in ['\\', '/', ':', '*', '?', '<', '>', '|']:
                if badChar in imageFilePrefix:
                    message = qtGui.QMessageBox()
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
    
                
    def updateSliceAxis(self, index):
        '''
        record changes as the axis for slicing is changed
        '''
        self.gridWriter.setSliceIndex(index)