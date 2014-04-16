'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''
import abc
import time
import numpy as np
import xrayutilities as xu
import Image

import vtk
from vtk.util import numpy_support
from rsMap3D.transforms.unitytransform3d import UnityTransform3D

class AbstractGridMapper(object):
    __metaclass__ = abc.ABCMeta
    '''
    This class is an abstract class around which to build a reciprical space 
    mapping class using the xrayutilities module.  It requires an input of the 
    type AbstractXrayUtilitiesDataSource provided in the rsMap3D.datasource 
    package. 
    '''


    def __init__(self, dataSource, \
                 outputFileName, \
                 nx=200, ny=201, nz=202, transform = None):
        '''
        Constructor
        '''
        self.dataSource = dataSource
        self.outputFileName = outputFileName
        self.nx = nx
        self.ny = ny
        self.nz = nz
        if transform == None:
            self.transform = UnityTransform3D()
        else:
            self.transform = transform

    def doMap(self):
        '''
        Produce a q map of the data.  This is the method typically called to 
        run the mapper.  This method calls the processMap method which is an 
        abstact method which needs to be defined in subclasses.
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
        image_data.SetNumberOfScalarComponents(1)
        image_data.SetOrigin(qx0,qy0,qz0)
        image_data.SetSpacing(dqx,dqy,dqz)
        image_data.SetExtent(0, self.nx-1,0, self.ny-1,0, self.nz-1)
        image_data.SetScalarTypeToDouble()
        
        pd = image_data.GetPointData()
        
        pd.SetScalars(data_array)

        # export data to file
        writer= vtk.vtkXMLImageDataWriter()
        if self.outputFileName == "":
            writer.SetFileName("%s_S%d.vti" % (self.dataSource.projectName, \
                                        self.dataSource.availableScans[0]))
        else:
            writer.SetFileName(self.outputFileName)
            
        writer.SetInput(image_data)
        writer.Write()

    def setGridSize(self, nx, ny, nz):
        """
        Set the grid size to be used for outputting data.
        """
        self.nx = nx
        self.ny = ny
        self.nz = nz
        
    def hotpixelkill(self, ad_data):
        """
        function to remove hot pixels from CCD frames
        ADD REMOVE VALUES IF NEEDED!
        """
        
        for pixel in self.dataSource.getBadPixels():
            ad_data[pixel[0],pixel[1]] = 0
        
        return ad_data

    @abc.abstractmethod
    def processMap(self,**kwargs):
        """
        Abstract method for processing data.  This method is called by the
        method doMap.  Typical access to this method is through the doMap
        method.
        """
        print("Running abstract Method")
        
    def rawmap(self,scans, angdelta=[0,0,0,0,0],
            adframes=None):
        """
        read ad frames and and convert them in reciprocal space
        angular coordinates are taken from the spec file
        or read from the edf file header when no scan number is given (scannr=None)
        """
        
        #sd = spec.SpecDataFile(self.dataSource.specFile)
        intensity = np.array([])
        
        # fourc goniometer in fourc coordinates
        # convention for coordinate system:
        # x: upwards;
        # y: along the incident beam;
        # z: "outboard" (makes coordinate system right-handed).
        # QConversion will set up the goniometer geometry.
        # So the first argument describes the sample rotations, the second the
        # detector rotations and the third the primary beam direction.
        qconv = xu.experiment.QConversion(self.dataSource.getSampleCircleDirections(), \
                                    self.dataSource.getDetectorCircleDirections(), \
                                    self.dataSource.getPrimaryBeamDirection())
    
        # define experimental class for angle conversion
        #
        # ipdir: inplane reference direction (ipdir points into the primary beam
        #        direction at zero angles)
        # ndir:  surface normal of your sample (ndir points in a direction
        #        perpendicular to the primary beam and the innermost detector
        #        rotation axis)
        en = self.dataSource.getIncidentEnergy()
        hxrd = xu.HXRD(self.dataSource.getInplaneReferenceDirection(), \
                       self.dataSource.getSampleSurfaceNormalDirection(), \
                       en=en[self.dataSource.getAvailableScans()[0]], \
                       qconv=qconv)

        
        # initialize area detector properties
        if (self.dataSource.getDetectorPixelWidth() != None ) and \
            (self.dataSource.getDistanceToDetector() != None):
            hxrd.Ang2Q.init_area(self.dataSource.getDetectorPixelDirection1(), \
                self.dataSource.getDetectorPixelDirection2(), \
                cch1=self.dataSource.getDetectorCenterChannel()[0], \
                cch2=self.dataSource.getDetectorCenterChannel()[1], \
                Nch1=self.dataSource.getDetectorDimensions()[0], \
                Nch2=self.dataSource.getDetectorDimensions()[0], \
                pwidth1=self.dataSource.getDetectorPixelWidth()[0], \
                pwidth2=self.dataSource.getDetectorPixelWidth()[1], \
                distance=self.dataSource.getDistanceToDetector(), \
                Nav=self.dataSource.getNumPixelsToAverage(), \
                roi=self.dataSource.getDetectorROI()) 
        else:
            hxrd.Ang2Q.init_area(self.dataSource.getDetectorPixelDirection1(), \
                self.dataSource.getDetectorPixelDirection2(), \
                cch1=self.dataSource.getDetectorCenterChannel()[0], \
                cch2=self.dataSource.getDetectorCenterChannel()[1], \
                Nch1=self.dataSource.getDetectorDimensions()[0], \
                Nch2=self.dataSource.getDetectorDimensions()[0], \
                chpdeg1=self.dataSource.getDetectorChannelsPerDegree()[0], \
                chpdeg2=self.dataSource.getDetectorChannelsPerDegree()[1], \
                Nav=self.dataSource.getNumPixelsToAverage(), 
                roi=self.dataSource.getDetectorROI()) 
            
        angleNames = self.dataSource.getAngles()
        scanAngle = {}
        for i in xrange(len(angleNames)):
            scanAngle[i] = np.array([])
    
        offset = 0
        imageToBeUsed = self.dataSource.getImageToBeUsed()
        monitorName = self.dataSource.getMonitorName()
        monitorScaleFactor = self.dataSource.getMonitorScaleFactor()
        filterName = self.dataSource.getFilterName()
        filterScaleFactor = self.dataSource.getFilterScaleFactor()
        for scannr in scans:
            scan = self.dataSource.sd[scannr]
            angles = self.dataSource.getGeoAngles(scan, angleNames)
            scanAngle1 = {}
            scanAngle2 = {}
            for i in xrange(len(angleNames)):
                scanAngle1[i] = angles[:,i]
                scanAngle2[i] = []
            if monitorName != None:
                monitor_data = scan.scandata.get(monitorName)
                if monitor_data == None:
                    raise IOError("Did not find Monitor source '" + \
                                  monitorName + \
                                  "' in the Spec file.  Make sure " + \
                                  "monitorName is correct in the " + \
                                  "instrument Config file")
            if filterName != None:
                filter_data = scan.scandata.get(filterName)
                if filter_data == None:
                    raise IOError("Did not find filter source '" + \
                                  filterName + \
                                  "' in the Spec file.  Make sure " + \
                                  "filterName is correct in the " + \
                                  "instrument Config file")
            # read in the image data
            arrayInitializedForScan = False
            foundIndex = 0
            
            for ind in xrange(scan.data.shape[0]):
                if imageToBeUsed[scannr][ind]:    
                    # read tif image
                    img = np.array(Image.open(self.dataSource.imageFileTmp % 
                                                 (scannr, scannr, ind))).T
                    img = self.hotpixelkill(img)
        
                    # reduce data size
                    img2 = xu.blockAverage2D(img, 
                                            self.dataSource.getNumPixelsToAverage()[0], \
                                            self.dataSource.getNumPixelsToAverage()[1], \
                                            roi=self.dataSource.getDetectorROI())

                    # apply intensity corrections
                    if monitorName != None:
                        img2 = img2 / monitor_data[ind] * monitorScaleFactor
                    if filterName != None:
                        img2 = img2 / filter_data[ind] * filterScaleFactor

                    # initialize data array
                    if not arrayInitializedForScan:
                        if not intensity.shape[0]:
                            intensity = np.zeros((np.count_nonzero(imageToBeUsed[scannr]),) + img2.shape)
                            arrayInitializedForScan = True
                        else: 
                            offset = intensity.shape[0]
                            intensity = np.concatenate(
                                (intensity,
                                (np.zeros((np.count_nonzero(imageToBeUsed[scannr]),) + img2.shape))),
                                axis=0)
                            arrayInitializedForScan = True
                    # add data to intensity array
                    intensity[foundIndex+offset,:,:] = img2
                    for i in xrange(len(angleNames)):
                        scanAngle2[i].append(scanAngle1[i][ind])
                    foundIndex += 1
            if len(scanAngle2[0]) > 0:
                for i in xrange(len(angleNames)):
                    scanAngle[i] = \
                        np.concatenate((scanAngle[i], np.array(scanAngle2[i])), \
                                          axis=0)
        # transform scan angles to reciprocal space coordinates for all detector pixels
        angleList = []
        for i in xrange(len(angleNames)):
            angleList.append(scanAngle[i])
        angleTuple = tuple(angleList)
        if self.dataSource.getUBMatrix(scans[0]) == None:
            qx, qy, qz = hxrd.Ang2Q.area(angleTuple[0], \
                            angleTuple[1], \
                            angleTuple[2], \
                            angleTuple[3],  \
                            roi=self.dataSource.getDetectorROI(), 
                            Nav=self.dataSource.getNumPixelsToAverage())
        else:
            qx, qy, qz = hxrd.Ang2Q.area(angleTuple[0], \
                            angleTuple[1], \
                            angleTuple[2], \
                            angleTuple[3],  \
                            roi=self.dataSource.getDetectorROI(), 
                            Nav=self.dataSource.getNumPixelsToAverage(), \
                            UB = self.dataSource.getUBMatrix(scans[0]))
            

        # apply selected transform
        qxTrans, qyTrans, qzTrans = \
            self.transform.do3DTransform(qx, qy, qz)

    
        return qxTrans, qyTrans, qzTrans, intensity

    def setTransform(self, transform):
        '''
        Set a transform which will define a mapping of q space to some other 
        system.  The transform set here should be a subclass of 
        AbstractTransform3D which is defined in 
        rsMap3D.transform.abstracttransform3D.
        '''
        self.transform = transform
        