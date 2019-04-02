'''
 Copyright (c) 2014,2017 UChicago Argonne, LLC
 See LICENSE file.
'''
import logging
logger = logging.getLogger(__name__)

import PyQt5.QtGui as qtGui
import PyQt5.QtCore as qtCore
import PyQt5.QtWidgets as qtWidgets

from rsMap3D.gui.rsmap3dsignals import DONE_LOADING_SIGNAL, RENDER_BOUNDS_SIGNAL,\
    CLEAR_RENDER_WINDOW_SIGNAL, SHOW_RANGE_BOUNDS_SIGNAL
from rsMap3D.gui.rsm3dcommonstrings import POSITIVE_INFINITY, \
    NEGATIVE_INFINITY, X_STR, Y_STR, Z_STR, EMPTY_STR, RED, BLACK, MIN_STR,\
    MAX_STR

class ScanForm(qtWidgets.QDialog):
    '''
    This class presents a form to display available scans, lists the angles 
    and q values for a selected scan and allows selecting of individual images 
    for exclusion/inclusion in the processing phase.  A window is also provided
    to visualize the q space covered by the included images in the selected
    scan.
    '''
    #define signals needed for this class
    doneLoading = qtCore.pyqtSignal(name=DONE_LOADING_SIGNAL)
    clearRenderWindow = qtCore.pyqtSignal(name=CLEAR_RENDER_WINDOW_SIGNAL)
    renderBoundsSignal = qtCore.pyqtSignal(object, name=RENDER_BOUNDS_SIGNAL)
    showRangeBounds = qtCore.pyqtSignal(object, name=SHOW_RANGE_BOUNDS_SIGNAL)
    
    def __init__(self, parent=None):
        '''
        Constructor - Layout widgets on the form and set up a VTK window for 
        displaying the covered q space 
        '''
        super(ScanForm, self).__init__(parent)
        self.rangeBounds = (float(POSITIVE_INFINITY), \
                            float(NEGATIVE_INFINITY), \
                            float(POSITIVE_INFINITY), \
                            float(NEGATIVE_INFINITY), \
                            float(POSITIVE_INFINITY), \
                            float(NEGATIVE_INFINITY))
        layout = qtWidgets.QGridLayout()
        self.scanList = qtWidgets.QListWidget()
        layout.addWidget(self.scanList, 0, 0)
        layout.setColumnStretch(0, 10)
        
        rightBox = qtWidgets.QVBoxLayout()
        qrange = qtWidgets.QGridLayout()
        xLabel = qtWidgets.QLabel(X_STR)
        xminLabel = qtWidgets.QLabel(MIN_STR)
        self.xminText = qtWidgets.QLabel(EMPTY_STR)
        xmaxLabel = qtWidgets.QLabel(MAX_STR)
        self.xmaxText = qtWidgets.QLabel(EMPTY_STR)
        yLabel = qtWidgets.QLabel(Y_STR)
        yminLabel = qtWidgets.QLabel(MIN_STR)
        self.yminText = qtWidgets.QLabel(EMPTY_STR)
        ymaxLabel = qtWidgets.QLabel(MAX_STR)
        self.ymaxText = qtWidgets.QLabel(EMPTY_STR)
        zLabel = qtWidgets.QLabel(Z_STR)
        zminLabel = qtWidgets.QLabel(MIN_STR)
        self.zminText = qtWidgets.QLabel(EMPTY_STR)
        zmaxLabel = qtWidgets.QLabel(MAX_STR)
        self.zmaxText = qtWidgets.QLabel(EMPTY_STR)

        self.selectAll = qtWidgets.QPushButton()
        self.selectAll.setText("Select All")
        self.selectAll.setDisabled(True)
        self.deselectAll = qtWidgets.QPushButton()
        self.deselectAll.setText("Deselect All")
        self.deselectAll.setDisabled(True)
        self.selectAll.clicked.connect(self.selectAllAction)
        self.deselectAll.clicked.connect(self.deselectAllAction)

        self.availableScanTypes = qtWidgets.QWidget()
        self.availableScanTypes.setLayout(qtWidgets.QVBoxLayout())
        
        row = 0
        qrange.addWidget(xLabel, row,0)
        qrange.addWidget(xminLabel, row,1)
        qrange.addWidget(self.xminText, row,2)
        qrange.addWidget(xmaxLabel, row,3)
        qrange.addWidget(self.xmaxText, row,4)
        row += 1
        qrange.addWidget(yLabel, row, 0)
        qrange.addWidget(yminLabel, row ,1)
        qrange.addWidget(self.yminText, row, 2)
        qrange.addWidget(ymaxLabel, row, 3)
        qrange.addWidget(self.ymaxText, row, 4)
        row += 1
        qrange.addWidget(zLabel, row, 0)
        qrange.addWidget(zminLabel, row, 1)
        qrange.addWidget(self.zminText, row, 2)
        qrange.addWidget(zmaxLabel, row, 3)
        qrange.addWidget(self.zmaxText, row, 4)
        row += 1
        qrange.addWidget(self.selectAll, row,0)
        qrange.addWidget(self.deselectAll, row,1)
        qrange.addWidget(self.availableScanTypes, row, 2)
        
        rightBox.addLayout(qrange)
        self.detail = qtWidgets.QTableWidget()
        rightBox.addWidget(self.detail)
        layout.addLayout(rightBox, 0,1)
        layout.setColumnStretch(1, 45)
                
        self.scanList.itemClicked[qtWidgets.QListWidgetItem]. \
            connect(self._scanSelected)
        
        self.initialSelectionMade = False
        self.setLayout(layout);
        
    def addAvailableScanTypes(self):
        layout = self.availableScanTypes.layout()
        for scanType in self.dataSource.getAvailableScanTypes():
            typeCheckBox = qtWidgets.QCheckBox(scanType)
            typeCheckBox.setChecked(True)
            typeCheckBox.stateChanged[int].connect(
                         self.availableScanTypesChanged)
            layout.addWidget(typeCheckBox)
        
    def addValueToTable(self, value, row, column, coloredBrush):
        '''
        Add a value to a cell in the table setting the value to display and 
        the foreground color
        :param value:  Value to be converted to a string for addition to the 
        table
        :param row:  Row to place the  value
        :param column: Column to place the value
        :param coloredBrush:  A colored brush  to use to affect a color change
        '''
        item = qtWidgets.QTableWidgetItem(str(value))
        item.setForeground(coloredBrush)
        item.setFlags(item.flags() & (~qtCore.Qt.ItemIsEditable))
        self.detail.setItem(row, column, item)
    
    @qtCore.pyqtSlot(int)
    def availableScanTypesChanged(self, state):
        scanTypes = self.availableScanTypes.children()
        for scanType in scanTypes:
            if isinstance(scanType, qtWidgets.QWidget):
                self.dataSource.setScanTypeUsed(scanType.text(), 
                                                scanType.isChecked())
        for scan in self.dataSource.getAvailableScans():
            self.showAngles(scan)
            self.showQs(scan)
    
    @qtCore.pyqtSlot(qtWidgets.QTableWidgetItem)
    def checkItemChanged(self, item):
        '''
        Change whether a row is selected or not and register if the associated
        image will be used in analysis
        :param item: checkbox item to check state of
        '''
        scanNo = self.getSelectedScan()
        row = item.row()
        if item.checkState() == qtCore.Qt.Checked:
            self.dataSource.imageToBeUsed[scanNo][row] = True
        else:
            self.dataSource.imageToBeUsed[scanNo][row] = False
        self.showQs(scanNo)

    @qtCore.pyqtSlot()
    def deselectAllAction(self):
        '''
        Change setting for all images in the selected scan so that none of the
        images are used in analysis
        '''
        scanNo = self.getSelectedScan()
        for i in range(len(self.dataSource.imageToBeUsed[scanNo])):
            self.dataSource.imageToBeUsed[scanNo][i] = False
        self.showQs(scanNo)

    def getSelectedScan(self):
        '''
        Return the scan number of the selected scan
        '''
        scansSel = self.scanList.selectedItems()
        if len(scansSel) > 1:
            logger.warning( "Should not be able to select more than one scan.")
        scan = scansSel[0]
        scanNo = int(scan.text().split(' ')[0])
        return scanNo
        
    def loadScanFile(self, dataSource):
        '''
        Load information from the selected dataSource into this form.
        :param dataSource: source of scan data that will populate the scan form
        '''
        self.dataSource = dataSource
        self.scanList.clear()
        self.removeAvailableScanTypes()
        for curScan in self.dataSource.getAvailableScans():
            item = qtWidgets.QListWidgetItem()
            item.setText(str(curScan))
            self.scanList.addItem(item)
        self.detail.setColumnCount(7 + \
                                   len(dataSource.getReferenceNames()))
        labels = []
        labels.append('Use Image')
        labels.extend(dataSource.getReferenceNames())
        labels.extend(['Min qx', 'Max qx', 'Min qy', \
                       'Max qy', 'Min qz', 'Max qz'])
        self.detail.setHorizontalHeaderLabels(labels)
        self.addAvailableScanTypes()
        self.doneLoading.emit()
        
   
    def removeAvailableScanTypes(self):
        scanTypes = self.availableScanTypes.children()
        layout = self.availableScanTypes.layout()
        for scanType in scanTypes:
            if isinstance(scanType, qtWidgets.QWidget):
                scanType.stateChanged[int].disconnect(
                                self.availableScanTypesChanged)
                layout.removeWidget(scanType)
                scanType.setParent(None)
        layout.update()
        
    def renderOverallQs(self):
        '''
        Render bounds for all selected images from all available scans 
        '''
        self.clearRenderWindow.emit()
        #self.ren.RemoveAllViewProps()
        imageToBeUsed = self.dataSource.getImageToBeUsed()
        for scan in self.dataSource.getAvailableScans():
            minx, maxx, miny, maxy, minz, maxz = \
                self.dataSource.getImageBounds(scan)                
            #set up to skip some images.
            if len(minx) >200:
                step = len(minx)/200 + 1
            else:
                step = 1
            #display scan 
            for i in range(0, len(minx)-1,int(step) ):
                if imageToBeUsed[scan][i]:
                    self.renderBoundsSignal[object] \
                            .emit((minx[i], maxx[i], miny[i], \
                               maxy[i], minz[i], maxz[i]))
        self.showRangeBounds[object].emit( self.dataSource.getRangeBounds())
                                
    @qtCore.pyqtSlot(qtWidgets.QListWidgetItem)
    def _scanSelected(self, item):
        '''
        When a scan is selected from the list, change the table to display 
        information about the images in that scan and call to to show the 
        bounds of the selected images in that scan.
        :param item: item selected from scan list.  
        '''
        scanNo = int(item.text().split(' ')[0])
        self.showAngles(scanNo)
        self.showQs(scanNo)
        self.selectAll.setEnabled(True)
        self.deselectAll.setEnabled(True)
                
    @qtCore.pyqtSlot()
    def selectAllAction(self):
        '''
        Mark all images in the currently selected scan for use in analysis
        '''
        scanNo = self.getSelectedScan()
        for i in range(len(self.dataSource.imageToBeUsed[scanNo])):
            self.dataSource.imageToBeUsed[scanNo][i] = True
        self.showQs(scanNo)
                        
    def showAngles(self, scanNo):
        '''
        Display the angles associated with images in the scan in the table.
        :param scanNo: scan number of the scan to show.
        '''
        angles = self.dataSource.getReferenceValues(scanNo)
        #print "Angles:" + str(angles)
        self.detail.setRowCount(len(angles))
        blackBrush = qtGui.QBrush()
        blackBrush.setColor(qtGui.QColor(BLACK))
        row = 0
        if self.initialSelectionMade:
            self.detail.itemChanged[qtWidgets.QTableWidgetItem].disconnect( \
                        self.checkItemChanged)

        for angle in angles:
            checkItem = qtWidgets.QTableWidgetItem(1)
            checkItem.data(qtCore.Qt.CheckStateRole)
            checkItem.setCheckState(qtCore.Qt.Checked)
            self.detail.setItem(row, 0, checkItem)
            for i in range(len(angle)):
                self.addValueToTable(angle[i], row, i+1, blackBrush)
            row += 1
        self.detail.itemChanged[qtWidgets.QTableWidgetItem].connect( \
                    self.checkItemChanged)
        self.initialSelectionMade = True

    def showQs(self, scan ):
        '''
        Display q max/min value for the image in the selected scan in the table
        and render the boundaries for those Q values.
        :param scan: The scan whos data will be shown
        '''
        self.clearRenderWindow.emit()
        redBrush = qtGui.QBrush()
        redBrush.setColor(qtGui.QColor(RED))
        blackBrush = qtGui.QBrush()
        blackBrush.setColor(qtGui.QColor(BLACK))
        xmin, xmax, ymin, ymax, zmin, zmax = \
            self.dataSource.getImageBounds(scan)
        row = 0
        if self.initialSelectionMade:
            self.detail.itemChanged[qtWidgets.QTableWidgetItem].disconnect( \
                        self.checkItemChanged)
        imageToBeUsed = self.dataSource.getImageToBeUsed()
        numAngles = len(self.dataSource.getReferenceNames())
        for value in xmin:
            if imageToBeUsed[scan][row]:
                self.addValueToTable(xmin[row], row, numAngles + 1, blackBrush)
                self.addValueToTable(xmax[row], row, numAngles + 2, blackBrush)
                self.addValueToTable(ymin[row], row, numAngles + 3, blackBrush)
                self.addValueToTable(ymax[row], row, numAngles + 4, blackBrush)
                self.addValueToTable(zmin[row], row, numAngles + 5, blackBrush)
                self.addValueToTable(zmax[row], row, numAngles + 6, blackBrush)
                self.renderBoundsSignal[object].emit((xmin[row], xmax[row], 
                                                      ymin[row], ymax[row], \
                                                      zmin[row], zmax[row]))
                checkItem = self.detail.item(row,0)
                checkItem.setCheckState(qtCore.Qt.Checked)
            else:
                self.addValueToTable(xmin[row], row, numAngles + 1, redBrush)
                self.addValueToTable(xmax[row], row, numAngles + 2, redBrush)
                self.addValueToTable(ymin[row], row, numAngles + 3, redBrush)
                self.addValueToTable(ymax[row], row, numAngles + 4, redBrush)
                self.addValueToTable(zmin[row], row, numAngles + 5, redBrush)
                self.addValueToTable(zmax[row], row, numAngles + 6, redBrush)
                checkItem = self.detail.item(row,0)
                checkItem.setCheckState(qtCore.Qt.Unchecked)
            row +=1
        
                         
        scanXmin, scanXmax, scanYmin, scanYmax, scanZmin, scanZmax = \
           self.dataSource.findScanQs(xmin, xmax, ymin, ymax, zmin, zmax)
        self.xminText.setText(str(scanXmin))
        self.xmaxText.setText(str(scanXmax))
        self.yminText.setText(str(scanYmin))
        self.ymaxText.setText(str(scanYmax))
        self.zminText.setText(str(scanZmin))
        self.zmaxText.setText(str(scanZmax))
        self.renderBoundsSignal[object].emit((scanXmin, scanXmax, scanYmin, 
                                              scanYmax, scanZmin, scanZmax))
        self.showRangeBounds[object].emit( (scanXmin, scanXmax, scanYmin, \
                                              scanYmax, scanZmin, scanZmax))
        self.detail.itemChanged[qtWidgets.QTableWidgetItem].connect( \
                    self.checkItemChanged)
        self.initialSelectionMade = True
