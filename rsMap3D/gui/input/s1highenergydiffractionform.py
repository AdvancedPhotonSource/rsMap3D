'''
 Copyright (c) 2017, UChicago Argonne, LLC
 See LICENSE file.
'''
import os
import logging

from rsMap3D.transforms.unitytransform3d import UnityTransform3D
from rsMap3D.transforms.polemaptransform3d import PoleMapTransform3D
from rsMap3D.datasource.s1highenergydiffractionds import S1ParameterFile,\
    S1HighEnergyDiffractionDS, INCIDENT_ENERGY
from rsMap3D.exception.rsmap3dexception import RSMap3DException
from rsMap3D.gui.input.usescommonoutputtype import UsesCommonOutputTypes
from rsMap3D.config.rsmap3dlogging import METHOD_ENTER_STR, METHOD_EXIT_STR
logger = logging.getLogger(__name__)

import PyQt5.QtGui as qtGui
import PyQt5.QtCore as qtCore
import PyQt5.QtWidgets as qtWidgets

from rsMap3D.gui.input.abstractimageperfileview import AbstractImagePerFileView

from rsMap3D.gui.output.processvtioutputform import ProcessVTIOutputForm
from rsMap3D.gui.input.usesxmldetectorconfig import UsesXMLDetectorConfig
from rsMap3D.gui.input.usesxmlinstconfig import UsesXMLInstConfig
from rsMap3D.gui.rsm3dcommonstrings import BROWSE_STR, EMPTY_STR, WARNING_STR

IMAGE_DIR_DIALOG_TITLE = "Select Image Directory"    
UPDATE_PAR_INFO = "updateParInfo"
RESET_PAR_INFO = "resetParInfo"

