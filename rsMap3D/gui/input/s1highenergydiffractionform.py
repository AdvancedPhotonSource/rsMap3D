'''
 Copyright (c) 2017, UChicago Argonne, LLC
 See LICENSE file.
'''
import os
import logging
from rsMap3D.gui.rsm3dcommonstrings import LOGGER_NAME
logger = logging.getLogger(LOGGER_NAME + '.gui.input.xpcsspecscanfileform ')

import PyQt4.QtGui as qtGui
import PyQt4.QtCore as qtCore

from rsMap3D.gui.input.abstractimageperfileview import AbstractImagePerFileView

from rsMap3D.gui.output.processvtioutputform import ProcessVTIOutputForm
from rsMap3D.gui.input.usesxmldetectorconfig import UsesXMLDetectorConfig
from rsMap3D.gui.input.usesxmlinstconfig import UsesXMLInstConfig
from rsMap3D.gui.rsm3dcommonstrings import BROWSE_STR, EMPTY_STR, WARNING_STR,\
    OK_TO_LOAD

IMAGE_DIR_DIALOG_TITLE = "Select Image Directory"    


class S1HighEnergyDiffractionForm(AbstractImagePerFileView, \
                                  UsesXMLDetectorConfig, UsesXMLInstConfig):
    '''
    This class presents information for selecting input files
    '''
    FORM_TITLE = "Sector 1 High Energy Diffraction"
    HED_IMAGE_FILE_TITLE = "HED Image File"
    HED_IMAGE_FILE_FILTER = "S1 corrected files *.par"

    @staticmethod
    def createInstance(parent=None):
        return S1HighEnergyDiffractionForm(parent)
    
    def __init__(self, parent=None):
        '''
         constructor
         '''
        super(S1HighEnergyDiffractionForm, self).__init__(parent)
        self.fileDialogTitle = self.HED_IMAGE_FILE_TITLE
        self.fileDialogFilter = self.HED_IMAGE_FILE_FILTER
        
        self.dataBox = self._createDataBox()
        controlBox =  self._createControlBox()
        
        self.layout.addWidget(self.dataBox)
        self.layout.addWidget(controlBox)
        self.setLayout(self.layout)
        
    @qtCore.pyqtSlot()
    def _browseForImageDir(self):
        logger.debug("Entering _browseForImageDir")
        if self.imageDirTxt.text() == EMPTY_STR:
            fileName = qtGui.QFileDialog.getExistingDirectory(None, \
                                                   IMAGE_DIR_DIALOG_TITLE)
        else:
            fileDirectory = os.path.dirname(str(self.imageDirTxt.text()))
            fileName = qtGui.QFileDialog.getExistingDirectory(None,\
                                                   IMAGE_DIR_DIALOG_TITLE, \
                                                   directory = fileDirectory)
            
        if fileName != EMPTY_STR:
            self.imageDirTxt.setText(fileName)
            self.imageDirTxt.editingFinished.emit()
        logger.debug("Entering _browseForImageDir")
    
    def checkOkToLoad(self):
        logger.debug("Entering checkOkToLoad")
        okToLoad = False
        projFileOK = AbstractImagePerFileView.checkOkToLoad(self)
        instFileOK = self.isInstFileOK()
        detFileOK = self.isDetFileOk()
        imageDirOK = os.path.isdir(self.imageDirTxt.text()) 
        if projFileOK and instFileOK and detFileOK and imageDirOK:
            okToLoad = True
        self.emit(qtCore.SIGNAL(OK_TO_LOAD), okToLoad)
            
        logger.debug("Leaving checkOkToLoad")
        return okToLoad
    

    def _createDataBox(self):
        dataBox = super(S1HighEnergyDiffractionForm,self)._createDataBox()
#        logging.debug ("Create S1 DataBox")
        dataLayout = dataBox.layout()
        
        row = dataLayout.rowCount()
        self._createInstConfig(dataLayout, row)
        
        row = dataLayout.rowCount() + 1
        self._createDetConfig(dataLayout, row)
    
        row = dataLayout.rowCount()  + 1
        self._createDetectorROIInput(dataLayout, row)
        
        row = dataLayout.rowCount()  + 1
        label = qtGui.QLabel("Image Directory:")
        self.imageDirTxt = qtGui.QLineEdit()
        self.imageDirBrowseButton = qtGui.QPushButton(BROWSE_STR)
        dataLayout.addWidget(label, row, 0)
        dataLayout.addWidget(self.imageDirTxt, row, 1)
        dataLayout.addWidget(self.imageDirBrowseButton, row, 2)
        
        self.imageDirBrowseButton.clicked.connect(self._browseForImageDir)
        self.imageDirTxt.editingFinished.connect(self._imageDirChanged)

        logger.debug("Done creating S1 dataBox")

        return dataBox
    
    def getDataSource(self):
        logger.debug("Entering getDataSource")

        logger.debug("Leaving getDataSource")

    def getOutputForms(self):
        logger.debug("Entering getOutputForms")

        outputForms = []
        outputForms.append(ProcessVTIOutputForm)
        logger.debug("Leaving getOutputForms")
        return outputForms

    @qtCore.pyqtSlot()
    def _imageDirChanged(self):
        logger.debug("Entering _imageDirChanged")
        if os.path.isdir(self.imageDirTxt.text()) or \
            self.imageDirTxt.text() == EMPTY_STR:
            self.checkOkToLoad()
        else:
            message = qtGui.QMessageBox() 
            message.warning(self, \
                             WARNING_STR
                             , \
                             "The IMM file entered is invalid")
        logger.debug("Leaving getOutputForms")
