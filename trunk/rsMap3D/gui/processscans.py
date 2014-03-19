'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''

from PyQt4.QtCore import *
from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QComboBox
from PyQt4.QtGui import QLineEdit

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
        label = QLabel("Output Type")        
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
        layout.addWidget(self.xDimTxt, 1,1)
        
        label = QLabel("Y")
        layout.addWidget(label, 2,0)
        self.yDimTxt = QLineEdit()
        self.yDimTxt.setText("200")
        layout.addWidget(self.yDimTxt, 2,1)
        
        label = QLabel("Z")
        layout.addWidget(label, 3,0)
        self.zDimTxt = QLineEdit()
        self.zDimTxt.setText("200")
        layout.addWidget(self.zDimTxt, 3,1)
        
        
        runButton = QPushButton("Run")
        layout.addWidget(runButton, 5, 3)
        self.setLayout(layout)                    
        self.connect(runButton, SIGNAL("clicked()"), self.process)
        
        
        
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
        print "Selected " + str(self.outTypeChooser.currentText())
        nx = int(self.xDimTxt.text())
        ny = int(self.yDimTxt.text())
        nz = int(self.zDimTxt.text())
        if (self.outTypeChooser.currentText() == self.GRID_MAP_STR):
            gridMapper = QGridMapper(dataSource, \
                                     nx=nx, ny=ny, nz=nz,
                                     transform = transform)
            gridMapper.doMap()
        else:
            poleMapper = PoleFigureMapper(dataSource, nx=nx, ny=ny, nz=nz, \
                                          transform = transform)
            poleMapper.doMap()
            
        
