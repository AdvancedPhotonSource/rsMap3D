'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''
import logging
from rsMap3D.config.rsmap3dlogging import METHOD_ENTER_STR, METHOD_EXIT_STR
logger = logging.getLogger(__name__)

import PyQt5.QtCore as qtCore
import PyQt5.QtGui as qtGui
import PyQt5.QtWidgets as qtWidgets

from rsMap3D.gui.input.abstractimageperfileview import AbstractImagePerFileView
from rsMap3D.gui.input.usesxmlinstconfig import UsesXMLInstConfig
from rsMap3D.gui.input.usesxmldetectorconfig import UsesXMLDetectorConfig
from rsMap3D.gui.rsm3dcommonstrings import EMPTY_STR,\
    SPEC_FILE_FILTER,\
    SELECT_SPEC_FILE_TITLE
from rsMap3D.utils.srange import srange


class SpecXMLDrivenFileForm(AbstractImagePerFileView, UsesXMLInstConfig, UsesXMLDetectorConfig):

    SCAN_LIST_REGEXP = "((\d)+(-(\d)+)?\,( )?)+"

    def __init__(self, **kwargs):
        super(SpecXMLDrivenFileForm, self).__init__(**kwargs)
        logger.debug(METHOD_ENTER_STR)
        
        self.fileDialogTitle = SELECT_SPEC_FILE_TITLE
        self.fileDialogFilter = SPEC_FILE_FILTER

        self.dataBox = self._createDataBox()
        controlBox = self._createControlBox()
        
        self.layout.addWidget(self.dataBox)
        self.layout.addWidget(controlBox)
        self.setLayout(self.layout);
        logger.debug(METHOD_EXIT_STR)

    def _createHKLOutput(self, layout, row):
        logger.debug(METHOD_ENTER_STR)
        label = qtWidgets.QLabel("HKL output")
        layout.addWidget(label, row, 0)
        self.hklCheckbox = qtWidgets.QCheckBox()
        layout.addWidget(self.hklCheckbox, row, 1)
        logger.debug(METHOD_EXIT_STR)

        
    def _createOutputType(self, layout, row):
        logger.debug(METHOD_ENTER_STR)
        label = qtWidgets.QLabel("Output Type")
        self.outTypeChooser = qtWidgets.QComboBox()
        self.outTypeChooser.addItem(self.SIMPLE_GRID_MAP_STR)
        self.outTypeChooser.addItem(self.POLE_MAP_STR)
        layout.addWidget(label, row, 0)
        layout.addWidget(self.outTypeChooser, row, 1)
        self.outTypeChooser.currentIndexChanged[str].connect(self._outputTypeChanged)
#         self.connect(self.outTypeChooser, \
#                      qtCore.SIGNAL(CURRENT_INDEX_CHANGED_SIGNAL), \
#                      self._outputTypeChanged)
        logger.debug(METHOD_EXIT_STR)
        
        
    def _createScanNumberInput(self, layout, row):
        logger.debug(METHOD_ENTER_STR)
        label = qtWidgets.QLabel("Scan Numbers")
        self.scanNumsTxt = qtWidgets.QLineEdit()
        rx = qtCore.QRegExp(self.SCAN_LIST_REGEXP)
        self.scanNumsTxt.setValidator(qtGui.QRegExpValidator(rx,self.scanNumsTxt))
        layout.addWidget(label, row, 0)
        layout.addWidget(self.scanNumsTxt, row, 1)
        logger.debug(METHOD_EXIT_STR)
        

    def getMapAsHKL(self):
        '''
        '''
#        Not sure if we need this JPH
        logger.debug(METHOD_ENTER_STR)
        mapAsHkl = self.hklCheckbox.isChecked()
        logger.debug(METHOD_EXIT_STR)
        return mapAsHkl
    
    def getOutputType(self):
        '''
        Get the output type to be used.
        '''
        logger.debug(METHOD_ENTER_STR)
        outType = self.outTypeChooser.currentText()
        logger.debug(METHOD_EXIT_STR)
        return outType 
    
    def getScanList(self):
        '''
        return a list of scans to be used for loading data
        '''
        logger.debug(METHOD_ENTER_STR)
        scanList = None
        if str(self.scanNumsTxt.text()) == EMPTY_STR:
            scanList = None
        else:
            scans = srange(str(self.scanNumsTxt.text()))
            scanList = scans.list() 
        logger.debug(METHOD_EXIT_STR)
        return scanList
    
    def _outputTypeChanged(self, typeStr):
        '''
        If the output is selected to be a simple grid map type then allow
        the user to select HKL as an output.
        :param typeStr: String holding the outpu type
        '''
        logger.debug(METHOD_ENTER_STR)
        if typeStr == self.SIMPLE_GRID_MAP_STR:
            self.hklCheckbox.setEnabled(True)
        else:
            self.hklCheckbox.setDisabled(True)
            self.hklCheckbox.setCheckState(False)
        logger.debug(METHOD_EXIT_STR)
