'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''
import os
from PyQt4.QtCore import *
from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QFileDialog
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QComboBox
from PyQt4.QtGui import QRegExpValidator
from rsMap3D.utils.srange import srange
from rsMap3D.datasource.DetectorGeometryForXrayutilitiesReader\
     import DetectorGeometryForXrayutilitiesReader

class FileForm(QDialog):
    '''
    This class presents information for selecting input files
    '''
    POLE_MAP_STR = "Streographic Projection"
    SIMPLE_GRID_MAP_STR = "qx,qy,qz Map"
    def __init__(self,parent=None):
        '''
        Constructor - Layout Widgets on the page and link actions
        '''
        super(FileForm, self).__init__(parent)
        self.roixmin = 1
        self.roixmax = 680
        self.roiymin = 1
        self.roiymax = 480
        
        layout = QGridLayout()

        label = QLabel("Project File:");
        self.projNameTxt = QLineEdit()
        self.projectDirButton = QPushButton("Browse")
        layout.addWidget(label, 0, 0)
        layout.addWidget(self.projNameTxt, 0, 1)
        layout.addWidget(self.projectDirButton, 0, 2)

#        label = QLabel("Project Name:");
#        self.projNameTxt = QLineEdit()
#        layout.addWidget(label, 1, 0)
#        layout.addWidget(self.projNameTxt, 1, 1)

        label = QLabel("Instrument Config File:");
        self.instConfigTxt = QLineEdit()
        self.instConfigFileButton = QPushButton("Browse")
        layout.addWidget(label, 2, 0)
        layout.addWidget(self.instConfigTxt, 2, 1)
        layout.addWidget(self.instConfigFileButton, 2, 2)

        label = QLabel("Detector Config File:");
        self.detConfigTxt = QLineEdit()
        self.detConfigFileButton = QPushButton("Browse")
        layout.addWidget(label, 3, 0)
        layout.addWidget(self.detConfigTxt, 3, 1)
        layout.addWidget(self.detConfigFileButton, 3, 2)
        
        label = QLabel("Number of Pixels To Average:");
        self.pixAvgTxt = QLineEdit("1,1")
        rxAvg = QRegExp('(\d)+,(\d)+')
        self.pixAvgTxt.setValidator(QRegExpValidator(rxAvg,self.pixAvgTxt))
        layout.addWidget(label, 4, 0)
        layout.addWidget(self.pixAvgTxt, 4, 1)

        label = QLabel("Detector ROI:");
        self.detROITxt = QLineEdit()
        self.updateROITxt()
        rxROI = QRegExp('(\d)+,(\d)+,(\d)+,(\d)+')
        self.detROITxt.setValidator(QRegExpValidator(rxROI,self.detROITxt))
        layout.addWidget(label, 5, 0)
        layout.addWidget(self.detROITxt, 5, 1)
        
        label = QLabel("Scan Numbers")
        self.scanNumsTxt = QLineEdit()
        rx = QRegExp('((\d)+(-(\d)+)?\,( )?)+')
        self.scanNumsTxt.setValidator(QRegExpValidator(rx,self.scanNumsTxt))
        layout.addWidget(label, 6, 0)
        layout.addWidget(self.scanNumsTxt, 6, 1)

        label = QLabel("Output Type")
        self.outTypeChooser = QComboBox()
        self.outTypeChooser.addItem(self.SIMPLE_GRID_MAP_STR)
        self.outTypeChooser.addItem(self.POLE_MAP_STR)
        layout.addWidget(label, 7, 0)
        layout.addWidget(self.outTypeChooser, 7, 1)

        
        self.loadButton = QPushButton("Load")        
        self.loadButton.setDisabled(True)
        layout.addWidget(self.loadButton,8 , 1)
        
        self.connect(self.loadButton, SIGNAL("clicked()"), self.loadFile)
        self.connect(self.projectDirButton, SIGNAL("clicked()"), 
                     self.browseForProjectDir)
        self.connect(self.instConfigFileButton, SIGNAL("clicked()"), 
                     self.browseForInstFile)
        self.connect(self.detConfigFileButton, SIGNAL("clicked()"), 
                     self.browseForDetFile)
        self.connect(self.projNameTxt, 
                     SIGNAL("editingFinished()"), 
                     self.projectDirChanged)
