'''
 Copyright (c) 2014, UChicago Argonne, LLC
 See LICENSE file.
'''

import PyQt5.QtGui as qtGui
import PyQt5.QtCore as qtCore
import PyQt5.QtWidgets as qtWidgets

from rsMap3D.gui.rsmap3dsignals import RANGE_CHANGED_SIGNAL
from rsMap3D.gui.rsm3dcommonstrings import POSITIVE_INFINITY, NEGATIVE_INFINITY,\
    WARNING_STR, XMIN_INDEX, XMAX_INDEX, YMIN_INDEX, YMAX_INDEX, ZMIN_INDEX,\
    ZMAX_INDEX, MIN_STR, MAX_STR, X_STR, Y_STR, Z_STR

class DataRange(qtWidgets.QDialog):
    '''
    This class displays the overall data range for all selected images in
    the available scans.
    '''

    rangeChanged = qtCore.pyqtSignal(name=RANGE_CHANGED_SIGNAL)
    
    def __init__(self, parent=None):                
        '''
        '''
        super(DataRange, self).__init__(parent)
        self._initializeRanges()
        
        layout = qtWidgets.QGridLayout()
        xLabel = qtWidgets.QLabel(X_STR)
        xminLabel = qtWidgets.QLabel(MIN_STR)
        self.xminText = qtWidgets.QLineEdit()
        self.xminValidator = qtGui.QDoubleValidator()
        self.xminText.setValidator(self.xminValidator)
        xmaxLabel = qtWidgets.QLabel(MAX_STR)
        self.xmaxText = qtWidgets.QLineEdit()
        self.xmaxValidator = qtGui.QDoubleValidator()
        self.xmaxText.setValidator(self.xmaxValidator)
        yLabel = qtWidgets.QLabel(Y_STR)
        yminLabel = qtWidgets.QLabel(MIN_STR)
        self.yminText = qtWidgets.QLineEdit()
        self.yminValidator = qtGui.QDoubleValidator()
        self.yminText.setValidator(self.yminValidator)
        ymaxLabel = qtWidgets.QLabel(MAX_STR)
        self.ymaxText = qtWidgets.QLineEdit()
        self.ymaxValidator = qtGui.QDoubleValidator()
        self.ymaxText.setValidator(self.ymaxValidator)
        zLabel = qtWidgets.QLabel(Z_STR)
        zminLabel = qtWidgets.QLabel(MIN_STR)
        self.zminText = qtWidgets.QLineEdit()
        self.zminValidator = qtGui.QDoubleValidator()
        self.zminText.setValidator(self.zminValidator)
        zmaxLabel = qtWidgets.QLabel(MAX_STR)
        self.zmaxText = qtWidgets.QLineEdit()
        self.zmaxValidator = qtGui.QDoubleValidator()
        self.zmaxText.setValidator(self.zmaxValidator)
        buttonLayout = qtWidgets.QHBoxLayout()

        self.resetButton = qtWidgets.QPushButton("Reset")
        self.resetButton.setDisabled(True)
        
        self.applyButton = qtWidgets.QPushButton("Apply")
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

        self.resetButton.clicked.connect(self._resetRange)
        self.applyButton.clicked.connect(self._applyRange)
        self.xminText.editingFinished.connect(self._xValChanged)
        self.xmaxText.editingFinished.connect(self._xValChanged)
        self.yminText.editingFinished.connect(self._yValChanged)
        self.ymaxText.editingFinished.connect(self._yValChanged)
        self.zminText.editingFinished.connect(self._zValChanged)
        self.zmaxText.editingFinished.connect(self._zValChanged)
        self.rangeChanged.connect(self._checkOkToApply)
        self.setLayout(layout)
        
    @qtCore.pyqtSlot()
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
        self.rangeChanged.emit()
        
    @qtCore.pyqtSlot()
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
        
    def _initializeRanges(self):
        '''
        Private class to initialize ranges at +- infinity.  This sets values 
        but puts them to bad values on purpose.
        '''
        self.ranges = (float(POSITIVE_INFINITY), \
                       float(NEGATIVE_INFINITY), \
                        float(POSITIVE_INFINITY), \
                        float(NEGATIVE_INFINITY), \
                        float(POSITIVE_INFINITY), \
                        float(NEGATIVE_INFINITY))
        self.xValsOk = True
        self.yValsOk = True
        self.zValsOk = True
        self.valsChanged = False
        
    @qtCore.pyqtSlot()
    def _resetRange(self):
        '''
        Reset the ranges to the last set of applied values.
        '''
        self.xminText.setText(str(self.ranges[XMIN_INDEX]))
        self.xmaxText.setText(str(self.ranges[XMAX_INDEX]))
        self.yminText.setText(str(self.ranges[YMIN_INDEX]))
        self.ymaxText.setText(str(self.ranges[YMAX_INDEX]))
        self.zminText.setText(str(self.ranges[ZMIN_INDEX]))
        self.zmaxText.setText(str(self.ranges[ZMAX_INDEX]))
        self.valsChanged = False
        self._checkOkToApply()
        
    def setRanges(self, xmin, xmax, ymin, ymax, zmin, zmax):
        '''
        Allow ranges to be set externally
        :param xmin: minimum value in x direction
        :param xmax: maximum value in x direction
        :param ymin: minimum value in y direction
        :param ymax: maximum value in y direction
        :param zmin: minimum value in z direction
        :param zmax: maximum value in z direction
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
        
    @qtCore.pyqtSlot()
    def _xValChanged(self):
        '''
        Trigger that the xmin or xmax value has changed
        '''
        #make sure this can be a float also make sure min < max
        self._checkValsOk()
        if not self.xValsOk:
            message = qtWidgets.QMessageBox()
            message.warning(self, \
                            WARNING_STR, \
                            "xmin must be less than xmax")
        self.valsChanged = True
        self._checkOkToApply()
        

    
    @qtCore.pyqtSlot()
    def _yValChanged(self):
        '''
        Trigger that the ymin or ymax value has changed
        '''
        #make sure this can be a float also make sure min < max
        self._checkValsOk()
        if not self.yValsOk:
            message = qtWidgets.QMessageBox()
            message.warning(self, \
                            WARNING_STR, \
                            "ymin must be less than ymax")
        self.valsChanged = True
        self._checkOkToApply()
    
    @qtCore.pyqtSlot()
    def _zValChanged(self):
        '''
        Trigger that the zmin value has changed
        '''
        #make sure this can be a float also make sure min < max
        self._checkValsOk()
        if not self.zValsOk:
            message = qtWidgets.QMessageBox()
            message.warning(self, \
                            WARNING_STR, \
                            "zmin must be less than zmax")
        self.valsChanged = True
        self._checkOkToApply()
