'''
 Copyright (c) 2014, UChicago Argonne, LLC
 See LICENSE file.
'''

import PyQt4.QtGui as qtGui
import PyQt4.QtCore as qtCore

from rsMap3D.gui.qtsignalstrings import CLICKED_SIGNAL, EDIT_FINISHED_SIGNAL

class DataRange(qtGui.QDialog):
    '''
    This class displays the overall data range for all selected images in
    the available scans.
    '''
    POSITIVE_INFINITY = "Infinity"
    NEGATIVE_INFINITY = "-Infinity"
    def __init__(self, parent=None):                
        '''
        '''
        super(DataRange, self).__init__(parent)
        self._initializeRanges()
        
        layout = qtGui.QGridLayout()
        xLabel = qtGui.QLabel("X")
        xminLabel = qtGui.QLabel("min")
        self.xminText = qtGui.QLineEdit()
        self.xminValidator = qtGui.QDoubleValidator()
        self.xminText.setValidator(self.xminValidator)
        xmaxLabel = qtGui.QLabel("max")
        self.xmaxText = qtGui.QLineEdit()
        self.xmaxValidator = qtGui.QDoubleValidator()
        self.xmaxText.setValidator(self.xmaxValidator)
        yLabel = qtGui.QLabel("Y")
        yminLabel = qtGui.QLabel("min")
        self.yminText = qtGui.QLineEdit()
        self.yminValidator = qtGui.QDoubleValidator()
        self.yminText.setValidator(self.yminValidator)
        ymaxLabel = qtGui.QLabel("max")
        self.ymaxText = qtGui.QLineEdit()
        self.ymaxValidator = qtGui.QDoubleValidator()
        self.ymaxText.setValidator(self.ymaxValidator)
        zLabel = qtGui.QLabel("Z")
        zminLabel = qtGui.QLabel("min")
        self.zminText = qtGui.QLineEdit()
        self.zminValidator = qtGui.QDoubleValidator()
        self.zminText.setValidator(self.zminValidator)
        zmaxLabel = qtGui.QLabel("max")
        self.zmaxText = qtGui.QLineEdit()
        self.zmaxValidator = qtGui.QDoubleValidator()
        self.zmaxText.setValidator(self.zmaxValidator)
        buttonLayout = qtGui.QHBoxLayout()

        self.resetButton = qtGui.QPushButton("Reset")
        self.resetButton.setDisabled(True)
        
        self.applyButton = qtGui.QPushButton("Apply")
        self.applyButton.setDisabled(True)
        
        buttonLayout.addWidget(self.resetButton)
        buttonLayout.addWidget(self.applyButton)
        
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

        self.connect(self.resetButton, qtCore.SIGNAL(CLICKED_SIGNAL), self._resetRange)
        self.connect(self.applyButton, qtCore.SIGNAL(CLICKED_SIGNAL), self._applyRange)
        self.connect(self.xminText, qtCore.SIGNAL(EDIT_FINISHED_SIGNAL), 
            self._xValChanged)
        self.connect(self.xmaxText, qtCore.SIGNAL(EDIT_FINISHED_SIGNAL), 
            self._xValChanged)
        self.connect(self.yminText, qtCore.SIGNAL(EDIT_FINISHED_SIGNAL), 
            self._yValChanged)
        self.connect(self.ymaxText, qtCore.SIGNAL(EDIT_FINISHED_SIGNAL), 
            self._yValChanged)
        self.connect(self.zminText, qtCore.SIGNAL(EDIT_FINISHED_SIGNAL), 
            self._zValChanged)
        self.connect(self.zmaxText, qtCore.SIGNAL(EDIT_FINISHED_SIGNAL), 
            self._zValChanged)
        self.connect(self, qtCore.SIGNAL("rangeChanged"), 
            self._checkOkToApply)
        self.setLayout(layout)
        
    def _initializeRanges(self):
        '''
        Private class to initialize ranges at +- infinity.  This sets values 
        but puts them to bad values on purpose.
        '''
        self.ranges = (float(self.POSITIVE_INFINITY), \
                       float(self.NEGATIVE_INFINITY), \
                        float(self.POSITIVE_INFINITY), \
                        float(self.NEGATIVE_INFINITY), \
                        float(self.POSITIVE_INFINITY), \
                        float(self.NEGATIVE_INFINITY))
        self.xValsOk = True
        self.yValsOk = True
        self.zValsOk = True
        self.valsChanged = False
        
    def _applyRange(self):
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
        self.emit(qtCore.SIGNAL("rangeChanged"))
        
    def _checkOkToApply(self):
        '''
        If x, y and z pairs are OK and if the value has changed enable apply. 
        Otherwise, disable apply.  If values have changed, enable reset.
        '''
        if self.xValsOk and self.yValsOk and self.zValsOk and self.valsChanged:
            self.applyButton.setDisabled(False)
        else:
            self.applyButton.setDisabled(True)
        if self.valsChanged:
            self.resetButton.setDisabled(False)
        else:
            self.resetButton.setDisabled(True)

    def _checkValsOk(self):
        '''
        Check the min/max value pairs to make sure that the min < max.
        '''
        xmin = float(self.xminText.text())
        xmax = float(self.xmaxText.text())
        if (xmin < xmax):
            self.xValsOk = True
        else: 
            self.xValsOk = False
        ymin = float(self.yminText.text())
        ymax = float(self.ymaxText.text())
        if (ymin < ymax):
            self.yValsOk = True
        else: 
            self.yValsOk = False
        zmin = float(self.zminText.text())
        zmax = float(self.zmaxText.text())
        if (zmin < zmax):
            self.zValsOk = True
        else: 
            self.zValsOk = False
        
    def getRanges(self):
        '''
        Return the range values
        '''
        return self.ranges
        
    def _resetRange(self):
        '''
        Reset the ranges to the last set of applied values.
        '''
        self.xminText.setText(str(self.ranges[0]))
        self.xmaxText.setText(str(self.ranges[1]))
        self.yminText.setText(str(self.ranges[2]))
        self.ymaxText.setText(str(self.ranges[3]))
        self.zminText.setText(str(self.ranges[4]))
        self.zmaxText.setText(str(self.ranges[5]))
        self.valsChanged = False
        self._checkOkToApply()
        
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
        self.valsChanged = False
        self._checkOkToApply()
        
    def _xValChanged(self):
        '''
        Trigger that the xmin or xmax value has changed
        '''
        #make sure this can be a float also make sure min < max
        self._checkValsOk()
        if not self.xValsOk:
            message = qtGui.QMessageBox()
            message.warning(self, \
                            "Warning", \
                            "xmin must be less than xmax")
        self.valsChanged = True
        self._checkOkToApply()
        

    
    def _yValChanged(self):
        '''
        Trigger that the ymin or ymax value has changed
        '''
        #make sure this can be a float also make sure min < max
        self._checkValsOk()
        if not self.yValsOk:
            message = qtGui.QMessageBox()
            message.warning(self, \
                            "Warning", \
                            "ymin must be less than ymax")
        self.valsChanged = True
        self._checkOkToApply()
    
    def _zValChanged(self):
        '''
        Trigger that the zmin value has changed
        '''
        #make sure this can be a float also make sure min < max
        self._checkValsOk()
        if not self.zValsOk:
            message = qtGui.QMessageBox()
            message.warning(self, \
                            "Warning", \
                            "zmin must be less than zmax")
        self.valsChanged = True
        self._checkOkToApply()
