'''
 Copyright (c) 2014, UChicago Argonne, LLC
 See LICENSE file.
'''
import abc
import time
import numpy as np

import vtk
from vtk.util import numpy_support
from rsMap3D.transforms.unitytransform3d import UnityTransform3D
from rsMap3D.exception.rsmap3dexception import RSMap3DException

VTI_OUTFILE_MERGE_STR = "%s_S%d.vti"

class AbstractGridMapper(object):
    __metaclass__ = abc.ABCMeta
    '''
    This class is an abstract class around which to build a reciprocal space 
    mapping class using the xrayutilities module.  It requires an input of the 
    type AbstractXrayUtilitiesDataSource provided in the rsMap3D.datasource 
    package. 
    '''


    def __init__(self, dataSource, \
                 outputFileName, \
                 nx=200, ny=201, nz=202, transform = None):
        '''
        Constructor
        :param dataSource: source of scan data
        :param outputFileName: filename for output
        :param nx: number of points in x direction for griidder
        :param ny: number of points in y direction for griidder
        :param nz: number of points in z direction for griidder
        :param transform: Transform to be applied to the axes before gridding
        '''
        self.dataSource = dataSource
        self.outputFileName = outputFileName
        self.nx = nx
        self.ny = ny
        self.nz = nz
        self.haltMap = False
        self.progressUpdater = None
        if transform == None:
            self.transform = UnityTransform3D()
        else:
            self.transform = transform

    def doMap(self):
        '''
        Produce a q map of the data.  This is the method typically called to 
        run the mapper.  This method calls the processMap method which is an 
        abstract method which needs to be defined in subclasses.
        '''
        
        # read and grid data with helper function
        _start_time = time.time()
        #rangeBounds = self.dataSource.getRangeBounds()
        qx, qy, qz, gint, gridder = \
            self.processMap()
        print 'Elapsed time for gridding: %.3f seconds' % \
               (time.time() - _start_time)
        
        # print some information
        print 'qx: ', qx.min(), ' .... ', qx.max()
        print 'qy: ', qy.min(), ' .... ', qy.max()
        print 'qz: ', qz.min(), ' .... ', qz.max()
        
        # prepare data for export to VTK image file
        #INT = xu.maplog(gint, 5.0, 0)
        INT = gint
        qx0 = qx.min()
        dqx  = (qx.max()-qx.min())/self.nx
        
        qy0 = qy.min()
        dqy  = (qy.max()-qy.min())/self.ny
        
        qz0 = qz.min()
        dqz = (qz.max()-qz.min())/self.nz
        
        INT = np.transpose(INT).reshape((INT.size))
        data_array = numpy_support.numpy_to_vtk(INT)
        
        image_data = vtk.vtkImageData()
        image_data.SetOrigin(qx0,qy0,qz0)
        image_data.SetSpacing(dqx,dqy,dqz)
        image_data.SetExtent(0, self.nx-1,0, self.ny-1,0, self.nz-1)
        if vtk.VTK_MAJOR_VERSION <= 5:
            image_data.SetNumberOfScalarComponents(1)
            image_data.SetScalarTypeToDouble()
        else:
            image_data.AllocateScalars(vtk.VTK_DOUBLE, 1)
               
        pd = image_data.GetPointData()
        
        pd.SetScalars(data_array)

        # export data to file
        writer= vtk.vtkXMLImageDataWriter()
        if self.outputFileName == "":
            writer.SetFileName(VTI_OUTFILE_MERGE_STR % (self.dataSource.projectName, \
                                        self.dataSource.availableScans[0]))
        else:
            writer.SetFileName(self.outputFileName)
            
        if vtk.VTK_MAJOR_VERSION <= 5:
            writer.SetInput(image_data)
        else:
            writer.SetInputData(image_data)
            
        writer.Write()

    @abc.abstractmethod
    def processMap(self, **kwargs):
        """
        Abstract method for processing data.  This method is called by the
        method doMap.  Typical access to this method is through the doMap
        method.
        """
        print("Running abstract Method")
        
    def setGridSize(self, nx, ny, nz):
        """
        Set the grid size to be used for outputting data.
        :param nx: number of points in x direction for griidder
        :param ny: number of points in y direction for griidder
        :param nz: number of points in z direction for griidder
        """
        self.nx = nx
        self.ny = ny
        self.nz = nz
        
    def setProgressUpdater(self, updater):
        '''
        Set the updater that will be used to maintain the progress bar value 
        '''
        self.progressUpdater = updater

    def setTransform(self, transform):
        '''
        Set a transform which will define a mapping of q space to some other 
        system.  The transform set here should be a subclass of 
        AbstractTransform3D which is defined in 
        rsMap3D.transform.abstracttransform3D.
        :param tranfoem:
        '''
        self.transform = transform
        
    def stopMap(self):
        '''
        Set a flag that will be used to halt processing the scan using 
        '''
        self.haltMap = True
        self.dataSource.stopMap() 
        
class ProcessCanceledException(RSMap3DException):
    '''
    Exception Thrown when loading data is canceled.
    '''
    def __init__(self, message):
        '''
        Constructor
        :param message:  Message to be carried conveyed with exception
        '''
        super(ProcessCanceledException, self).__init__(message)
