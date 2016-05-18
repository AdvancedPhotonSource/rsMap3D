'''
 Copyright (c) 2014, UChicago Argonne, LLC
 See LICENSE file.
'''

import PyQt4.QtGui as qtGui
import PyQt4.QtCore as qtCore

from rsMap3D.datasource.xpcsspecdatasource import XPCSSpecDataSource
from rsMap3D.transforms.polemaptransform3d import PoleMapTransform3D
from rsMap3D.transforms.unitytransform3d import UnityTransform3D
from rsMap3D.gui.input.specxmldrivenfileform import SpecXMLDrivenFileForm


XPCS_FILE_DIALOG_TITLE = "XPCS File Input"
XPCS_FILE_FILTER = "*.imm"


class XPCSSpecScanFileForm(SpecXMLDrivenFileForm):
    
    DET_ROI_REGEXP_1 =  "^(\d*,*)+$"
    DET_ROI_REGEXP_2 =  "^(\d)+,(\d)+,(\d)+,(\d)+$"
    SCAN_LIST_REGEXP = "((\d)+(-(\d)+)?\,( )?)+"

    def __init__(self, parent=None):
        super(XPCSSpecScanFileForm, self).__init__(parent)

        self.imageFileDialogFilter = XPCS_FILE_FILTER
        
    def _createDataBox(self):
        dataBox = super(XPCSSpecScanFileForm, self)._createDataBox()
        dataLayout = dataBox.layout()
        #grab present row count so we can add to the end.
        row = dataLayout.rowCount()
        self._createInstConfig(dataLayout, row)

        row += 1
        self._createDetConfig(dataLayout, row)

        row += 1
        self._createDetectorROIInput(dataLayout, row)
        
        row += 1
        self._createScanNumberInput(dataLayout, row)
            
        row += 1
        self._createOutputType(dataLayout, row)
        # Add Signals between widgets

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
            
        self.dataSource = \
            XPCSSpecDataSource(str(self.getProjectDir()), \
                                   str(self.getProjectName()), \
                                   str(self.getProjectExtension()), \
                                   str(self.getInstConfigName()), \
                                   str(self.getDetConfigName()), \
                                   scanList = self.getScanList()
                                  )
        self.dataSource.setProgressUpdater(self.updateProgress)
        self.dataSource.loadSource(mapHKL = self.getMapAsHKL())
        return self.dataSource
        