class S1HighEnergyDiffractionForm(AbstractImagePerFileView, \
                                  UsesXMLDetectorConfig, UsesXMLInstConfig,
                                  UsesCommonOutputTypes):
    '''
    This class presents information for selecting input files
    '''
    WAITING_FOR_INPUT = "Waiting for input..."
    FORM_TITLE = "Sector 1 High Energy Diffraction"
    HED_IMAGE_FILE_TITLE = "HED Image File"
    HED_IMAGE_FILE_FILTER = "S1 corrected files *.par"
    
    # Set up signals for this class
    updateParInfo = qtCore.pyqtSignal(int, name=UPDATE_PAR_INFO)
    resetParInfo = qtCore.pyqtSignal(name=RESET_PAR_INFO)

    @staticmethod
    def createInstance(parent=None, appConfig=None):
        return S1HighEnergyDiffractionForm(parent=parent, appConfig=appConfig)
    
    def __init__(self, **kwargs):
        '''
         constructor
         '''
        super(S1HighEnergyDiffractionForm, self).__init__( **kwargs)
        logger.debug(METHOD_ENTER_STR)
        self.fileDialogTitle = self.HED_IMAGE_FILE_TITLE
        self.fileDialogFilter = self.HED_IMAGE_FILE_FILTER
        
        self.dataBox = self._createDataBox()
        controlBox =  self._createControlBox()
        
        self.layout.addWidget(self.dataBox)
        self.layout.addWidget(controlBox)
        self.setLayout(self.layout)
        
        self.parFile=None
        
        logger.debug(METHOD_EXIT_STR)
        
    @qtCore.pyqtSlot()
    def _browseForImageDir(self):
        logger.debug("Entering")
        if self.imageDirTxt.text() == EMPTY_STR:
            fileName = qtWidgets.QFileDialog.getExistingDirectory(None, \
                                                   IMAGE_DIR_DIALOG_TITLE)
        else:
            fileDirectory = os.path.dirname(str(self.imageDirTxt.text()))
            fileName = qtWidgets.QFileDialog.getExistingDirectory(None,\
                                                   IMAGE_DIR_DIALOG_TITLE, \
                                                   directory = fileDirectory)
            
        if fileName != EMPTY_STR:
            self.imageDirTxt.setText(fileName)
            self.imageDirTxt.editingFinished.emit()
        logger.debug("Exiting")
    
    def checkOkToLoad(self):
        logger.debug("Entering")
        okToLoad = False
        projFileOK = AbstractImagePerFileView.checkOkToLoad(self)
        if projFileOK:
            parFileName = os.path.join(self.getProjectDir(), \
                                       self.getProjectName() + 
                                       self.getProjectExtension())
            try:
                self.parFile = S1ParameterFile(parFileName)
                maxLine = self.parFile.getNumOfLines()
                self.parFileLineTxt.setRange(1,maxLine)
                self.parFileLineRange.setText("1:" + str(maxLine))
                self.parFileLineTxt.setEnabled(True)
                self.updateParInfo.emit(1)
                
            except RSMap3DException as ex:
                logger.warning("Trouble with S1 par file")
                message = qtWidgets.QMessageBox()
                message.warning(self, \
                                 WARNING_STR, \
                                 str(ex))
                
                self.parFileLineTxt.setEnabled(False)
                self.resetParInfo.emit()
        else:
            self.parFileLineTxt.setEnabled(False)
        instFileOK = self.instFileOk
        detFileOK = self.detFileOk
        imageDirOK = os.path.isdir(str(self.imageDirTxt.text())) 
        if projFileOK and instFileOK and detFileOK and imageDirOK:
            okToLoad = True
        self.okToLoad.emit(okToLoad)
            
        logger.debug("Exiting" + 
                     " projFileOK " + str(projFileOK) +
                     " instFileOK " + str(instFileOK) +
                     " detFileOK " + str(detFileOK) +
                     " imageDirOK " + str(imageDirOK) +
                     " okToLoad " + str(okToLoad))
        return okToLoad
    

    def _createDataBox(self):
        dataBox = super(S1HighEnergyDiffractionForm,self)._createDataBox()
        logger.debug ("Entering")
        dataLayout = dataBox.layout()
        
        row = dataLayout.rowCount()
        label = qtWidgets.QLabel("Par File Line")
        self.parFileLineTxt = qtWidgets.QSpinBox()
        self.parFileLineTxt.setValue(1)
        self.parFileLineTxt.setSingleStep(1)
        self.parFileLineTxt.setRange(1,1)
        self.parFileLineRange = qtWidgets.QLabel("1:1")
        #disable until a good file is found
        self.parFileLineTxt.setEnabled(False)
        dataLayout.addWidget(label, row, 0)
        dataLayout.addWidget(self.parFileLineTxt,row, 1)
        dataLayout.addWidget(self.parFileLineRange, row, 2)
        
        row = dataLayout.rowCount()
        
        # Setup a place to show setup parameters
        label = qtWidgets.QLabel("Angle Info")
        self.angleRange = qtWidgets.QLabel(self.WAITING_FOR_INPUT)
        dataLayout.addWidget(label, row, 0)
        dataLayout.addWidget(self.angleRange, row, 1)
        row = dataLayout.rowCount() + 1
        label = qtWidgets.QLabel("File Info")
        self.fileInfo = qtWidgets.QLabel(self.WAITING_FOR_INPUT)
        dataLayout.addWidget(label, row, 0)
        dataLayout.addWidget(self.fileInfo, row, 1)
        
        
        
        row = dataLayout.rowCount() + 1
        self._createInstConfig(dataLayout, row)
        
        row = dataLayout.rowCount() + 1
        self._createDetConfig(dataLayout, row)
    
        row = dataLayout.rowCount()  + 1
        self._createDetectorROIInput(dataLayout, row)
        
        row = dataLayout.rowCount()  + 1
        self._createNumberOfPixelsToAverage(dataLayout, row, True)
        
        
        row = dataLayout.rowCount()  + 1
        label = qtWidgets.QLabel("Image Directory:")
        self.imageDirTxt = qtWidgets.QLineEdit()
        self.imageDirBrowseButton = qtWidgets.QPushButton(BROWSE_STR)
        dataLayout.addWidget(label, row, 0)
        dataLayout.addWidget(self.imageDirTxt, row, 1)
        dataLayout.addWidget(self.imageDirBrowseButton, row, 2)
        

        row = dataLayout.rowCount() + 1
        posDoubleValidator = qtGui.QDoubleValidator()
        posDoubleValidator.setBottom(0.000000)
        label = qtWidgets.QLabel("Override detector distance: ")
        self.detectorDistanceOverrideTxt = qtWidgets.QLineEdit(str(0.0))
        self.detectorDistanceOverrideTxt.setValidator(posDoubleValidator)
        self.detectorDistanceActive = qtWidgets.QLabel()
        dataLayout.addWidget(label, row, 0)
        dataLayout.addWidget(self.detectorDistanceOverrideTxt, row, 1)
        dataLayout.addWidget(self.detectorDistanceActive,row, 2)
         
        row = dataLayout.rowCount() + 1
        label = qtWidgets.QLabel("Override Incident Energy: ")
        self.incidentEnergyOverrideTxt = qtWidgets.QLineEdit(str(0.0))
        self.incidentEnergyOverrideTxt.setValidator(posDoubleValidator)
        self.incidentEnergyActive = qtWidgets.QLabel()
        dataLayout.addWidget(label, row, 0)
        dataLayout.addWidget(self.incidentEnergyOverrideTxt, row, 1)
        dataLayout.addWidget(self.incidentEnergyActive, row, 2)
         
        row = dataLayout.rowCount() + 1
        self.angleLimitValidator = qtGui.QDoubleValidator()
        self.angleLimitValidator.setBottom(-360.0)
        self.angleLimitValidator.setTop(360.0)
