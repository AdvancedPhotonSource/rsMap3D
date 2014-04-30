'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''
import os

from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QRegExp
from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QProgressBar
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QFileDialog
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QComboBox
from PyQt4.QtGui import QCheckBox
from PyQt4.QtGui import QRegExpValidator
from PyQt4.QtGui import QRadioButton
from PyQt4.QtGui import QButtonGroup

from rsMap3D.utils.srange import srange
from rsMap3D.datasource.DetectorGeometryForXrayutilitiesReader\
     import DetectorGeometryForXrayutilitiesReader
from rsMap3D.datasource.InstForXrayutilitiesReader import InstForXrayutilitiesReader

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
        self.projectionDirection = [0,0,1]
        layout = QGridLayout()

        row = 0
        label = QLabel("Project File:");
        self.projNameTxt = QLineEdit()
        self.projectDirButton = QPushButton("Browse")
        layout.addWidget(label, row, 0)
        layout.addWidget(self.projNameTxt, row, 1)
        layout.addWidget(self.projectDirButton, row, 2)

        row += 1
        label = QLabel("Instrument Config File:");
        self.instConfigTxt = QLineEdit()
        self.instConfigFileButton = QPushButton("Browse")
        layout.addWidget(label, row, 0)
        layout.addWidget(self.instConfigTxt, row, 1)
        layout.addWidget(self.instConfigFileButton, row, 2)

        row += 1
        label = QLabel("Detector Config File:");
        self.detConfigTxt = QLineEdit()
        self.detConfigFileButton = QPushButton("Browse")
        layout.addWidget(label, row, 0)
        layout.addWidget(self.detConfigTxt, row, 1)
        layout.addWidget(self.detConfigFileButton, row, 2)
        
        row += 1
        self.fieldCorrectionGroup = QButtonGroup(self)
        self.noFieldRadio = QRadioButton("None")
        self.badPixelRadio = QRadioButton("Bad Pixel File")
        self.flatFieldRadio = QRadioButton("Flat Field Correction")
        self.fieldCorrectionGroup.addButton(self.noFieldRadio, 1)
        self.fieldCorrectionGroup.addButton(self.badPixelRadio, 2)
        self.fieldCorrectionGroup.addButton(self.flatFieldRadio, 3)
        self.badPixelFileTxt = QLineEdit()
        self.flatFieldFileTxt = QLineEdit()
        self.badPixelFileBrowseButton = QPushButton("Browse")
        self.flatFieldFileBrowseButton = QPushButton("Browse")
        
        layout.addWidget(self.noFieldRadio, row, 0)
        row += 1
        layout.addWidget(self.badPixelRadio, row, 0)
        layout.addWidget(self.badPixelFileTxt, row, 1)
        layout.addWidget(self.badPixelFileBrowseButton, row, 2)
        row += 1
        layout.addWidget(self.flatFieldRadio, row, 0)
        layout.addWidget(self.flatFieldFileTxt, row, 1)
        layout.addWidget(self.flatFieldFileBrowseButton, row, 2)
        
        row += 1
        label = QLabel("Number of Pixels To Average:");
        self.pixAvgTxt = QLineEdit("1,1")
        rxAvg = QRegExp('(\d)+,(\d)+')
        self.pixAvgTxt.setValidator(QRegExpValidator(rxAvg,self.pixAvgTxt))
        layout.addWidget(label, row, 0)
        layout.addWidget(self.pixAvgTxt, row, 1)

        row += 1
        label = QLabel("Detector ROI:");
        self.detROITxt = QLineEdit()
        self.updateROITxt()
        rxROI = QRegExp('(\d)+,(\d)+,(\d)+,(\d)+')
        self.detROITxt.setValidator(QRegExpValidator(rxROI,self.detROITxt))
        layout.addWidget(label, row, 0)
        layout.addWidget(self.detROITxt, row, 1)
        
        row += 1
        label = QLabel("Scan Numbers")
        self.scanNumsTxt = QLineEdit()
        rx = QRegExp('((\d)+(-(\d)+)?\,( )?)+')
        self.scanNumsTxt.setValidator(QRegExpValidator(rx,self.scanNumsTxt))
        layout.addWidget(label, row, 0)
        layout.addWidget(self.scanNumsTxt, row, 1)

        row += 1
        label = QLabel("Output Type")
        self.outTypeChooser = QComboBox()
        self.outTypeChooser.addItem(self.SIMPLE_GRID_MAP_STR)
        self.outTypeChooser.addItem(self.POLE_MAP_STR)
        layout.addWidget(label, row, 0)
        layout.addWidget(self.outTypeChooser, row, 1)

        row += 1
        label = QLabel("HKL output")
        layout.addWidget(label, row, 0)
        self.hklCheckbox = QCheckBox()
        layout.addWidget(self.hklCheckbox, row, 1)
       
        row += 1
        self.progressBar = QProgressBar()
        layout.addWidget(self.progressBar, row, 1)
        
        row += 1
        self.loadButton = QPushButton("Load")        
        self.loadButton.setDisabled(True)
        layout.addWidget(self.loadButton, row, 1)
        self.cancelButton = QPushButton("Cancel")        
        self.cancelButton.setDisabled(True)
