'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''

from PyQt4.QtCore import *
from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QPushButton

class DataRange(QDialog):
    '''
    '''
    def __init__(self, parent=None):                
        '''
        '''
        super(DataRange, self).__init__(parent)
        self._initializeRanges()
        
        layout = QGridLayout()
        xLabel = QLabel("X")
        xminLabel = QLabel("min")
        self.xminText = QLineEdit()
        xmaxLabel = QLabel("max")
        self.xmaxText = QLineEdit()
        yLabel = QLabel("Y")
        yminLabel = QLabel("min")
        self.yminText = QLineEdit()
        ymaxLabel = QLabel("max")
        self.ymaxText = QLineEdit()
        zLabel = QLabel("Z")
        zminLabel = QLabel("min")
        self.zminText = QLineEdit()
        zmaxLabel = QLabel("max")
        self.zmaxText = QLineEdit()
        buttonLayout = QHBoxLayout()
        resetButton = QPushButton("Reset")
        applyButton = QPushButton("Apply")
        buttonLayout.addWidget(resetButton)
        
        self.connect(resetButton, SIGNAL("clicked()"), self.resetRange)
        self.connect(applyButton, SIGNAL("clicked()"), self.applyRange)
        
        buttonLayout.addWidget(applyButton)
        
        layout.addWidget(xLabel, 0,0)
        layout.addWidget(xminLabel, 0,1)
        layout.addWidget(self.xminText, 0,2)
        layout.addWidget(xmaxLabel, 0,3)
        layout.addWidget(self.xmaxText, 0,4)
        layout.addWidget(yLabel, 1,0)
        layout.addWidget(yminLabel, 1,1)
        layout.addWidget(self.yminText, 1,2)
        layout.addWidget(ymaxLabel, 1,3)
        layout.addWidget(self.ymaxText, 1,4)
        layout.addWidget(zLabel, 2,0)
        layout.addWidget(zminLabel, 2,1)
        layout.addWidget(self.zminText, 2,2)
        layout.addWidget(zmaxLabel, 2,3)
        layout.addWidget(self.zmaxText, 2,4)
        layout.addLayout(buttonLayout, 3,4)
        self.connect(self.xminText, SIGNAL("editingFinished()"), 
            self.xminChanged)
        self.connect(self.xmaxText, SIGNAL("editingFinished()"), 
            self.xmaxChanged)
        self.connect(self.yminText, SIGNAL("editingFinished()"), 
            self.yminChanged)
        self.connect(self.ymaxText, SIGNAL("editingFinished()"), 
            self.ymaxChanged)
        self.connect(self.zminText, SIGNAL("editingFinished()"), 
            self.zminChanged)
        self.connect(self.zmaxText, SIGNAL("editingFinished()"), 
            self.zmaxChanged)
        self.setLayout(layout)
        
    def _initializeRanges(self):
        '''
        '''
        self.ranges = (float("Infinity"), float("-Infinity"), \
                        float("Infinity"), float("-Infinity"), \
                        float("Infinity"), float("-Infinity"))
        
    def applyRange(self):
        '''
        '''
        self.ranges = (float(self.xminText.text()),
                       float(self.xmaxText.text()),
                       float(self.yminText.text()),
                       float(self.ymaxText.text()),
                       float(self.zminText.text()),
                       float(self.zmaxText.text()))
        self.emit(SIGNAL("rangeChanged"))
        
    def resetRange(self):
        '''
        '''
        self.xminText.setText(str(self.ranges[0]))
        self.xmaxText.setText(str(self.ranges[1]))
        self.yminText.setText(str(self.ranges[2]))
        self.ymaxText.setText(str(self.ranges[3]))
        self.zminText.setText(str(self.ranges[4]))
        self.zmaxText.setText(str(self.ranges[5]))
        
    def setRanges(self, xmin, xmax, ymin, ymax, zmin, zmax):
        '''
        '''
        self.ranges = (xmin, xmax, ymin, ymax, zmin, zmax)
        self.xminText.setText(str(xmin))
        self.xmaxText.setText(str(xmax))
        self.yminText.setText(str(ymin))
        self.ymaxText.setText(str(ymax))
        self.zminText.setText(str(zmin))
        self.zmaxText.setText(str(zmax))
        
    def getRanges(self):
        '''
        '''
        return self.ranges
        
    def xminChanged(self):
        '''
        '''
        #make sure this can be a float also make sure min < max
        print 'change)'
    
    def xmaxChanged(self):
        '''
        '''
        #make sure this can be a float also make sure min < max
        print 'change)'
    
    def yminChanged(self):
        '''
        '''
        #make sure this can be a float also make sure min < max
        print 'change)'
    
    def ymaxChanged(self):
        '''
        '''
        #make sure this can be a float also make sure min < max
        print 'change)'
    
    def zminChanged(self):
        '''
        '''
        #make sure this can be a float also make sure min < max
        print 'change)'
    
    def zmaxChanged(self):
        '''
        '''
        #make sure this can be a float also make sure min < max
        print 'change)'
        
        
