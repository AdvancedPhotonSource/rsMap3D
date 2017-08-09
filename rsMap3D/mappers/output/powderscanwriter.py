'''
 Copyright (c) 2017 UChicago Argonne, LLC
 See LICENSE file.
'''
import logging
logger = logging.getLogger(__name__)
import inspect
import numpy as np
from rsMap3D.gui.rsm3dcommonstrings import EMPTY_STR


FILENAME_MERGE_STR = "%s_S%03d.xye"

class PowderScanWriter():
    
    def __init__(self):
        self.gridData = None
        self.numPoints = None
        self.fileInfo = []
        self.outputFileName = None
        
    def setData(self, x, y, e):
        self.gridData = np.transpose(np.array([x, y, e]))
        self.fileInfo = []
        
    def setFileInfo(self, fileInfo):
        if ((fileInfo is None) or (len(fileInfo) ==0) ):
            raise ValueError(self.whatFunction() +
                             "passed no filename information." +
                             "requires a tuple with four members:\n" +
                             "1. project filename so that a filename can be" +
                             "constructed if filename is blank\n" +
                             "2. User filename\n" + 
                             "3 number of datapints" +
                             "4. outputFileName")
        elif len(fileInfo) != 4:
            raise ValueError(self.whatFunction() +
                             "passed no filename information." +
                             "requires a tuple with four members:\n" +
                             "1. project filename so that a filename can be" +
                             "constructed if filename is blank\n" +
                             "2. User filename\n" + 
                             "3 number of datapints" +
                             "4. outputFileName")
        self.fileInfo.append(fileInfo[0])
        self.fileInfo.append(fileInfo[1])
        self.numPoints = fileInfo[2]
        self.outputFileName = fileInfo[3]

            
        
    def write(self):
        
        logger.debug("fileInfo[0] %s, fileInfo[1] %s" %
                     (self.fileInfo[0], self.fileInfo[1]))
        if self.outputFileName == EMPTY_STR or self.outputFileName is None:
            outputFileName = FILENAME_MERGE_STR % \
                            (self.fileInfo[0], self.fileInfo[1])
        else:
            outputFileName = self.outputFileName
        logger.debug("outputFileName %s " % outputFileName)
        with open(outputFileName, "w") as outFile:
            outFile.write("# SPECfile=%s\n" % self.fileInfo[0])
            outFile.write("# Scan Numbers=%s\n" % self.fileInfo[1])
            outFile.write("# Instrument configuration=%s\n")
            outFile.write("# Detector Configuration=%s\n" )
            outFile.write("# Bad Pixel File %s")
            outFile.write("#\n") 
            logger.debug("self.gridData %s" % self.gridData)
            logger.debug("self.gridData.shape %s" % str(self.gridData.shape))
            outFile.write("# x_min = %.4f\n" % self.gridData[0][0])
            outFile.write("# x_max = %.4f\n" % self.gridData[-1][0])
            x_step = (self.gridData[-1][0] - self.gridData[0][0])/self.numPoints
            outFile.write("# x_step = %.4f\n" % x_step)
            outFile.write("# x_npts = %d\n" % self.numPoints)
#            outFile.write("# Wavelength = %.6f\n" % self.wavelength)
            outFile.write("# Temperature = n/a\n")
            outFile.write("# \n")
            outFile.write("# TwoTheta Intensity Error\n")
            np.savetxt(outFile, self.gridData, fmt="%10.6e %10.6e %10.6e")
        
    def whatFunction(self):
        return inspect.stack()[1][3]