'''
 Copyright (c) 2014, UChicago Argonne, LLC
 See LICENSE file.
'''
import PyQt4.QtGui as qtGui
import PyQt4.QtCore as qtCore

from  PyQt4.QtCore import pyqtSlot as Slot

import os.path
import abc

from rsMap3D.gui.input.abstractfileview import AbstractFileView
from rsMap3D.gui.rsm3dcommonstrings import WARNING_STR, BROWSE_STR, EMPTY_STR

class AbstractImagePerFileView(AbstractFileView):
    '''
    classdocs
    '''


    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(AbstractImagePerFileView, self).__init__(parent)
        self.fileDialogTitle = "Dummy File Dialog"
        self.fileDialogFilter = ""
        

    @Slot()
    def _browseForProjectDir(self):
        '''
        Launch file selection dialog for instrument file.
        '''
        if self.projNameTxt.text() == EMPTY_STR:
            fileName = qtGui.QFileDialog.getOpenFileName(None, \
                                                   self.fileDialogTitle, \
                                                   filter=self.fileDialogFilter)
        else:
            fileDirectory = os.path.dirname(str(self.projNameTxt.text()))
            fileName = qtGui.QFileDialog.getOpenFileName(None,\
                                                   self.fileDialogTitle, \
                                                   directory = fileDirectory,
                                                   filter=self.fileDialogFilter)
            
        if fileName != EMPTY_STR:
            self.projNameTxt.setText(fileName)
            self.projNameTxt.editingFinished.emit()

    @Slot()
    def checkOkToLoad(self):
        '''
        Make sure we have valid file names for project, instrument config, 
        and the detector config.  If we do enable load button.  If not disable
        the load button
        '''
        print("AbstractImagePerFileViewCheckOKtoLoad")
        if os.path.isfile(self.projNameTxt.text()):
            retVal = True
        else:
            retVal = False
        return retVal
    
    def _createControlBox(self):
        '''
        Create Layout holding controls widgets
        '''
        return super(AbstractImagePerFileView, self)._createControlBox()
    
    def _createDataBox(self):
        '''
        Create widgets for collecting data
        '''
        dataBox = super(AbstractImagePerFileView, self)._createDataBox()
        dataLayout = dataBox.layout()
        row = dataLayout.rowCount()
        label = qtGui.QLabel("Project File:");
        self.projNameTxt = qtGui.QLineEdit()
        self.projectDirButton = qtGui.QPushButton(BROWSE_STR)
        dataLayout.addWidget(label, row, 0)
        dataLayout.addWidget(self.projNameTxt, row, 1)
        dataLayout.addWidget(self.projectDirButton, row, 2)

        # Add Signals between widgets
        self.projectDirButton.clicked.connect(self._browseForProjectDir)
        self.projNameTxt.editingFinished.connect(self._projectDirChanged)

        return dataBox
    
    
    @abc.abstractmethod
    def getOutputForms(self):
        ''' 
        Return a list of appropriate output forms for use in the process 
        scan controller
        '''
        outputForms = []
        return outputForms
    
    def getProjectDir(self):
        '''
        Return the project directory
        '''
        return os.path.dirname(str(self.projNameTxt.text()))
        
    def getProjectExtension(self):
        '''
        Return the project file extension
        '''
        return os.path.splitext(os.path.basename(str(self.projNameTxt.text())))[1]

    def getProjectName(self):
        '''
        Return the project name
        '''
        return os.path.splitext(os.path.basename(str(self.projNameTxt.text())))[0]
    
    @Slot()
    def _projectDirChanged(self):
        '''
        When the project name changes, check to see if it is valid file and 
        then check to see if it is OK to enable the Load button.
        '''
        if os.path.isfile(self.projNameTxt.text()) or \
            self.projNameTxt.text() == EMPTY_STR:
            self.checkOkToLoad()
        else:
            message = qtGui.QMessageBox()
            message.warning(self, \
                             WARNING_STR, \
                             "The project directory entered is invalid")
