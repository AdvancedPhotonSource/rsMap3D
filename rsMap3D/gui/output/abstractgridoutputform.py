'''
 Copyright (c) 2016, UChicago Argonne, LLC
 See LICENSE file.
'''
from rsMap3D.gui.output.abstractoutputview import AbstractOutputView
import PyQt4.QtCore as qtCore
import PyQt4.QtGui as qtGui

import abc
from rsMap3D.gui.rsm3dcommonstrings import X_STR, Y_STR, Z_STR
from rsMap3D.gui.rsmap3dsignals import SET_FILE_NAME_SIGNAL,\
    PROCESS_ERROR_SIGNAL
import os
from rsMap3D.mappers.gridmapper import QGridMapper
from rsMap3D.mappers.output.vtigridwriter import VTIGridWriter



class AbstractGridOutputForm(AbstractOutputView):
    '''
    A mid level abstract class for output of grid data.  This adds inputs for the output grid
    dimensions.  Subclasses will need to add to _createDataBox in order to provide application 
    level inputs
    '''
    FORM_TITLE = "AbstractOutputForm"
    
    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(AbstractGridOutputForm, self).__init__(parent)
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
        label = qtGui.QLabel("Grid Dimensions")
        layout.addWidget(label, row,0)
        row += 1
        label = qtGui.QLabel(X_STR)
        layout.addWidget(label, row,0)
        self.xDimTxt = qtGui.QLineEdit()
        self.xDimTxt.setText("200")
        self.xDimValidator = qtGui.QIntValidator()
        self.xDimTxt.setValidator(self.xDimValidator)
        layout.addWidget(self.xDimTxt, row,1)
        
        row += 1
        label = qtGui.QLabel(Y_STR)
        layout.addWidget(label, row,0)
        self.yDimTxt = qtGui.QLineEdit()
        self.yDimTxt.setText("200")
        self.yDimValidator = qtGui.QIntValidator()
        self.yDimTxt.setValidator(self.yDimValidator)
        layout.addWidget(self.yDimTxt, row,1)
        
        row += 1
        label = qtGui.QLabel(Z_STR)
        layout.addWidget(label, row,0)
        self.zDimTxt = qtGui.QLineEdit()
        self.zDimTxt.setText("200")
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
        print ("Entering Abstractgridoutput form runMapper " + self.FORM_TITLE)
        self.dataSource = dataSource
        nx = int(self.xDimTxt.text())
        ny = int(self.yDimTxt.text())
        nz = int(self.zDimTxt.text())
        self.outputFileName = self.getOutputFileName()
        if self.outputFileName == "":
            self.outputFileName = os.path.join(dataSource.projectDir,  \
                "%s%s" %(dataSource.projectName,self.gridWriter.FILE_EXTENSION) )
            self.emit(qtCore.SIGNAL(SET_FILE_NAME_SIGNAL), self.outputFileName)
        if os.access(os.path.dirname(self.outputFileName), os.W_OK):
            self.mapper = QGridMapper(dataSource, \
                                     self.outputFileName, \
                                     nx=nx, ny=ny, nz=nz,
                                     transform = transform,
                                     gridWriter = self.gridWriter)
            self.mapper.setProgressUpdater(self.updateProgress)
            self.mapper.doMap()
        else:
            self.emit(qtCore.SIGNAL(PROCESS_ERROR_SIGNAL), \
                         "The specified directory \n" + \
                         str(os.path.dirname(self.outputFileName)) + \
                         "\nis not writable")
        print ("Entering Abstractgridoutput form runMapper " + self.FORM_TITLE)

    def stopMapper(self):
        '''
        Halt the mapping _process
        '''
        self.mapper.stopMap()
 