#         angleLimitValidator.setNotation(qtGui.QDoubleValidator.StandardNotation)
        label = qtWidgets.QLabel("Offset Angle: ")
        self.offsetAngleTxt = qtWidgets.QLineEdit(str(0.0))
        self.offsetAngleTxt.setValidator(self.angleLimitValidator)
        self.offsetAngleActive = qtWidgets.QLabel()
        dataLayout.addWidget(label, row, 0)
        dataLayout.addWidget(self.offsetAngleTxt, row, 1)
        dataLayout.addWidget(self.offsetAngleActive, row, 2)
        
        
        row = dataLayout.rowCount()  + 1
        self._createOutputType(dataLayout, row)
        
        row = dataLayout.rowCount()  + 1
        self._createHKLOutput(dataLayout, row)
        self.imageDirBrowseButton.clicked.connect(self._browseForImageDir)
        self.imageDirTxt.editingFinished.connect(self._imageDirChanged)
        self.updateParInfo[int].connect(self._updateParInfo)
        self.resetParInfo.connect(self._resetParInfo)
        self.parFileLineTxt.valueChanged[int].connect(self._parFileLineChanged)
        self.detectorDistanceOverrideTxt.editingFinished.connect(
                self._detectorDistanceOverrideChanged)
        self.incidentEnergyOverrideTxt.editingFinished.connect(
            self._incidentEnergyOverrideChanged)
        self.offsetAngleTxt.editingFinished.connect(
            self._offsetAngleChanged)
        self.detSelect.currentIndexChanged[str].connect(self._detectorSelectedIndexChanged)
        logger.debug("Exiting")
        
        
        return dataBox
    
    @qtCore.pyqtSlot()
    def _detectorDistanceOverrideChanged(self):
        logger.debug(METHOD_ENTER_STR)
        overrideDistance = float(self.detectorDistanceOverrideTxt.text())
        logger.debug("overrideDistance %f " % overrideDistance)
        if overrideDistance == 0.0:
            detector = self.detConfig.getDetectorById(str(self.currentDetector))
            logger.debug("detector currently: " + str(detector))
            self.detectorDistance = self.detConfig.getDistance(detector)
            self.detectorDistanceActive.setText(str(self.detectorDistance))
        else:
            self.detectorDistance = float(self.detectorDistanceOverrideTxt.text())
            self.detectorDistanceActive.setText(str(self.detectorDistance))
        logger.debug(METHOD_EXIT_STR)
        
    @qtCore.pyqtSlot(str)
    def _detectorSelectedIndexChanged(self, currentDetector):
        logger.debug(METHOD_ENTER_STR)
        if float(self.detectorDistanceOverrideTxt.text()) == 0.0:
            detector = self.detConfig.getDetectorById(str(currentDetector))
            logger.debug("detector currently: " + str(detector))
            self.detectorDistance = self.detConfig.getDistance(detector)
            self.detectorDistanceActive.setText(str(self.detectorDistance))
        else:
            self.detectorDistance = float(self.detectorDistanceOverrideTxt.text())
            self.detectorDistanceActive.setText(str(self.detectorDistance))
        logger.debug(METHOD_EXIT_STR)
        
    def getOffsetAngle(self):
        '''
        returns an offset angle which will be added to the motor angle on the
        spinning axis
        '''
        logger.debug(METHOD_ENTER_STR)
        offsetAngle = float(self.offsetAngleTxt.text())
        logger.debug(METHOD_EXIT_STR % str(offsetAngle))
        return offsetAngle
    
    def getDataSource(self):
        logger.debug(METHOD_ENTER_STR)
        if self.getOutputType() == self.SIMPLE_GRID_MAP_STR:
            self.transform = UnityTransform3D()
        elif self.getOutputType() == self.POLE_MAP_STR:
            self.transform = \
                PoleMapTransform3D(projectionDirection=\
                                   self.getProjectionDirection())
        else:
            self.transform = None
        
        self.dataSource = \
            S1HighEnergyDiffractionDS(str(self.getProjectDir()), \
                                   str(self.getProjectName()), \
                                   str(self.getProjectExtension()), \
                                   str(self.getInstConfigName()), \
                                   str(self.getDetConfigName()), \
                                   str(self.getImageDirName()), \
                                   transform = self.transform, \
                                   scanList = self.getScanList(), \
                                   roi = self.getDetectorROI(), \
                                   pixelsToAverage = \
                                    [1,1], \
                                 badPixelFile = None, \
                                 flatFieldFile = None, \
                                 detectorDistanceOverride = \
                                    self.getDetectorDistanceOverride(), \
                                 incidentEnergyOverride = 
                                    self.getIncidentEnergyOverride(), \
                                offsetAngle = self.getOffsetAngle(), \
                                appConfig = self.appConfig
                                )
        self.dataSource.setProgressUpdater(self.updateProgress)
        self.dataSource.setCurrentDetector(self.currentDetector)
        self.dataSource.loadSource(mapHKL = self.getMapAsHKL())

        logger.debug(METHOD_EXIT_STR)
        return self.dataSource
    
    def getDetectorDistanceOverride(self):
        '''
        return a value to override the detector distance in the detector
        config file
        '''
        logger.debug(METHOD_ENTER_STR)
        detectorDistanceOverride = \
            float(self.detectorDistanceOverrideTxt.text())
        logger.debug(METHOD_ENTER_STR % str(detectorDistanceOverride))
        return detectorDistanceOverride
    
    
    
    
    def getImageDirName(self):
        return str(self.imageDirTxt.text())
        
    def getIncidentEnergyOverride(self):
        '''
        get a value to override the energy read from the instrument par file 
        used to load up the values associated with differrent scans.
        '''
        logger.debug(METHOD_ENTER_STR)
        incidentEnergyOverride = float(self.incidentEnergyOverrideTxt.text())
        logger.debug(METHOD_EXIT_STR % str(incidentEnergyOverride))
        return incidentEnergyOverride
 
    def getScanList(self):
        logger.debug(METHOD_ENTER_STR)
        scan = int (self.parFileLineTxt.value())
        scanList = [scan,]
        logger.debug(METHOD_EXIT_STR + str(scanList))
        return scanList
    
    def getOutputForms(self):
        logger.debug(METHOD_ENTER_STR)

        outputForms = []
        outputForms.append(ProcessVTIOutputForm)
        logger.debug(METHOD_EXIT_STR + str(outputForms))
        return outputForms

    @qtCore.pyqtSlot()
    def _imageDirChanged(self):
        logger.debug(METHOD_ENTER_STR)
        if os.path.isdir(self.imageDirTxt.text()) or \
            self.imageDirTxt.text() == EMPTY_STR:
            self.checkOkToLoad()
        else:
            message = qtWidgets.QMessageBox() 
            message.warning(self, \
                             WARNING_STR
                             , \
                             "The IMM file entered is invalid")
        logger.debug(METHOD_EXIT_STR)

    @qtCore.pyqtSlot()
    def _incidentEnergyOverrideChanged(self):
        logger.debug(METHOD_ENTER_STR)
        self.incidentEnergyOverride = float(self.incidentEnergyOverrideTxt.text())
        lines = int(self.parFileLineTxt.text())
        if self.incidentEnergyOverride == 0.0:
            self.incidentEnergy = self.parFile.getEnergy([lines,])[lines]
            self.incidentEnergyActive.setText((str(self.incidentEnergy[INCIDENT_ENERGY])))
        else:
            self.incidentEnergyActive.setText((str(self.incidentEnergyOverride)))
        logger.debug(METHOD_EXIT_STR)
        
    @qtCore.pyqtSlot()
    def _offsetAngleChanged(self):
        logger.debug(METHOD_ENTER_STR)
        state = self.angleLimitValidator.validate(self.offsetAngleTxt.text(),0)
        logger.debug(METHOD_EXIT_STR + str(state))
        
    @qtCore.pyqtSlot(int)
    def _parFileLineChanged(self, lineNum):
        self.updateParInfo.emit(lineNum)
    
    @qtCore.pyqtSlot()
    def _resetParInfo(self):
        self.angleRange.setText(self.WAITING_FOR_INPUT)
        self.fileInfo.setText(self.WAITING_FOR_INPUT)        

    @qtCore.pyqtSlot(int)
    def _updateParInfo(self, lines):
        logger.debug("lines: " + str(lines))
        angleData = self.parFile.getAngleData([lines,])
        fileData = self.parFile.getFileData([lines,])
        logger.debug("updating angle info to "  + str(angleData))
        logger.debug("updating file info to "  + str(fileData))
        self.angleRange.setText(str(angleData))
        self.fileInfo.setText(str(fileData))
        self.incidentEnergyOverride = float(self.incidentEnergyOverrideTxt.text())
        if self.incidentEnergyOverride == 0.0:
            self.incidentEnergy = self.parFile.getEnergy([lines,])[lines]
            self.incidentEnergyActive.setText((str(self.incidentEnergy[INCIDENT_ENERGY])))
        else:
            self.incidentEnergyActive.setText((str(self.incidentEnergyOverride)))
            
                
                