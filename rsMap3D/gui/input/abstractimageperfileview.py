'''
 Copyright (c) 2014, UChicago Argonne, LLC
 See LICENSE file.
'''
import logging
from rsMap3D.config.rsmap3dlogging import METHOD_EXIT_STR, METHOD_ENTER_STR
logger = logging.getLogger(__name__)

import PyQt5.QtGui as qtGui
import PyQt5.QtWidgets as qtWidgets
import PyQt5.QtCore as qtCore

from  PyQt5.QtCore import pyqtSlot as Slot

import os.path
import abc

from rsMap3D.gui.input.abstractfileview import AbstractFileView
from rsMap3D.gui.rsm3dcommonstrings import WARNING_STR, BROWSE_STR, EMPTY_STR

class AbstractImagePerFileView(AbstractFileView):
    '''
    classdocs
    '''


    def __init__(self, **kwargs):
        '''
        Constructor
        '''
        logger.debug(METHOD_ENTER_STR  % str(kwargs))
        super(AbstractImagePerFileView, self).__init__(**kwargs)
        self.fileDialogTitle = "Dummy File Dialog"
        self.fileDialogFilter = ""
        logger.debug(METHOD_EXIT_STR)

    @Slot()
    def _browseForProjectDir(self):
        '''
        Launch file selection dialog for instrument file.
        '''
        logger.debug(METHOD_ENTER_STR)
        if self.projNameTxt.text() == EMPTY_STR:
            fileName = qtWidgets.QFileDialog.getOpenFileName(None, \
                                                   self.fileDialogTitle, \
                                                   filter=self.fileDialogFilter)[0]
        else:
            fileDirectory = os.path.dirname(str(self.projNameTxt.text()))
            fileName = qtWidgets.QFileDialog.getOpenFileName(None,\
                                                   self.fileDialogTitle, \
                                                   directory = fileDirectory,
                                                   filter=self.fileDialogFilter)[0]
            
        logger.debug("Filename: %s" % ((fileName,)))
        if fileName != EMPTY_STR:
            self.projNameTxt.setText(fileName)
            self.projNameTxt.editingFinished.emit()
        logger.debug(METHOD_EXIT_STR)
        
    @Slot()
    def checkOkToLoad(self):
        '''
        Make sure we have valid file names for project, instrument config, 
        and the detector config.  If we do enable load button.  If not disable
        the load button
        '''
        logger.debug(METHOD_ENTER_STR)
        if os.path.isfile(str(self.projNameTxt.text())):
            retVal = True
        else:
            if str(self.projNameTxt.text()) != "":
                logger.warning("Project file name is invalid")
            retVal = False
        logger.debug("Enter " + str(retVal))
        return retVal 
    
    def _createControlBox(self):
        '''
        Create Layout holding controls widgets
        '''
        logger.debug(METHOD_ENTER_STR)
        logger.debug(METHOD_EXIT_STR)
        return super(AbstractImagePerFileView, self)._createControlBox()
        
    def _createDataBox(self):
        '''
        Create widgets for collecting data
        '''
        logger.debug(METHOD_ENTER_STR)
        dataBox = super(AbstractImagePerFileView, self)._createDataBox()
        dataLayout = dataBox.layout()
        row = dataLayout.rowCount()
        label = qtWidgets.QLabel("Project File:");
        self.projNameTxt = qtWidgets.QLineEdit()
        self.projectDirButton = qtWidgets.QPushButton(BROWSE_STR)
        dataLayout.addWidget(label, row, 0)
        dataLayout.addWidget(self.projNameTxt, row, 1)
        dataLayout.addWidget(self.projectDirButton, row, 2)

        # Add Signals between widgets
        self.projectDirButton.clicked.connect(self._browseForProjectDir)
        self.projNameTxt.editingFinished.connect(self._projectDirChanged)
        logger.debug(METHOD_EXIT_STR)
        return dataBox
    
    
    @abc.abstractmethod
    def getOutputForms(self):
        ''' 
        Return a list of appropriate output forms for use in the process 
        scan controller
        '''
        logger.debug(METHOD_ENTER_STR)
        outputForms = []
        logger.debug(METHOD_EXIT_STR % str(outputForms))
        return outputForms
    
    def getProjectDir(self):
        '''
        Return the project directory
        '''
        logger.debug(METHOD_ENTER_STR)
        logger.debug(METHOD_EXIT_STR )
        return os.path.dirname(str(self.projNameTxt.text()))
        
    def getProjectExtension(self):
        '''
        Return the project file extension
        '''
        logger.debug(METHOD_ENTER_STR)
        logger.debug(METHOD_EXIT_STR )
        return os.path.splitext(os.path.basename(str(self.projNameTxt.text())))[1]

    def getProjectName(self):
        '''
        Return the project name
        '''
        logger.debug(METHOD_ENTER_STR)
        logger.debug(METHOD_EXIT_STR )
        return os.path.splitext(os.path.basename(str(self.projNameTxt.text())))[0]
    
    @Slot()
    def _projectDirChanged(self):
        '''
        When the project name changes, check to see if it is valid file and 
        then check to see if it is OK to enable the Load button.
        '''
        logger.debug(METHOD_ENTER_STR)
        if os.path.isfile(self.projNameTxt.text()) or \
            self.projNameTxt.text() == EMPTY_STR:
            self.checkOkToLoad()
        else:
            logger.warning("The project directory entered is invalid")
            message = qtWidgets.QMessageBox()
            message.warning(self, \
                             WARNING_STR, \
                             "The project directory entered is invalid")
        logger.debug(METHOD_EXIT_STR )
