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
        layout.addWidget(label, 0, 0)
        self.outTypeChooser = QComboBox()
        self.outTypeChooser.addItem(self.GRID_MAP_STR)
        self.outTypeChooser.addItem(self.POLE_MAP_STR)
        layout.addWidget(self.outTypeChooser, 0,1)
        runButton = QPushButton("Run")
        layout.addWidget(runButton, 2,3)
        self.setLayout(layout)                    
        self.connect(runButton, SIGNAL("clicked()"), self.process)
        
        
    def process(self):
        '''
        Emit a signal to trigger the start of procesing.
        '''
        self.emit(SIGNAL("process"))
        
    def runMapper(self, dataSource):
        '''
        Run the selected mapper
        '''
        self.dataSource = dataSource
        print "Selected " + str(self.outTypeChooser.currentText())
        nx = 200
        ny = 201
        nz = 202
        if (self.outTypeChooser.currentText() == self.GRID_MAP_STR):
            gridMapper = QGridMapper(dataSource, nx=nx, ny=ny, nz=nz)
            gridMapper.doMap()
        else:
            poleMapper = PoleFigureMapper(dataSource, nx=nx, ny=ny, nz=nz)
            poleMapper.doMap()
            
        
