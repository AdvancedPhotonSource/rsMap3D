'''
 Copyright (c) 2017, UChicago Argonne, LLC
 See LICENSE file.
'''
import logging
logger = logging.getLogger(__name__)

import PyQt5.QtCore as qtCore
import PyQt5.QtGui as qtGui
import PyQt5.QtWidgets as qtWidgets

from rsMap3D.gui.input.abstractfileview import AbstractFileView


class UsesCommonOutputTypes(AbstractFileView):
    """
    Class to provide input fields associated with common output types 
    such as qx, qy, qz Or Stereographic Projection
    """
    
    def __init__(self,parent=None, **kwargs):
        super(UsesCommonOutputTypes, self).__init__(parent, **kwargs)
        
        
    def _createHKLOutput(self, layout, row):
        logger.debug("Enter")
        label = qtWidgets.QLabel("HKL output")
        layout.addWidget(label, row, 0)
        self.hklCheckbox = qtWidgets.QCheckBox()
        layout.addWidget(self.hklCheckbox, row, 1)
        logger.debug("Exit")

    def _createOutputType(self, layout, row):
        '''
        Add input elements to the layout for the outputType.
        '''
        logger.debug("Enter")

        label = qtWidgets.QLabel("Output Type")
        self.outTypeChooser = qtWidgets.QComboBox()
        self.outTypeChooser.addItem(self.SIMPLE_GRID_MAP_STR)
        self.outTypeChooser.addItem(self.POLE_MAP_STR)
        layout.addWidget(label, row, 0)
        layout.addWidget(self.outTypeChooser, row, 1)
        self.outTypeChooser.currentIndexChanged[str].connect(self._outputTypeChanged)
        
        logger.debug("Exit")
        
    def getMapAsHKL(self):
        '''
        '''
#        Not sure if we need this JPH
        logger.debug("Enter")
        mapAsHkl = self.hklCheckbox.isChecked()
        logger.debug("Exit")
        return mapAsHkl
    
    def getOutputType(self):
        '''
        Get the output type to be used.
        '''
        logger.debug("Enter")
        outType = self.outTypeChooser.currentText()
        logger.debug("Exit")
        return outType 
    
    def _outputTypeChanged(self, typeStr):
        '''
        If the output is selected to be a simple grid map type then allow
        the user to select HKL as an output.
        :param typeStr: String holding the outpu type
        '''
        logger.debug("Enter")
        if typeStr == self.SIMPLE_GRID_MAP_STR:
            self.hklCheckbox.setEnabled(True)
        else:
            self.hklCheckbox.setDisabled(True)
            self.hklCheckbox.setCheckState(False)
        logger.debug("Exit")
        