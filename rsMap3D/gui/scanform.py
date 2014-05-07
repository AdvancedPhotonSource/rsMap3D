'''
 Copyright (c) 2014, UChicago Argonne, LLC
 See LICENSE file.
'''
import PyQt4.QtGui as qtGui
import PyQt4.QtCore as qtCore

class ScanForm(qtGui.QDialog):
    '''
    This class presents a form to display available scans, lists the angles 
    and q values for a selected scan and allows selecting of individual images 
    for exclusion/inclusion in the processing phase.  A window is also provided
    to visualize the q space covered by the included images in the selected
    scan.
    '''
    def __init__(self, parent=None):
        '''
        Constructor - Layout widgets on the form and set up a VTK window for 
        displaying the covered q space 
        '''
        super(ScanForm, self).__init__(parent)
        self.rangeBounds = (float("Infinity"), float("-Infinity"), \
                        float("Infinity"), float("-Infinity"), \
                        float("Infinity"), float("-Infinity"))
        layout = qtGui.QGridLayout()
        self.scanList = qtGui.QListWidget()
        layout.addWidget(self.scanList, 0, 0)
        layout.setColumnStretch(0, 10)
        
        rightBox = qtGui.QVBoxLayout()
        qrange = qtGui.QGridLayout()
        xLabel = qtGui.QLabel("X")
        xminLabel = qtGui.QLabel("min")
        self.xminText = qtGui.QLabel("")
        xmaxLabel = qtGui.QLabel("max")
        self.xmaxText = qtGui.QLabel("")
        yLabel = qtGui.QLabel("Y")
        yminLabel = qtGui.QLabel("min")
        self.yminText = qtGui.QLabel("")
        ymaxLabel = qtGui.QLabel("max")
        self.ymaxText = qtGui.QLabel("")
        zLabel = qtGui.QLabel("Z")
        zminLabel = qtGui.QLabel("min")
        self.zminText = qtGui.QLabel("")
        zmaxLabel = qtGui.QLabel("max")
        self.zmaxText = qtGui.QLabel("")

        self.selectAll = qtGui.QPushButton()
        self.selectAll.setText("Select All")
        self.selectAll.setDisabled(True)
        self.deselectAll = qtGui.QPushButton()
        self.deselectAll.setText("Deselect All")
        self.deselectAll.setDisabled(True)
        self.connect(self.selectAll, qtCore.SIGNAL("clicked()"), self.selectAllAction)
        self.connect(self.deselectAll, qtCore.SIGNAL("clicked()"), 
                     self.deselectAllAction)
        
        qrange.addWidget(xLabel, 0,0)
        qrange.addWidget(xminLabel, 0,1)
        qrange.addWidget(self.xminText, 0,2)
        qrange.addWidget(xmaxLabel, 0,3)
        qrange.addWidget(self.xmaxText, 0,4)
        qrange.addWidget(yLabel, 1,0)
        qrange.addWidget(yminLabel, 1,1)
        qrange.addWidget(self.yminText, 1,2)
        qrange.addWidget(ymaxLabel, 1,3)
        qrange.addWidget(self.ymaxText, 1,4)
        qrange.addWidget(zLabel, 2,0)
        qrange.addWidget(zminLabel, 2,1)
        qrange.addWidget(self.zminText, 2,2)
        qrange.addWidget(zmaxLabel, 2,3)
        qrange.addWidget(self.zmaxText, 2,4)
        qrange.addWidget(self.selectAll, 3,0)
        qrange.addWidget(self.deselectAll, 3,1)
        
        rightBox.addLayout(qrange)
        self.detail = qtGui.QTableWidget()
        rightBox.addWidget(self.detail)
        layout.addLayout(rightBox, 0,1)
        layout.setColumnStretch(1, 45)
                
        self.connect(self.scanList, qtCore.SIGNAL("itemClicked(QListWidgetItem *)"), 
                self.scanSelected)
         
        self.setLayout(layout);
        
    def addValueToTable(self, value, row, column, coloredBrush):
        '''
        Add a value to a cell in the table setting the value to display and 
        the foreground color
        '''
        item = qtGui.QTableWidgetItem(str(value))
        item.setForeground(coloredBrush)
        item.setFlags(item.flags() & (~qtCore.Qt.ItemIsEditable))
        self.detail.setItem(row, column, item)
        
    def checkItemChanged(self,item):
        '''
        Change whether a row is selected or not and register if the associated
        image will be used in analysis
        '''
        scanNo = self.getSelectedScan()
        row = item.row()
        if item.checkState() == qtCore.Qt.Checked:
            self.dataSource.imageToBeUsed[scanNo][row] = True
        else:
            self.dataSource.imageToBeUsed[scanNo][row] = False
        self.showQs(scanNo)

    def deselectAllAction(self):
        '''
        Change setting for all images in the selected scan so that none of the
        images are used in analysis
        '''
        scanNo = self.getSelectedScan()
        for i in xrange(len(self.dataSource.imageToBeUsed[scanNo])):
            self.dataSource.imageToBeUsed[scanNo][i] = False
        self.showQs(scanNo)

    def getSelectedScan(self):
        '''
        Return the scan number of the selected scan
        '''
        scansSel = self.scanList.selectedItems()
        if len(scansSel) > 1:
            print "Should not be able to select more than one scan."
        scan = scansSel[0]
        scanNo = int(scan.text().split(' ')[0])
        return scanNo
        
    def loadScanFile(self, dataSource):
        '''
        Load information from the selected dataSource into this form.
        '''
        self.dataSource = dataSource
        self.scanList.clear()
        for curScan in self.dataSource.getAvailableScans():
            item = qtGui.QListWidgetItem()
            item.setText(str(curScan))
            self.scanList.addItem(item)
        self.detail.setColumnCount(7 + \
                                   len(dataSource.getDetectorAngleNames()) + \
                                   len(dataSource.getSampleAngleNames()))
        self.detail.setHorizontalHeaderLabels(['Use Image'] + \
                                            dataSource.getSampleAngleNames() + \
                                            dataSource.getDetectorAngleNames() + \
                                            ['Min qx', 'Max qx', 'Min qy', \
                                            'Max qy', 'Min qz', 'Max qz'])
        self.emit(qtCore.SIGNAL("doneLoading"))
        
   
    def renderBounds(self, bounds):
        '''
        Render a box with boundaries from the given input
        '''
        self.emit(qtCore.SIGNAL("renderBounds"), bounds)
        
    def renderOverallQs(self):
        '''
        Render bounds for all selected images from all available scans 
        '''
        self.emit(qtCore.SIGNAL("clearRenderWindow"))
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
            for i in xrange(0, len(minx)-1,step ):
                if imageToBeUsed[scan][i]:
                    self.renderBounds((minx[i], maxx[i], miny[i], \
                                      maxy[i], minz[i], maxz[i]))
        self.emit(qtCore.SIGNAL("showRangeBounds"), \
                  self.dataSource.getRangeBounds())
                                
    def scanSelected(self, item):
        '''
        When a scan is selected from the list, change the table to display 
        information about the images in that scan and call to to show the 
        bounds of the selected images in that scan.
        '''
        scanNo = int(item.text().split(' ')[0])
        self.showAngles(scanNo)
        self.showQs(scanNo)
        self.selectAll.setEnabled(True)
        self.deselectAll.setEnabled(True)
                
    def selectAllAction(self):
        '''
        Mark all images in the currently selected scan for use in analysis
        '''
        scanNo = self.getSelectedScan()
        for i in xrange(len(self.dataSource.imageToBeUsed[scanNo])):
            self.dataSource.imageToBeUsed[scanNo][i] = True
        self.showQs(scanNo)
                        
    def showAngles(self, scanNo):
        '''
        Display the angles associated with images in the scan in the table.
        '''
        angles = self.dataSource.getGeoAngles(self.dataSource.sd[scanNo], \
                                              self.dataSource.getAngles())
        self.detail.setRowCount(len(angles))
        blackBrush = qtGui.QBrush()
        blackBrush.setColor(qtGui.QColor('black'))
        row = 0
        self.disconnect(self.detail, qtCore.SIGNAL("itemChanged(QTableWidgetItem *)"), 
                        self.checkItemChanged)

        for angle in angles:
            checkItem = qtGui.QTableWidgetItem(1)
            checkItem.data(qtCore.Qt.CheckStateRole)
            checkItem.setCheckState(qtCore.Qt.Checked)
            self.detail.setItem(row, 0, checkItem)
            for i in xrange(len(angle)):
                self.addValueToTable(angle[i], row, i+1, blackBrush)
            row +=1
        self.connect(self.detail, qtCore.SIGNAL("itemChanged(QTableWidgetItem *)"), 
                    self.checkItemChanged)

    def showQs(self, scan ):
        '''
        Display q max/min value for the image in the selected scan in the table
        and render the boundaries for those Q values.
        '''
        self.emit(qtCore.SIGNAL("clearRenderWindow"))
        redBrush = qtGui.QBrush()
        redBrush.setColor(qtGui.QColor('red'))
        blackBrush = qtGui.QBrush()
        blackBrush.setColor(qtGui.QColor('black'))
        xmin, xmax, ymin, ymax, zmin, zmax = \
            self.dataSource.getImageBounds(scan)
        row = 0
        self.disconnect(self.detail, qtCore.SIGNAL("itemChanged(QTableWidgetItem *)"), 
                        self.checkItemChanged)
        imageToBeUsed = self.dataSource.getImageToBeUsed()
        numAngles = len(self.dataSource.getAngles())
        for value in xmin:
            if imageToBeUsed[scan][row]:
                self.addValueToTable(xmin[row], row, numAngles + 1, blackBrush)
                self.addValueToTable(xmax[row], row, numAngles + 2, blackBrush)
                self.addValueToTable(ymin[row], row, numAngles + 3, blackBrush)
                self.addValueToTable(ymax[row], row, numAngles + 4, blackBrush)
                self.addValueToTable(zmin[row], row, numAngles + 5, blackBrush)
                self.addValueToTable(zmax[row], row, numAngles + 6, blackBrush)
                self.renderBounds((xmin[row], xmax[row], ymin[row], ymax[row], \
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
        self.renderBounds((scanXmin, scanXmax, scanYmin, scanYmax, \
            scanZmin, scanZmax))
        self.emit(qtCore.SIGNAL("showRangeBounds"), (scanXmin, scanXmax, scanYmin, \
                                              scanYmax, scanZmin, scanZmax))
        self.connect(self.detail, qtCore.SIGNAL("itemChanged(QTableWidgetItem *)"), 
                    self.checkItemChanged)

