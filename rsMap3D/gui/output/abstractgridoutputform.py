'''
 Copyright (c) 2016, UChicago Argonne, LLC
 See LICENSE file.
'''
import os
import logging
logger = logging.getLogger(__name__)

import PyQt5.QtCore as qtCore
import PyQt5.QtGui as qtGui
import PyQt5.QtWidgets as qtWidgets

from  PyQt5.QtCore import pyqtSignal as Signal

import abc

from rsMap3D.mappers.gridmapper import QGridMapper
from rsMap3D.mappers.output.vtigridwriter import VTIGridWriter
from rsMap3D.gui.rsm3dcommonstrings import X_STR, Y_STR, Z_STR
from rsMap3D.gui.output.abstractoutputview import AbstractOutputView

INITIAL_DIM = 200

class AbstractGridOutputForm(AbstractOutputView):
    '''
    A mid level abstract class for output of grid data.  This adds inputs for the output grid
    dimensions.  Subclasses will need to add to _createDataBox in order to provide application 
    level inputs
    '''
    FORM_TITLE = "AbstractOutputForm"
    
    def __init__(self, **kwargs):
        '''
        Constructor
        '''
        super(AbstractGridOutputForm, self).__init__(**kwargs)
        self.gridWriter = VTIGridWriter()
        self.outputFileName = ""
        
    def _createDataBox(self):
        '''
        Create Widgets to collect output info.  This class adds parameters for the size of 
        the output grid.  Subclasses will override this method (Super'ing the method) to add 
        application specific inputs.
        '''
        dataBox = super(AbstractGridOutputForm, self)._createDataBox()
        layout = dataBox.layout()

        row = layout.rowCount()
        row += 1
        self._createGridDimensionInput(layout, row)        

        return dataBox
    
    def _createGridDimensionInput(self, layout, row):
        '''
        provide parameters for output grid size
        '''
        label = qtWidgets.QLabel("Grid Dimensions")
        layout.addWidget(label, row,0)
        row += 1
        label = qtWidgets.QLabel(X_STR)
        layout.addWidget(label, row,0)
        self.xDimTxt = qtWidgets.QLineEdit()
        self.xDimTxt.setText(str(INITIAL_DIM))
        self.xDimValidator = qtGui.QIntValidator()
        self.xDimTxt.setValidator(self.xDimValidator)
        layout.addWidget(self.xDimTxt, row,1)
        
        row += 1
        label = qtWidgets.QLabel(Y_STR)
        layout.addWidget(label, row,0)
        self.yDimTxt = qtWidgets.QLineEdit()
        self.yDimTxt.setText(str(INITIAL_DIM))
        self.yDimValidator = qtGui.QIntValidator()
        self.yDimTxt.setValidator(self.yDimValidator)
        layout.addWidget(self.yDimTxt, row,1)
        
        row += 1
        label = qtWidgets.QLabel(Z_STR)
        layout.addWidget(label, row,0)
        self.zDimTxt = qtWidgets.QLineEdit()
        self.zDimTxt.setText(str(INITIAL_DIM))
        self.zDimValidator = qtGui.QIntValidator()
        self.zDimTxt.setValidator(self.zDimValidator)
        layout.addWidget(self.zDimTxt, row,1)
    
    def getOutputFileName(self):
        '''
        dummy method to return self.outputFileName.  This is used by runMapper to 
        supply a filename for output files.  If the Writer used needs a fileName, 
        then the the derived class should supply self.outputFileName before running
        the mapper.  Otherwise a filename will be constructed using the project name 
        and gridWriter supplied extension.
        '''
        return self.outputFileName
    
    def runMapper(self, dataSource, transform):
        '''
        Run the selected mapper.  Writer specific class should be specified
        in the application specific subclass.  A list of forms is provided in 
        dataSource classes.
        '''
        logger.debug ("Entering " + self.FORM_TITLE + " " + \
            str(self.gridWriter))
        self.dataSource = dataSource
        nx = int(self.xDimTxt.text())
        ny = int(self.yDimTxt.text())
        nz = int(self.zDimTxt.text())
        self.outputFileName = self.getOutputFileName()
        if self.outputFileName == "":
            self.outputFileName = os.path.join(dataSource.projectDir,  \
                "%s%s" %(dataSource.projectName,self.gridWriter.FILE_EXTENSION) )
            self.setFileName.emit(self.outputFileName)
        if os.access(os.path.dirname(self.outputFileName), os.W_OK):
            self.mapper = QGridMapper(dataSource, \
                                     self.outputFileName, \
                                     self.outputType,\
                                     nx=nx, ny=ny, nz=nz,
                                     transform = transform,
                                     gridWriter = self.gridWriter,
                                     appConfig=self.appConfig)
            self.mapper.setProgressUpdater(self._updateProgress)
            self.mapper.doMap()
        else:
            self.processError.emit("The specified directory \n" + \
                                   str(os.path.dirname(self.outputFileName)) + \
                                   "\nis not writable")
        logger.debug ("Exit " + self.FORM_TITLE)

    def stopMapper(self):
        '''
        Halt the mapping _process
        '''
        self.mapper.stopMap()
 
