'''
 Copyright (c) 2017 UChicago Argonne, LLC
 See LICENSE file.
'''
from rsMap3D.datasource.abstractDataSource import AbstractDataSource


class S1HighEnergyDiffractionDS(AbstractDataSource):
    '''
    '''
    
    def __init__(self, 
                 projectDir,
                 projectName,
                 projectExtension,
                 detConfigFile,
                 detectorId="GE",
                 **kwargs):
        super(S1HighEnergyDiffractionDS, self).__init__()
        self.projectDir = str(projectDir)
        self.projectName = str(projectName)
        self.projectExtension = str(projectExtension)
        self.detConfigFile = str(detConfigFile)
        self.detectorId = detectorId
        self.files = None
        self.availableFiles = []
        self.detectorROI = []
        self.incidentEnergy = {}
        self.progressUpdater = None
        self.progress = 0
        self.progressInc = 1.0 *100.0
        self.progressMax = 1
        self.cancelLoad = False

    def findImageQs(self):
        pass
        
    def loadSource(self):
        pass

    def rawmap(self, scans, angledelta=[0,0,0,0],
               adframes=None, mask=None ):
        
        pass