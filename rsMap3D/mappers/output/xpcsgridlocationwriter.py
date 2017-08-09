'''
 Copyright (c) 2016, UChicago Argonne, LLC
 See LICENSE file.
'''
from rsMap3D.mappers.output.abstactgridwriter import AbstractGridWriter
import csv

GRID_LOCATION_WRITER_MERGE_STR = "%s_S%d.csv"

class XPCSGridLocationWriter(AbstractGridWriter):
    FILE_EXTENSION = ""
    
    def setFileInfo(self, fileInfo):
        if ((fileInfo is None) or (len(fileInfo) == 0)):
            raise ValueError(self.whatFunction() +
                            "passed no filename information " +
                            "requires a tuple with six members:\n"
                            "1. project filename so that a filename can be " +
                            "constructed if filename is blank\n 2. User " +
                            "filename, and number of pixels for output in " + 
                            "x/y/z directions and output file name")
        elif (len( fileInfo) != 6):
            raise ValueError(self.whatFunction() +
                            "passed no filename information " +
                            "requires a tuple with six members:\n"
                            "1. project filename so that a filename can be " +
                            "constructed if filename is blank\n 2. User " +
                            "filename, and number of pixels for output in " + 
                            "x/y/z directions and outputFileName")
        self.fileInfo.append(fileInfo[0])
        self.fileInfo.append(fileInfo[1])
        self.nx = fileInfo[2]
        self.ny = fileInfo[3]
        self.nz = fileInfo[4]
        self.outputFileName = fileInfo[5]
    
    def write(self):
        
        
        if self.outputFileName == "":
            fileName=(GRID_LOCATION_WRITER_MERGE_STR % 
                               (self.fileInfo[0], \
                                self.fileInfo[1]))
        else:
            fileName=(self.outputFileName)
        
        with open(fileName, "w") as csvfile:
            writer = csv.writer(csvfile, delimiter = ',',
                                 quotechar = '|',
                                 quoting=csv.QUOTE_MINIMAL)
            shape = self.qx.shape
            writer.writerow(("Image Size", shape[0], shape[1]))
            writer.writerow(("qx", "qy", "qz"))
            shape = self.qx.shape
            qx = self.qx.reshape((shape[0]*shape[1]))
            qy = self.qy.reshape((shape[0]*shape[1]))
            qz = self.qz.reshape((shape[0]*shape[1]))
            for x, y, z in zip(qx, qy, qz):
                writer.writerow((x, y, z))
            csvfile.close()
