'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''
from rsMap3D.exception.rsmap3dexception import ScanDataMissingException
from rsMap3D.datasource.Sector33SpecDataSource import IMAGE_DIR_MERGE_STR,\
    Sector33SpecFileException,  LoadCanceledException
import time
import os
from spec2nexus.spec import SpecDataFile
from rsMap3D.gui.rsm3dcommonstrings import CANCEL_STR
from rsMap3D.datasource.specxmldrivendatasource import SpecXMLDrivenDataSource

class XPCSSpecDataSource(SpecXMLDrivenDataSource):
    
    def __init__(self,
                 projectDir,
                 projectName,
                 projectExtension,
                 instConfigFile,
                 detConfigFile,
                 **kwargs):
        
        super(XPCSSpecDataSource, self).__init__(projectDir,
                                                 projectName,
                                                 projectExtension,
                                                 instConfigFile,
                                                 detConfigFile,
                                                 **kwargs)
        self.cancelLoad = False

    
    def getGeoAngles(self, scan, angleNames):
        """
        This function returns all of the geometry angles for the
        for the scan as a N-by-num_geo array, where N is the number of scan
        points and num_geo is the number of geometry motors.
        """
#        scan = self.sd[scanNo]
        geoAngles = self.getScanAngles(scan, angleNames)
        return geoAngles
        
    def loadSource(self, mapHKL=False):
        #Load up the instrument config XML file
        self.loadInstrumentXMLConfig()
        #Load up the detector configuration file
        self.loadDetectorXMLConfig()
        
        self.specFile = os.path.join(self.projectDir, self.projectName + \
                                     self.projectExt)
        try:
            self.sd = SpecDataFile(self.specFile)
            self.mapHKL = mapHKL
            maxScan = int(self.sd.getMaxScanNumber())
            print str(maxScan) + " scans"
            if self.scans  == None:
                self.scans = range(1, maxScan+1)
            imagePath = os.path.join(self.projectDir, 
                            IMAGE_DIR_MERGE_STR % self.projectName)
            
            self.imageBounds = {}
            self.imageToBeUsed = {}
            self.availableScans = []
            self.incidentEnergy = {}
            self.ubMatrix = {}
            self.scanType = {}
            self.progress = 0
            self.progressInc = 1
            # Zero the progress bar at the beginning.
            if self.progressUpdater <> None:
                self.progressUpdater(self.progress, self.progressMax)
            for scan in self.scans:
                if (self.cancelLoad):
                    self.cancelLoad = False
                    raise LoadCanceledException(CANCEL_STR)
                
                else:
#                     if (os.path.exists(os.path.join(imagePath, \
#                                             SCAN_NUMBER_MERGE_STR % scan))):
                    curScan = self.sd.scans[str(scan)]
                    try:
                        angles = self.getGeoAngles(curScan, self.angleNames)
                        self.availableScans.append(scan)
                        self.scanType[scan] = \
                            self.sd.scans[str(scan)].scanCmd.split()[0]
                        if self.mapHKL==True:
                            self.ubMatrix[scan] = self.getUBMatrix(curScan)
                            if self.ubMatrix[scan] == None:
                                raise Sector33SpecFileException("UB matrix " + \
                                                                "not found.")
                        else:
                            self.ubMatrix[scan] = None
                        self.incidentEnergy[scan] = 12398.4 /float(curScan.G['G4'].split()[3])
                        _start_time = time.time()
                        self.imageBounds[scan] = \
                            self.findImageQs(angles, \
                                             self.ubMatrix[scan], \
                                             self.incidentEnergy[scan])
                        if self.progressUpdater <> None:
                            self.progressUpdater(self.progress, self.progressMax)
                        print (('Elapsed time for Finding qs for scan %d: ' +
                               '%.3f seconds') % \
                               (scan, (time.time() - _start_time)))
                        #Make sure to show 100% completion
                    except ScanDataMissingException:
                        print scan
            if self.progressUpdater <> None:
                self.progressUpdater(self.progressMax, self.progressMax)
        except IOError:
            raise IOError( "Cannot open file " + str(self.specFile))
#         if len(self.getAvailableScans()) == 0:
#             raise ScanDataMissingException("Could not find scan data for " + \
#                                            "input file \n" + self.specFile + \
#                                            "\nOne possible reason for this " + \
#                                            "is that the image files are " + \
#                                            "missing.  Images are assumed " + \
#                                            "to be in " + \
#                                            os.path.join(self.projectDir, 
#                                         IMAGE_DIR_MERGE_STR % self.projectName))

    
        self.availableScanTypes = set(self.scanType.values())
        
    def rawmap(self):
        pass
