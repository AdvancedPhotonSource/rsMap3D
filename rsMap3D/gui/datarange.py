'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''

from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QDoubleValidator

class DataRange(QDialog):
    '''
    This class displays the overall data range for all selected images in
    the available scans.
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
        self.xminValidator = QDoubleValidator()
        self.xminText.setValidator(self.xminValidator)
        xmaxLabel = QLabel("max")
        self.xmaxText = QLineEdit()
        self.xmaxValidator = QDoubleValidator()
        self.xmaxText.setValidator(self.xmaxValidator)
        yLabel = QLabel("Y")
        yminLabel = QLabel("min")
        self.yminText = QLineEdit()
        self.yminValidator = QDoubleValidator()
        self.yminText.setValidator(self.yminValidator)
        ymaxLabel = QLabel("max")
        self.ymaxText = QLineEdit()
        self.ymaxValidator = QDoubleValidator()
        self.ymaxText.setValidator(self.ymaxValidator)
        zLabel = QLabel("Z")
        zminLabel = QLabel("min")
        self.zminText = QLineEdit()
        self.zminValidator = QDoubleValidator()
        self.zminText.setValidator(self.zminValidator)
        zmaxLabel = QLabel("max")
        self.zmaxText = QLineEdit()
        self.zmaxValidator = QDoubleValidator()
        self.zmaxText.setValidator(self.zmaxValidator)
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
        Private class to initialize ranges at +- infinity.  This sets values 
        but puts them to bad values on purpose.
        '''
        self.ranges = (float("Infinity"), float("-Infinity"), \
                        float("Infinity"), float("-Infinity"), \
                        float("Infinity"), float("-Infinity"))
        
    def applyRange(self):
        '''
        Apply changes by recording them as current values and signaling that 
        the ranges have changed.
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
        Reset the ranges to the last set of applied values.
        '''
        self.xminText.setText(str(self.ranges[0]))
        self.xmaxText.setText(str(self.ranges[1]))
        self.yminText.setText(str(self.ranges[2]))
        self.ymaxText.setText(str(self.ranges[3]))
        self.zminText.setText(str(self.ranges[4]))
        self.zmaxText.setText(str(self.ranges[5]))
        
    def setRanges(self, xmin, xmax, ymin, ymax, zmin, zmax):
        '''
        Allow ranges to be set externally
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
        Return the range values
        '''
        return self.ranges
        
    def xminChanged(self):
        '''
        Trigger that the xmin value has changed
        '''
        #make sure this can be a float also make sure min < max
        print 'change)'
    
    def xmaxChanged(self):
        '''
        Trigger that the xmax value has changed
        '''
        #make sure this can be a float also make sure min < max
        print 'change)'
    
    def yminChanged(self):
        '''
        Trigger that the ymin value has changed
        '''
        #make sure this can be a float also make sure min < max
        print 'change)'
    
    def ymaxChanged(self):
        '''
        trigger that the ymax value has changed
        '''
        #make sure this can be a float also make sure min < max
        print 'change)'
    
    def zminChanged(self):
        '''
        Trigger that the zmin value has changed
        '''
        #make sure this can be a float also make sure min < max
        print 'change)'
    
    def zmaxChanged(self):
        '''
        Trigger that the zmax value has changed.
        '''
        #make sure this can be a float also make sure min < max
        print 'change)'
        
        
