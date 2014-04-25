'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''
import os

from PyQt4.QtCore import *
from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QComboBox
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QFileDialog
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QIntValidator

from rsMap3D.mappers.gridmapper import QGridMapper
from rsMap3D.mappers.polemapper import PoleFigureMapper

class ProcessScans(QDialog):
    '''
    This class presents a form to select to start analysis.  This display
    allows switching between Grid map and pole figure.
    '''
    POLE_MAP_STR = "Pole Map"
    GRID_MAP_STR = "Grid Map"
    
    def __init__(self, parent=None):
        '''
        Constructor - Layout widgets on the page & link up actions.
        '''
        super(ProcessScans, self).__init__(parent)
        layout = QGridLayout()
#        label = QLabel("Output Type")        
#        layout.addWidget(label, 0, 0)
        self.outTypeChooser = QComboBox()
        self.outTypeChooser.addItem(self.GRID_MAP_STR)
        self.outTypeChooser.addItem(self.POLE_MAP_STR)
#        layout.addWidget(self.outTypeChooser, 0,1)
        
        label = QLabel("Grid Dimensions")
        layout.addWidget(label, 0,0)
        
        label = QLabel("X")
        layout.addWidget(label, 1,0)
        self.xDimTxt = QLineEdit()
        self.xDimTxt.setText("200")
        self.xDimValidator = QIntValidator()
        self.xDimTxt.setValidator(self.xDimValidator)
        layout.addWidget(self.xDimTxt, 1,1)
        
        label = QLabel("Y")
        layout.addWidget(label, 2,0)
        self.yDimTxt = QLineEdit()
        self.yDimTxt.setText("200")
        self.yDimValidator = QIntValidator()
        self.yDimTxt.setValidator(self.yDimValidator)
        layout.addWidget(self.yDimTxt, 2,1)
        
        label = QLabel("Z")
        layout.addWidget(label, 3,0)
        self.zDimTxt = QLineEdit()
        self.zDimTxt.setText("200")
        self.zDimValidator = QIntValidator()
        self.zDimTxt.setValidator(self.zDimValidator)
        layout.addWidget(self.zDimTxt, 3,1)
        
        label = QLabel("Output File")
        layout.addWidget(label, 4,0)
        self.outFileTxt = QLineEdit()
        layout.addWidget(self.outFileTxt, 4,1)
        self.outputFileButton = QPushButton("Browse")
        layout.addWidget(self.outputFileButton, 4, 2)
        
        
        runButton = QPushButton("Run")
        layout.addWidget(runButton, 5, 3)
        self.setLayout(layout)                    
        self.connect(runButton, SIGNAL("clicked()"), self.process)
        self.connect(self.outputFileButton, SIGNAL("clicked()"), 
                     self.browseForOutputFile)
        self.connect(self.outputFileButton, SIGNAL("editFinished()"), 
                     self.editFinishedOutputFile)
        
        
        
    def browseForOutputFile(self):
        '''
        Launch file browser to select the output file.  Checks are done to make
        sure the selected directory exists and that the selected file is 
        writable
        '''
        if self.outFileTxt.text() == "":
            fileName = str(QFileDialog.getSaveFileName(None, \
                                               "Save File", \
                                               filter="*.vti"))
        else:
            fileDirectory = os.path.dirname(str(self.outFileTxt.text()))
            fileName = str(QFileDialog.getOpenFileName(None, 
                                               "Save File", 
                                               filter="*.vti", \
                                               directory = fileDirectory))
        if fileName != "":
            if os.path.exists(os.path.dirname(str(fileName))):
                self.outFileTxt.setText(fileName)
                self.outFileTxt.emit(SIGNAL("editingFinished()"))
            else:
                message = QMessageBox()
                message.warning(self, \
                             "Warning", \
                             "The specified directory does not exist")
                self.outFileTxt.setText(fileName)
                self.outFileTxt.emit(SIGNAL("editingFinished()"))
            if not os.access(os.path.dirname(fileName), os.W_OK):
                message = QMessageBox()
                message.warning(self, \
                             "Warning", \
                             "The specified fileis not writable")
            
                
    def editFinishedOutputFile(self):
        '''
        When edititing is finished the a check is done to make sure that the 
        directory exists and the file is writable
        '''
        fileName = str(self.outFileTxt.text())
        if fileName != "":
            if os.path.exists(os.path.dirname(fileName)):
                self.outFileTxt.setText(fileName)
                self.outFileTxt.emit(SIGNAL("editingFinished()"))
            else:
                message = QMessageBox()
                message.warning(self, \
                             "Warning"\
                             "The specified directory does not exist")
            if not os.access(os.path.dirname(fileName), os.W_OK):
                message = QMessageBox()
                message.warning(self, \
                             "Warning", \
                             "The specified fileis not writable")

    def process(self):
        '''
        Emit a signal to trigger the start of procesing.
        '''
        self.emit(SIGNAL("process"))
        
    def runMapper(self, dataSource, transform):
        '''
        Run the selected mapper
        '''
        self.dataSource = dataSource
#        print "Selected " + str(self.outTypeChooser.currentText())
        nx = int(self.xDimTxt.text())
        ny = int(self.yDimTxt.text())
        nz = int(self.zDimTxt.text())
        outputFileName = str(self.outFileTxt.text())
        if os.access(os.path.dirname(outputFileName), os.W_OK):
            if (self.outTypeChooser.currentText() == self.GRID_MAP_STR):
                gridMapper = QGridMapper(dataSource, \
                                         outputFileName, \
                                         nx=nx, ny=ny, nz=nz,
                                         transform = transform)
                gridMapper.doMap()
            else:
                poleMapper = PoleFigureMapper(dataSource, \
                                              outputFileName, \
                                              nx=nx, ny=ny, nz=nz, \
                                              transform = transform)
                poleMapper.doMap()
        else:
            message = QMessageBox()
            message.warning(self, \
                         "Warning", \
                         "The specified fileis not writable")
        