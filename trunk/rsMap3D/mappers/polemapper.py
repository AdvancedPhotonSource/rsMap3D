'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''
import numpy as np

import xrayutilities as xu
from rsMap3D.mappers.abstractmapper import AbstractGridMapper

class PoleFigureMapper(AbstractGridMapper):
    '''
    '''
    
    def processMap(self, **kwargs):
        """
        read ad frames and grid them in reciprocal space
        angular coordinates are taken from the spec file
    
        **kwargs are passed to the rawmap function
        """
    
        gridder = xu.Gridder3D(self.nx, self.ny ,self.nz)
        gridder.KeepData(True)
        rangeBounds = self.dataSource.getRangeBounds()
        qxmin = rangeBounds[0]
        qxmax = rangeBounds[1]
        qymin = rangeBounds[2]
        qymax = rangeBounds[3]
        qzmin = rangeBounds[4]
        qzmax = rangeBounds[5]
        
        maxqxsq = max(qxmin**2, qxmax**2)
        minqxsq = min(qxmin**2, qxmax**2)
        maxqysq = max(qymin**2, qymax**2)
        minqysq = min(qymin**2, qymax**2)
        maxqzsq = max(qzmin**2, qzmax**2)
        minqzsq = min(qzmin**2, qzmax**2)
        
        minspq = 4
        maxspq = 6
        minspx = -1.0
        maxspx = 1.0
        minspy = -1.0
        maxspy = 1.0
    
        print "qx range: " + str(qxmin) + ", " + str(qxmax)
        print "qy range: " + str(qymin) + ", " + str(qymax)
        print "qz range: " + str(qzmin) + ", " + str(qzmax)
        print "spx range: " + str(minspx) + ", " + str(maxspx)
        print "spy range: " + str(minspy) + ", " + str(maxspy)
        print "spq range: " + str(minspq) + ", " + str(maxspq)
        gridder.dataRange((minspx, maxspx), (minspy, maxspy), (minspq, maxspq), True)
        
        imageToBeUsed = self.dataSource.getImageToBeUsed()
        for scan in self.dataSource.getAvailableScans():
            #print '---' + str(scan) + str(imageToBeUsed[scan])
            if True in imageToBeUsed[scan]:
                qx, qy, qz, intensity = self.rawmap((scan, ), **kwargs)
                
                # convert qx,qy,qz to stereographic projection
                spq = np.sqrt(qx**2 + qy**2 + qz**2)
                spx = qx / (spq + qz)
                spy = qy / (spq + qz)
                
            
                # convert data to rectangular grid in reciprocal space
                gridder(spx,spy,spq,intensity)
    
        return gridder.xaxis,gridder.yaxis,gridder.zaxis,gridder.gdata,gridder