#        self.connect(self.projNameTxt, 
#                     SIGNAL("editingFinished()"), 
#                     self.projectNameChanged)
        self.connect(self.instConfigTxt, 
                     SIGNAL("editingFinished()"), 
                     self.instConfigChanged)
        self.connect(self.detConfigTxt, 
                     SIGNAL("editingFinished()"), 
                     self.detConfigChanged)
        
        self.setLayout(layout);
        
    def loadFile(self):
        '''
        Emit a signal to start loading data
        '''
        self.emit(SIGNAL("loadFile"))
        
    def browseForInstFile(self):
        '''
        Launch file selection dialog for instrument file.
        '''
        if self.instConfigTxt.text() == "":
            fileName = QFileDialog.getOpenFileName(None, 
                                               "Select Instrument Config File", 
                                               filter="*.xml")
        else:
            fileDirectory = os.path.dirname(str(self.instConfigTxt.text()))
            fileName = QFileDialog.getOpenFileName(None, 
                                               "Select Instrument Config File", 
                                               filter="*.xml", \
                                               directory = fileDirectory)
        if fileName != "":
            self.instConfigTxt.setText(fileName)
            self.instConfigTxt.emit(SIGNAL("editingFinished()"))

    def browseForDetFile(self):
        '''
        Launch file selection dialog for Detector file.
        '''
        if self.detConfigTxt.text() == "":
            fileName = QFileDialog.getOpenFileName(None, \
                                               "Select Detector Config File", \
                                               filter="*.xml")
        else:
            fileDirectory = os.path.dirname(str(self.detConfigTxt.text()))
            fileName = QFileDialog.getOpenFileName(None, \
                                               "Select Detector Config File", \
                                               filter="*.xml", \
                                               directory = fileDirectory)
        if fileName != "":
            self.detConfigTxt.setText(fileName)
            self.detConfigTxt.emit(SIGNAL("editingFinished()"))

    def browseForProjectDir(self):
        '''
        Launch file selection dialog for instrument file.
        '''
        if self.projNameTxt.text() == "":
            fileName = QFileDialog.getOpenFileName(None, \
                                                   "Select Spec file")
        else:
            fileDirectory = os.path.dirname(str(self.projNameTxt.text()))
            fileName = QFileDialog.getOpenFileName(None,\
                                                   "Select Spec file", \
                                                   directory = fileDirectory)
            
        self.projNameTxt.setText(fileName)
        self.projNameTxt.emit(SIGNAL("editingFinished()"))


    def getDetConfigName(self):
        '''
        Return the selected Detector Configuration file
        '''
        return self.detConfigTxt.text()

    def getInstConfigName(self):
        '''
        Return the Instrument config file name
        '''
        return self.instConfigTxt.text()

    def getProjectDir(self):
        '''
        Return the project directory
        '''
        return os.path.dirname(str(self.projNameTxt.text()))
        
    def getProjectName(self):
        '''
        Return the project name
        '''
        return os.path.splitext(os.path.basename(str(self.projNameTxt.text())))[0]
    
    def getProjectExtension(self):
        '''
        Return the project name
        '''
        return os.path.splitext(os.path.basename(str(self.projNameTxt.text())))[1]

            
    def projectDirChanged(self):
        if os.path.isfile(self.projNameTxt.text()) or \
            self.projNameTxt.text() == "":
            self.checkOkToLoad()
        else:
            message = QMessageBox()
            message.warning(self, \
                             "Warning", \
                             "The project directory entered is invalid")
        
    def projectNameChanged(self):
        self.checkOkToLoad()
        
    def instConfigChanged(self):
        if os.path.isfile(self.instConfigTxt.text()) or \
           self.instConfigTxt.text() == "":
            self.checkOkToLoad()
        else:
            message = QMessageBox()
            message.warning(self, \
                            "Warning", \
                             "The filename entered for the instrument " + \
                             "configuration is invalid")
        
    def detConfigChanged(self):
        if os.path.isfile(self.detConfigTxt.text()) or \
           self.detConfigTxt.text() == "":
            self.checkOkToLoad()
            self.updateROIandNumAvg()
        else:
            message = QMessageBox()
            message.warning(self, \
                             "Warning"\
                             "The filename entered for the detector " + \
                             "configuration is invalid")
        
    def checkOkToLoad(self):
        if os.path.isfile(self.projNameTxt.text()) and \
            os.path.isfile(self.instConfigTxt.text()) and \
            os.path.isfile(self.detConfigTxt.text()):
            self.loadButton.setEnabled(True)
        else:
            self.loadButton.setDisabled(True)
            
    def getOutputType(self):
        return self.outTypeChooser.currentText()
    
    def getScanList(self):
        if str(self.scanNumsTxt.text()) == "":
            return None
        else:
            scans = srange(str(self.scanNumsTxt.text()))
            return scans.list() 
        
    def getDetectorROI(self):
        roiStrings = str(self.detROITxt.text()).split(',')
        roi = []
        print("getting ROIs") + str(roiStrings)
        for value in roiStrings:
            roi.append(int(value))
        print("Done getting ROIs")
        return roi
    
    def getPixelsToAverage(self):
        pixelStrings = str(self.pixAvgTxt.text()).split(',')
        pixels = []
        print "getting number of pixels to average" + str(pixelStrings)
        for value in pixelStrings:
            pixels.append(int(value))
        return pixels
    
    def updateROIandNumAvg(self):
        detConfig = \
            DetectorGeometryForXrayutilitiesReader(self.detConfigTxt.text())
        detector = detConfig.getDetectorById("Pilatus")
        detSize = detConfig.getNpixels(detector)
        print(detSize)
        xmax = detSize[0]
        ymax = detSize[1]
        if xmax < self.roixmax:
            self.roixmax = xmax
        if ymax < self.roiymax:
            self.roiymax = ymax
        self.updateROITxt()
        
    def updateROITxt(self):
        roiStr = str(self.roixmin) +\
                "," +\
                str(self.roixmax) +\
                "," +\
                str(self.roiymin) +\
                "," +\
                str(self.roiymax)
        self.detROITxt.setText(roiStr)
        