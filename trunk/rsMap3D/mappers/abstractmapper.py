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

# region of interest on the detector
default_roi = [0,487,0,195] 

class AbstractGridMapper(object):
    __metaclass__ = abc.ABCMeta
    '''
    classdocs
    '''


    def __init__(self, dataSource, nx=200, ny=201, nz=202, transform = None):
        '''
        Constructor
        '''
        self.dataSource = dataSource
        self.nx = nx
        self.ny = ny
        self.nz = nz
        if transform == None:
            self.transform = UnityTransform3D()
        else:
            self.transform = transform

    def doMap(self):
        '''
        Produce a q map of the data.
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
        INT = xu.maplog(gint, 5.0, 0)
        
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
        writer.SetFileName("%s_S%d.vti" % (self.dataSource.projectName, \
                                           self.dataSource.availableScans[0]))
        writer.SetInput(image_data)
        writer.Write()

    def setGridSize(self, nx, ny, nz):
        self.nx = nx
        self.ny = ny
        self.nz = nz
        
    def hotpixelkill(self, ad_data):
        """
        function to remove hot pixels from CCD frames
        ADD REMOVE VALUES IF NEEDED!
        """
        
        #ad_data[44,159] = 0
        
        return ad_data

    @abc.abstractmethod
    def processMap(self,**kwargs):
        print("Running abstract Method")
        
    def rawmap(self,scans, roi=default_roi,angdelta=[0,0,0,0,0],
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
                Nav=self.dataSource.getNumPixelsToAverage(), roi=roi) 
        else:
            hxrd.Ang2Q.init_area(self.dataSource.getDetectorPixelDirection1(), \
                self.dataSource.getDetectorPixelDirection2(), \
                cch1=self.dataSource.getDetectorCenterChannel()[0], \
                cch2=self.dataSource.getDetectorCenterChannel()[1], \
                Nch1=self.dataSource.getDetectorDimensions()[0], \
                Nch2=self.dataSource.getDetectorDimensions()[0], \
                chpdeg1=self.dataSource.getDetectorChannelsPerDegree()[0], \
                chpdeg2=self.dataSource.getDetectorChannelsPerDegree()[1], \
                Nav=self.dataSource.getNumPixelsToAverage(), roi=roi) 
            
        scanAngle = {}
        for i in xrange(len(self.dataSource.sd[self.dataSource.getAvailableScans()[0]].geo_angle_names)):
            scanAngle[i] = np.array([])
    
        offset = 0
        imageToBeUsed = self.dataSource.getImageToBeUsed()
        for scannr in scans:
            scan = self.dataSource.sd[scannr]
            scan.geo_angle_names = self.dataSource.getSampleAngleNames() + \
                                   self.dataSource.getDetectorAngleNames()
            angles = scan.get_geo_angles()
            scanAngle1 = {}
            scanAngle2 = {}
            for i in xrange(len(scan.geo_angle_names)):
                scanAngle1[i] = angles[:,i]
                scanAngle2[i] = []
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
                                            roi=roi)
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
                    for i in xrange(len(scan.geo_angle_names)):
                        scanAngle2[i].append(scanAngle1[i][ind])
                    foundIndex += 1
            if len(scanAngle2[0]) > 0:
                for i in xrange(len(scan.geo_angle_names)):
                    scanAngle[i] = \
                        np.concatenate((scanAngle[i], np.array(scanAngle2[i])), \
                                          axis=0)
        # transform scan angles to reciprocal space coordinates for all detector pixels
        angleList = []
        for i in xrange(len(scan.geo_angle_names)):
            angleList.append(scanAngle[i])
        angleTuple = tuple(angleList)
        qx, qy, qz = hxrd.Ang2Q.area(angleTuple[0], \
                                     angleTuple[1], \
                                     angleTuple[2], \
                                     angleTuple[3],  \
                                     roi=roi, 
                                     Nav=self.dataSource.getNumPixelsToAverage())

        # apply selected transform
        qxTrans, qyTrans, qzTrans = \
            self.transform.do3DTransform(qx, qy, qz)

    
        return qxTrans, qyTrans, qzTrans, intensity

    def setTransform(self, transform):
        ''' '''
        self.transform = transform
        