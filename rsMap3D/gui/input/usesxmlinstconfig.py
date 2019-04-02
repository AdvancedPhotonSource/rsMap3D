'''
 Copyright (c) 2017, UChicago Argonne, LLC
 See LICENSE file.
'''
import logging
from rsMap3D.config.rsmap3dlogging import METHOD_ENTER_STR, METHOD_EXIT_STR
logger = logging.getLogger(__name__)

import PyQt5.QtGui as qtGui
import PyQt5.QtCore as qtCore
import PyQt5.QtWidgets as qtWidgets
from PyQt5.QtCore import pyqtSlot
import os

from rsMap3D.gui.input.abstractfileview import AbstractFileView
from rsMap3D.gui.rsm3dcommonstrings import EMPTY_STR,\
    SELECT_INSTRUMENT_CONFIG_TITLE, INSTRUMENT_CONFIG_FILE_FILTER, BROWSE_STR,\
    WARNING_STR
from rsMap3D.exception.rsmap3dexception import InstConfigException
from rsMap3D.datasource.InstForXrayutilitiesReader import InstForXrayutilitiesReader

class UsesXMLInstConfig(AbstractFileView):
    def __init__(self, parent=None, **kwargs):
        '''
        constructor
        '''
        logger.debug(METHOD_ENTER_STR)
        super(UsesXMLInstConfig, self).__init__(parent, **kwargs)
        self.projectionDirection = None
        self.instFileOk = False
        logger.debug(METHOD_EXIT_STR)
        
#    @pyqtSlot(bool)
    def _browseForInstFile(self, checked):
        '''
        Launch file selection dialog for instrument file.
        '''
        logger.debug(METHOD_ENTER_STR)
        if self.instConfigTxt.text() == EMPTY_STR:
            fileName = qtWidgets.QFileDialog.getOpenFileName(None, 
                                        SELECT_INSTRUMENT_CONFIG_TITLE, 
                                        filter=INSTRUMENT_CONFIG_FILE_FILTER)[0]
        else:
            fileDirectory = os.path.dirname(str(self.instConfigTxt.text()))
            fileName = qtWidgets.QFileDialog.getOpenFileName(None, 
                                        SELECT_INSTRUMENT_CONFIG_TITLE, 
                                        filter=INSTRUMENT_CONFIG_FILE_FILTER, \
                                        directory = fileDirectory)[0]
        if fileName != EMPTY_STR:
            self.instConfigTxt.setText(fileName)
            # use new style to emit edit finished signal
            self.instConfigTxt.editingFinished.emit()
        logger.debug(METHOD_EXIT_STR)

    def _createInstConfig(self, layout, row):
        
        logger.debug(METHOD_ENTER_STR)
        label = qtWidgets.QLabel("Instrument Config File:");
        self.instConfigTxt = qtWidgets.QLineEdit()
        self.instConfigFileButton = qtWidgets.QPushButton(BROWSE_STR)
        layout.addWidget(label, row, 0)
        layout.addWidget(self.instConfigTxt, row, 1)
        layout.addWidget(self.instConfigFileButton, row, 2)
        # switched to using new style signals
        self.instConfigFileButton.clicked.connect(self._browseForInstFile)
        self.instConfigTxt.editingFinished.connect(self._instConfigChanged)
        logger.debug(METHOD_EXIT_STR)

    def getInstConfigName(self):
        '''
        Return the Instrument config file name
        '''
        logger.debug(METHOD_ENTER_STR)
        logger.debug(METHOD_EXIT_STR)
        return self.instConfigTxt.text()

    def _instConfigChanged(self):
        '''
        When the inst config file name changes check to make sure we have a 
        valid file (if not empty) and the check to see if it is OK to enable
        the Load button.  Also, grab the projection direction from the file.
        '''
        logger.debug(METHOD_ENTER_STR)
        logger.debug("Entering _instConfigChanged")
        if self.instFileExists() or \
           self.instConfigTxt.text() == EMPTY_STR:
            self.checkOkToLoad()
            if self.instConfigTxt.text() != EMPTY_STR:
                try:
                    # if you can get projection direction inst config is likely 
                    # a well formed instConfigFile
                    self.instFileOk = self.isInstFileOK()
                except InstConfigException :
                    message = qtWidgets.QMessageBox()
                    message.warning(self, \
                                    WARNING_STR, \
                                     "Trouble getting the projection direction " + \
                                     "from the instrument config file.")
        else:
            message = qtWidgets.QMessageBox()
            message.warning(self, \
                            WARNING_STR, \
                             "The filename entered for the instrument " + \
                             "configuration is invalid")
        logger.debug(METHOD_EXIT_STR)
        
    def instFileExists(self):
        logger.debug(METHOD_ENTER_STR)
        logger.debug(METHOD_EXIT_STR)
        
        return os.path.isfile(self.instConfigTxt.text())
    
    def isInstFileOK(self):
        logger.debug(METHOD_ENTER_STR)
        instFileExists = self.instFileExists()
        try:
            self.updateProjectionDirection()
        except InstConfigException:
            # If this fails the file is not likely a well formed inst config
            return False
        logger.debug(METHOD_EXIT_STR)
        return instFileExists
    
    def updateProjectionDirection(self):
        '''
        update the stored value for the projection direction
        '''
        logger.debug(METHOD_ENTER_STR)
        instConfig = \
            InstForXrayutilitiesReader(self.instConfigTxt.text())
        self.projectionDirection = instConfig.getProjectionDirection()
        logger.debug(METHOD_EXIT_STR)
        
