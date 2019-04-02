'''
 Copyright (c) 2014, UChicago Argonne, LLC
 See LICENSE file.
'''
import os
import logging
from spec2nexus.spec import SpecDataFile
logger = logging.getLogger(__name__)
import PyQt5.QtGui as qtGui
import PyQt5.QtCore as qtCore
import PyQt5.QtWidgets as qtWidgets

from rsMap3D.gui.output.processvtioutputform import ProcessVTIOutputForm
from rsMap3D.gui.output.processxpcsgridlocationform import ProcessXpcsGridLocationForm

try:
    from rsMap3D.datasource.xpcsspecdatasource import XPCSSpecDataSource
except ImportError as ex:
    logger.info("Need to install pypimm in order to use rsMap3D to use XPCS data.")
    #raise ex
from rsMap3D.transforms.polemaptransform3d import PoleMapTransform3D
from rsMap3D.transforms.unitytransform3d import UnityTransform3D
from rsMap3D.gui.input.specxmldrivenfileform import SpecXMLDrivenFileForm
from rsMap3D.gui.rsm3dcommonstrings import BROWSE_STR, EMPTY_STR, WARNING_STR


XPCS_FILE_DIALOG_TITLE = "XPCS File Input"
XPCS_FILE_FILTER = "*.imm"


class XPCSSpecScanFileForm(SpecXMLDrivenFileForm):
    '''
    '''
    FORM_TITLE = "XPCS SPEC/XML Setup"
    
    DET_ROI_REGEXP_1 =  "^(\d*,*)+$"
    DET_ROI_REGEXP_2 =  "^(\d)+,(\d)+,(\d)+,(\d)+$"
    SCAN_LIST_REGEXP = "((\d)+(-(\d)+)?\,( )?)+"

    @staticmethod
    def createInstance(parent=None, appConfig=None):
        return XPCSSpecScanFileForm(parent=parent, appConfig=appConfig)
    
    def __init__(self, pathToReplace=None, replacePathWith=None, **kwargs):
        super(XPCSSpecScanFileForm, self).__init__(**kwargs)

        self.imageFileDialogFilter = XPCS_FILE_FILTER
        
    def _browseForPathToReplace(self):
        if os.path.exists(str(self.projNameTxt.text())) and \
                          (str(self.scanNumsTxt.text()) != ""):
            specFile = str(self.projNameTxt.text())
            scans = self.getScanList()
            sd = SpecDataFile(specFile)
            scan = sd.scans[str(scans[0])]
            scan.interpret()
            if scan.CCD != None:
                try:
                    filePath = scan.CCD['image_dir'][0]
                    self.pathToReplaceTxt.setText(filePath)
                except:
                    qtWidgets.QMessageBox.warning(self, "File patgh not Found", \
                                              "File path not found for scan %s" \
                                              % scan)
            
            self.pathToReplaceTxt.editingFinished.emit()
    
    def _browseForReplacePathWith(self):
        if self.replacePathWithTxt.text() == EMPTY_STR:
            fileName = qtWidgets.QFileDialog.getExistingDirectory(None, \
                                                   XPCS_FILE_DIALOG_TITLE)
        else:
            fileDirectory = os.path.dirname(str(self.replacePathWithTxt.text()))
            fileName = qtWidgets.QFileDialog.getExistingDirectory(None,\
                                                   XPCS_FILE_FILTER, \
                                                   dir = fileDirectory)
            
        if fileName != EMPTY_STR:
            self.replacePathWithTxt.setText(fileName)
            self.replacePathWithTxt.editingFinished.emit()
    
    def checkOkToLoad(self):
        logger.debug ("CheckOKToLoad in xpcs spec scan Fileform")
        superOk = super(XPCSSpecScanFileForm, self).checkOkToLoad()
        xpcsFileOk = self.isXpcsFileNameOK()
         