#        self.cancelButton.setDisabled(True)
        layout.addWidget(self.cancelButton, row, 2)
        
        # Add Signals between widgets
        self.connect(self.loadButton, SIGNAL("clicked()"), self.loadFile)
        self.connect(self.cancelButton, SIGNAL("clicked()"), self.cancelLoadFile)
        self.connect(self.projectDirButton, SIGNAL("clicked()"), 
                     self.browseForProjectDir)
        self.connect(self.instConfigFileButton, SIGNAL("clicked()"), 
                     self.browseForInstFile)
        self.connect(self.detConfigFileButton, SIGNAL("clicked()"), 
                     self.browseForDetFile)
        self.connect(self.projNameTxt, 
                     SIGNAL("editingFinished()"), 
                     self.projectDirChanged)
        self.connect(self.instConfigTxt, 
                     SIGNAL("editingFinished()"), 
                     self.instConfigChanged)
        self.connect(self.detConfigTxt, 
                     SIGNAL("editingFinished()"), 
                     self.detConfigChanged)
        self.connect(self.outTypeChooser, \
                     SIGNAL("currentIndexChanged(QString )"), \
                     self.outputTypeChanged)
        self.connect(self.fieldCorrectionGroup,\
                     SIGNAL("buttonClicked(QAbstractButton *)"), \
                     self.fieldCorrectionTypeChanged)
        self.connect(self.badPixelFileTxt,
                     SIGNAL("editingFinished()"),
                     self.badPixelFileChanged)
        self.connect(self.flatFieldFileTxt,
                     SIGNAL("editingFinished()"),
                     self.flatFieldFileChanged)
        self.connect(self.badPixelFileBrowseButton, \
                     SIGNAL("clicked()"), \
                     self.browseBadPixelFileName)
        self.connect(self.flatFieldFileBrowseButton, \
                     SIGNAL("clicked()"), \
                     self.browseFlatFieldFileName)
        self.connect(self, SIGNAL("updateProgress"), self.setProgress)
        self.noFieldRadio.setChecked(True)
        #print self.noFieldRadio.
        self.fieldCorrectionTypeChanged(*(self.noFieldRadio,))
        self.setLayout(layout);
        
    def loadFile(self):
        '''
        Emit a signal to start loading data
        '''
        self.emit(SIGNAL("loadFile"))

    def badPixelFileChanged(self):
        '''
        Do some verification when the bad pixel file changes
        '''
        if os.path.isfile(self.badPixelFileTxt.text()) or \
           self.badPixelFileTxt.text() == "":
            self.checkOkToLoad()
        else:
            message = QMessageBox()
            message.warning(self, \
                            "Warning", \
                             "The filename entered for the bad pixel " + \
                             "file is invalid")
            
                
    def browseBadPixelFileName(self):
        '''
        Launch file browser for bad pixel file
        '''
        if self.badPixelFileTxt.text() == "":
            fileName = QFileDialog.getOpenFileName(None, 
                                               "Select Bad Pixel File", 
                                               filter="Bad Pixel *.txt ;;" + \
                                                      "All Files *.*")
        else:
            fileDirectory = os.path.dirname(str(self.badPixelFileTxt.text()))
            fileName = QFileDialog.getOpenFileName(None, 
                                               "Select Bad Pixel File", 
                                               filter="Bad Pixel *.txt ;;" + \
                                                      "All Files *.*", \
                                               directory = fileDirectory)
        if fileName != "":
            self.badPixelFileTxt.setText(fileName)
            self.badPixelFileTxt.emit(SIGNAL("editingFinished()"))

    
    def browseFlatFieldFileName(self):
        '''
        Launch file browser for Flat field file
        '''
        if self.flatFieldFileTxt.text() == "":
            fileName = QFileDialog.getOpenFileName(None, 
                                               "Select Flat Field File", 
                                               filter="TIFF Files (*.tiff *.tif)")
        else:
            fileDirectory = os.path.dirname(str(self.flatFieldFileTxt.text()))
            fileName = QFileDialog.getOpenFileName(None, 
                                               "Select Flat Field File", 
                                               filter="TIFF Files (*.tiff *.tif)", \
                                               directory = fileDirectory)
        if fileName != "":
            self.flatFieldFileTxt.setText(fileName)
            self.flatFieldFileTxt.emit(SIGNAL("editingFinished()"))
    
    def browseForInstFile(self):
        '''
        Launch file selection dialog for instrument file.
        '''
        if self.instConfigTxt.text() == "":
            fileName = QFileDialog.getOpenFileName(None, 
                                        "Select Instrument Config File", 
                                        filter="Instrument Config *.xml" + \
                                                " ;; All Files *.*")
        else:
            fileDirectory = os.path.dirname(str(self.instConfigTxt.text()))
            fileName = QFileDialog.getOpenFileName(None, 
                                        "Select Instrument Config File", 
                                        filter="Instrument Config *.xml" + \
                                                 " ;; All Files *.*", \
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
                                     "Select Spec file",
                                     filter=("SPEC files *.spc *.spec ;; " + \
                                                           "All files *.*"))
        else:
            fileDirectory = os.path.dirname(str(self.projNameTxt.text()))
            fileName = QFileDialog.getOpenFileName(None,\
                                                   "Select Spec file", \
                                                   directory = fileDirectory,
                                     filter=("SPEC files *.spc *.spec ;; " + \
                                                           "All files *.*"))
            
        if fileName != "":
            self.projNameTxt.setText(fileName)
            self.projNameTxt.emit(SIGNAL("editingFinished()"))


    def cancelLoadFile(self):
        ''' Send signal to cancel a file load'''
        self.emit(SIGNAL("cancelLoadFile"))
        
    def fieldCorrectionTypeChanged(self, *fieldCorrType):
        if fieldCorrType[0].text() == "None":
            self.badPixelFileTxt.setDisabled(True)
            self.badPixelFileBrowseButton.setDisabled(True)
            self.flatFieldFileTxt.setDisabled(True)
            self.flatFieldFileBrowseButton.setDisabled(True)
        elif fieldCorrType[0].text() == "Bad Pixel File":
            self.badPixelFileTxt.setDisabled(False)
            self.badPixelFileBrowseButton.setDisabled(False)
            self.flatFieldFileTxt.setDisabled(True)
            self.flatFieldFileBrowseButton.setDisabled(True)
        elif fieldCorrType[0].text() == "Flat Field Correction":
            self.badPixelFileTxt.setDisabled(True)
            self.badPixelFileBrowseButton.setDisabled(True)
            self.flatFieldFileTxt.setDisabled(False)
            self.flatFieldFileBrowseButton.setDisabled(False)
        self.checkOkToLoad()
            
            
    def flatFieldFileChanged(self):
        '''
        Do some verification when the flat field file changes
        '''
        if os.path.isfile(self.flatFieldFileTxt.text()) or \
           self.flatFieldFileTxt.text() == "":
            self.checkOkToLoad()
        else:
            message = QMessageBox()
            message.warning(self, \
                            "Warning", \
                             "The filename entered for the flat field " + \
                             "file is invalid")
                
    def getBadPixelFileName(self):
        '''
        Return the badPixel file name.  If empty or if the bad pixel radio 
        button is not checked return None
        '''
        if (str(self.badPixelFileTxt.text()) == "") or \
           (not self.badPixelRadio.isChecked()):
            return None
        else:
            return str(self.badPixelFileTxt.text())
        
    def getDetConfigName(self):
        '''
        Return the selected Detector Configuration file
        '''
        return self.detConfigTxt.text()

    def getFlatFieldFileName(self):
        '''
        Return the flat field file name.  If empty or if the bad pixel radio 
        button is not checked return None
        '''
        if (str(self.flatFieldFileTxt.text()) == "") or \
           (not self.flatFieldRadio.isChecked()):
            return None
        else:
            return str(self.flatFieldFileTxt.text())
        
    def getMapAsHKL(self):
        return self.hklCheckbox.isChecked()
        
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
  
    def getProjectionDirection(self):
        '''
        Return projection direction for stereographic projections
        '''
        return self.projectionDirection
          
    def instConfigChanged(self):
        if os.path.isfile(self.instConfigTxt.text()) or \
           self.instConfigTxt.text() == "":
            self.checkOkToLoad()
            self.updateProjectionDirection()
        else:
            message = QMessageBox()
            message.warning(self, \
                            "Warning", \
                             "The filename entered for the instrument " + \
                             "configuration is invalid")
        
    def detConfigChanged(self):
        '''
        '''
        if os.path.isfile(self.detConfigTxt.text()) or \
           self.detConfigTxt.text() == "":
            self.checkOkToLoad()
            self.updateROIandNumAvg()
        else:
            message = QMessageBox()
            message.warning(self, \
                             "Warning",\
                             "The filename entered for the detector " + \
                             "configuration is invalid")
        
    def checkOkToLoad(self):
        '''
        '''
        if os.path.isfile(self.projNameTxt.text()) and \
            os.path.isfile(self.instConfigTxt.text()) and \
            os.path.isfile(self.detConfigTxt.text()) and \
            (self.noFieldRadio.isChecked() or \
             (self.badPixelRadio.isChecked() and \
              not (str(self.badPixelFileTxt.text()) == "")) or \
             (self.flatFieldRadio.isChecked() and \
              not (str(self.flatFieldFileTxt.text()) == ""))):
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
    
    def outputTypeChanged(self, typeStr):
        '''
        If the output is selected to be a simple grid map type then allow
        the user to select HKL as an output.
        '''
        if typeStr == self.SIMPLE_GRID_MAP_STR:
            self.hklCheckbox.setEnabled(True)
        else:
            self.hklCheckbox.setDisabled(True)
            self.hklCheckbox.setCheckState(False)
            
    def setLoadOK(self):
        '''
        If Load is OK the load button is enabled and the cancel button is 
        disabled
        '''
        self.loadButton.setDisabled(False)
        self.cancelButton.setDisabled(True)

    def setCancelOK(self):
        '''
        If Cancel is OK the loadbutton is disabled and the cancel button is 
        enabled
        '''
        self.loadButton.setDisabled(True)
        self.cancelButton.setDisabled(False)

    def setProgressLimits(self, min, max):
        '''
        Set the limits on the progress bar
        '''
        self.progressBar.setMinimum(min)
        self.progressBar.setMaximum(max)
        
    def setProgress(self, value, maxValue):
        '''
        Set the value to be displayed in the progress bar.
        '''
        self.progressBar.setMinimum(1)
        self.progressBar.setMaximum(maxValue)
        self.progressBar.setValue(value)
        
    def updateProjectionDirection(self):
        instConfig = \
            InstForXrayutilitiesReader(self.instConfigTxt.text())
        self.projectionDirection = instConfig.getProjectionDirection()
        
    def updateROIandNumAvg(self):
        '''
        Set defailt values into the ROI and number of pixel to average text 
        boxes
        '''
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
        '''
        Update the ROI string with the current value of the ROI
        '''
        roiStr = str(self.roixmin) +\
                "," +\
                str(self.roixmax) +\
                "," +\
                str(self.roiymin) +\
                "," +\
                str(self.roiymax)
        self.detROITxt.setText(roiStr)
        
    def updateProgress(self, value, maxValue):
        '''
        Emit a signal to update the progress bar
        '''
        self.emit(SIGNAL("updateProgress"), value, maxValue)
