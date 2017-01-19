'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''

import PyQt4.QtCore as qtCore
import PyQt4.QtGui as qtGui

from rsMap3D.gui.input.abstractimageperfileview import AbstractImagePerFileView
from rsMap3D.gui.input.usesxmlinstconfig import UsesXMLInstConfig
from rsMap3D.gui.input.usesxmldetectorconfig import UsesXMLDetectorConfig
from rsMap3D.gui.rsm3dcommonstrings import EMPTY_STR,\
    SPEC_FILE_FILTER,\
    SELECT_SPEC_FILE_TITLE
from rsMap3D.gui.qtsignalstrings import CURRENT_INDEX_CHANGED_SIGNAL
from rsMap3D.utils.srange import srange


class SpecXMLDrivenFileForm(AbstractImagePerFileView, UsesXMLInstConfig, UsesXMLDetectorConfig):

    SCAN_LIST_REGEXP = "((\d)+(-(\d)+)?\,( )?)+"

    def __init__(self, parent=None):
        super(SpecXMLDrivenFileForm, self).__init__(parent)
        
        self.fileDialogTitle = SELECT_SPEC_FILE_TITLE
        self.fileDialogFilter = SPEC_FILE_FILTER

        self.dataBox = self._createDataBox()
        controlBox = self._createControlBox()
        
        self.layout.addWidget(self.dataBox)
        self.layout.addWidget(controlBox)
        self.setLayout(self.layout);

    def _createHKLOutput(self, layout, row):
        label = qtGui.QLabel("HKL output")
        layout.addWidget(label, row, 0)
        self.hklCheckbox = qtGui.QCheckBox()
        layout.addWidget(self.hklCheckbox, row, 1)

        
    def _createOutputType(self, layout, row):
        label = qtGui.QLabel("Output Type")
        self.outTypeChooser = qtGui.QComboBox()
        self.outTypeChooser.addItem(self.SIMPLE_GRID_MAP_STR)
        self.outTypeChooser.addItem(self.POLE_MAP_STR)
        layout.addWidget(label, row, 0)
        layout.addWidget(self.outTypeChooser, row, 1)
        self.outTypeChooser.currentIndexChanged[str].connect(self._outputTypeChanged)
#         self.connect(self.outTypeChooser, \
#                      qtCore.SIGNAL(CURRENT_INDEX_CHANGED_SIGNAL), \
#                      self._outputTypeChanged)
        
        
    def _createScanNumberInput(self, layout, row):
        label = qtGui.QLabel("Scan Numbers")
        self.scanNumsTxt = qtGui.QLineEdit()
        rx = qtCore.QRegExp(self.SCAN_LIST_REGEXP)
        self.scanNumsTxt.setValidator(qtGui.QRegExpValidator(rx,self.scanNumsTxt))
        layout.addWidget(label, row, 0)
        layout.addWidget(self.scanNumsTxt, row, 1)
        

    def getMapAsHKL(self):
        '''
        '''
#        Not sure if we need this JPH
        return self.hklCheckbox.isChecked()
#        return False
    
    def getOutputType(self):
        '''
        Get the output type to be used.
        '''
        return self.outTypeChooser.currentText()
    
    def getScanList(self):
        '''
        return a list of scans to be used for loading data
        '''
        if str(self.scanNumsTxt.text()) == EMPTY_STR:
            return None
        else:
            scans = srange(str(self.scanNumsTxt.text()))
            return scans.list() 
        
    def _outputTypeChanged(self, typeStr):
        '''
        If the output is selected to be a simple grid map type then allow
        the user to select HKL as an output.
        :param typeStr: String holding the outpu type
        '''
        if typeStr == self.SIMPLE_GRID_MAP_STR:
            self.hklCheckbox.setEnabled(True)
        else:
            self.hklCheckbox.setDisabled(True)
            self.hklCheckbox.setCheckState(False)