#         self.okToLoad.emit( superOk & xpcsFileOk)
        self.okToLoad.emit( superOk)
        return superOk
        
    def _createDataBox(self):
        dataBox = super(XPCSSpecScanFileForm, self)._createDataBox()
        dataLayout = dataBox.layout()
        #grab present row count so we can add to the end.
        row = dataLayout.rowCount()
        self._createInstConfig(dataLayout, row)

        row = dataLayout.rowCount() + 1
        self._createDetConfig(dataLayout, row)

        row = dataLayout.rowCount() + 1
        self._createDetectorROIInput(dataLayout, row)
        
        row = dataLayout.rowCount() + 1
        self._createScanNumberInput(dataLayout, row)
            
        row = dataLayout.rowCount() + 1
        self._createOutputType(dataLayout, row)

        row = dataLayout.rowCount() + 1
        self._createHKLOutput(dataLayout, row)


        row = dataLayout.rowCount() + 2
        label1 = qtWidgets.QLabel("<b>The following correct the file path if it has" +
                             " moved from the original location stored in the" +
                             " file.  The first one requires that the spec " + 
                             "file and scan number have been entered</b>")
        label1.setWordWrap(True)
        dataLayout.addWidget(label1, row, 0, 2, -1)
        
        
        row = dataLayout.rowCount() + 1
        label = qtWidgets.QLabel("file path to replace:")
        self.pathToReplaceTxt = qtWidgets.QLineEdit()
        self.pathToReplaceBrowseButton = qtWidgets.QPushButton(BROWSE_STR)
        dataLayout.addWidget(label, row, 0)
        dataLayout.addWidget(self.pathToReplaceTxt, row, 1)
        dataLayout.addWidget(self.pathToReplaceBrowseButton, row, 2)
        
        self.pathToReplaceBrowseButton.clicked.connect(self._browseForPathToReplace)
        self.pathToReplaceTxt.editingFinished.connect(self._pathToReplaceChanged)

        row = dataLayout.rowCount() + 1
        label = qtWidgets.QLabel("replace file path with:")
        self.replacePathWithTxt = qtWidgets.QLineEdit()
        self.replacePathWithBrowseButton = qtWidgets.QPushButton(BROWSE_STR)
        dataLayout.addWidget(label, row, 0)
        dataLayout.addWidget(self.replacePathWithTxt, row, 1)
        dataLayout.addWidget(self.replacePathWithBrowseButton, row, 2)
        
        self.replacePathWithBrowseButton.clicked.connect(self._browseForReplacePathWith)
        self.replacePathWithTxt.editingFinished.connect(self._replacePathWithChanged)
        
        dataBox.setLayout(dataLayout)
        return dataBox

    def getDataSource(self):
        if self.getOutputType() == self.SIMPLE_GRID_MAP_STR:
            self.transform = UnityTransform3D()
        elif self.getOutputType() == self.POLE_MAP_STR:
            self.transform = \
                PoleMapTransform3D(projectionDirection=\
                                   self.fileForm.getProjectionDirection())
        else:
            self.transform = None
        pathToReplaceStr = str(self.pathToReplaceTxt.text())
        replacePathWithStr = str(self.replacePathWithTxt.text())
        if (pathToReplaceStr == ""):
            pathToReplace = None
        else:
            pathToReplace = pathToReplaceStr
        if (replacePathWithStr == ""):
            replacePathWith = None
        else:
            replacePathWith = replacePathWithStr
        self.dataSource = \
            XPCSSpecDataSource(str(self.getProjectDir()), \
                                   str(self.getProjectName()), \
                                   str(self.getProjectExtension()), \
                                   str(self.getInstConfigName()), \
                                   str(self.getDetConfigName()), \
#                                    str(self.getImmFileName()), \
                                   scanList = self.getScanList(), \
                                   transform = self.transform, \
                                   appConfig = self.appConfig,
                                   pathToReplace = pathToReplace,
                                   replacePathWith = replacePathWith
                                  )
        self.dataSource.setProgressUpdater(self.updateProgress)
        self.dataSource.setCurrentDetector(self.currentDetector)
        self.dataSource.loadSource(mapHKL = self.getMapAsHKL())
        return self.dataSource
        

    def getImmFileName(self):
        '''
        Return the IMM file name with XPCS images
        '''
        return str(self.xpcsDataFileTxt.text())
    
    def getOutputForms(self):
        outputForms = []
        outputForms.append(ProcessVTIOutputForm)
        outputForms.append(ProcessXpcsGridLocationForm)
        return outputForms

    def isXpcsFileNameOK(self):
        return self.pathToReplaceTxt.text() != EMPTY_STR
            
    def isReplacePathWithNameOK(self):
        return os.path.isdir(self.replacePathWithTxt.text()) or \
            (self.replacePathWithTxt.text() == EMPTY_STR)
            
    @qtCore.pyqtSlot()
    def _pathToReplaceChanged(self):
        if self.isXpcsFileNameOK():
            self.checkOkToLoad()
        else:
            message = qtWidgets.QMessageBox()
            message.warning(self, \
                             WARNING_STR
                             , \
                             "The path To replace is invalid")

    @qtCore.pyqtSlot()
    def _replacePathWithChanged(self):
        if self.isReplacePathWithNameOK():
            self.checkOkToLoad()
        else:
            message = qtWidgets.QMessageBox()
            message.warning(self, \
                             WARNING_STR
                             , \
                             "The replace Path with is invalid")
