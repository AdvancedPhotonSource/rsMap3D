'''
 Copyright (c) 2016, UChicago Argonne, LLC
 See LICENSE file.
'''
from rsMap3D.mappers.abstractmapper import AbstractGridMapper

class XPCSGridLocationMapper(AbstractGridMapper):
    '''
    This map provides and then writes the grid location for 
    specified scan
    '''
    
    def doMap(self):
        print("Entering XpcsGridLocationMapper.doMap")
        scan = self.dataSource.getAvailableScans()[0]
        qx, qy, qz = self.dataSource.rawmapSingle(scan)
        
        self.gridWriter.setData(qx, qy, qz, None)
        self.gridWriter.setFileInfo((self.dataSource.projectName, 
                                        self.dataSource.availableScans[0],
                                        self.nx, self.ny, self.nz,
                                        self.outputFileName))
        self.gridWriter.write()
        print("Leaving XpcsGridLocationMapper.doMap")
        
        
    def processMap(self, **kwargs):
        '''
        '''
        pass