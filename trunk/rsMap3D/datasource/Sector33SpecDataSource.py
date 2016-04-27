'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''
import os
from spec2nexus.spec import SpecDataFile
from rsMap3D.exception.rsmap3dexception import RSMap3DException,\
    InstConfigException, DetectorConfigException, ScanDataMissingException
from rsMap3D.gui.rsm3dcommonstrings import CANCEL_STR
from rsMap3D.config.rsmap3dconfig import RSMap3DConfig
from rsMap3D.datasource.pilatusbadpixelfile import PilatusBadPixelFile
from rsMap3D.mappers.abstractmapper import ProcessCanceledException
from rsMap3D.datasource.AbstractXrayUtilitiesDataSource \
    import AbstractXrayutilitiesDataSource
import rsMap3D.datasource.InstForXrayutilitiesReader as InstReader
import rsMap3D.datasource.DetectorGeometryForXrayutilitiesReader \
    as DetectorReader
import numpy as np
import xrayutilities as xu
import time
import sys,traceback
try:
    from PIL import Image
except ImportError:
    import Image



IMAGE_DIR_MERGE_STR = "images/%s"
SCAN_NUMBER_MERGE_STR = "S%03d"
TIFF_FILE_MERGE_STR = "S%%03d/%s_S%%03d_%%05d.tif"

class Sector33SpecDataSource(AbstractXrayutilitiesDataSource):
    '''
    Class to load data from spec file and configuration xml files from 
    for the way that data is collected at sector 33.
    :members
    '''


    def __init__(self, 
                 projectDir, 
                 projectName, 
                 projectExtension,
                 instConfigFile, 
                 detConfigFile, 
                 **kwargs):
        '''
        Constructor
        :param projectDir: Directory holding the project file to open
        :param projectName: First part of file name for the project
        :param projectExt: File extension for the project file.
        :param instConfigFile: Full path to Instrument configuration file.
        :param detConfigFile: Full path to the detector configuration file
        :param kwargs: Assorted keyword arguments

        :rtype: Sector33SpecDataSource
        '''
        super(Sector33SpecDataSource, self).__init__(**kwargs)
        self.projectDir = str(projectDir)
        self.projectName = str(projectName)
        self.projectExt = str(projectExtension)
        self.instConfigFile = str(instConfigFile)
        self.detConfigFile = str(detConfigFile)
        self.progress = 0
        self.progressInc = 1
        self.progressMax = 1
        self.haltMap = False
        try:
            self.scans = kwargs['scanList']
        except KeyError:
            self.scans = None
        
    def _calc_eulerian_from_kappa(self, primaryAngles=None, \
                                  referenceAngles = None):
        """
        Calculate the eulerian sample angles from the kappa stage angles.
        :param primaryAngles:  list of sample axis numbers to be handled by 
        the conversion
        :param referenceAngles: list of reference angles to be used in angle 
        conversion
        """

        keta = np.deg2rad(referenceAngles[:,0])
        kappa = np.deg2rad(referenceAngles[:,1])
        kphi = np.deg2rad(referenceAngles[:,2])
        kappaParam = self.instConfig.getSampleAngleMappingParameter('kappa')
        
        try:
            if kappaParam != None:
                self.kalpha = np.deg2rad(float(kappaParam))
            else:
                self.kalpha = np.deg2rad(50.000)
            kappaInvertedParam = \
                self.instConfig.getSampleAngleMappingParameter('kappaInverted')
            if kappaInvertedParam != None:
                self.kappa_inverted = self.to_bool(kappaInvertedParam)
            else:
                self.kappa_inverted = False
        except Exception as ex:
            raise RSMap3DConfig("Error trying to get parameter for " + \
                                "sampleAngleMappingFunction " + \
                                "_calc_eulerian_from_kappa in inst config " + \
                                "file\n" + \
                                str(ex))
        
        _t1 = np.arctan(np.tan(kappa / 2.0) * np.cos(self.kalpha))
        if self.kappa_inverted:
            eta = np.rad2deg(keta + _t1)
            phi = np.rad2deg(kphi + _t1)
        else:
            eta = np.rad2deg(keta - _t1)
            phi = np.rad2deg(kphi - _t1)
        chi = 2.0 * np.rad2deg(np.arcsin(np.sin(kappa / 2.0) * \
                               np.sin(self.kalpha)))
        
        return eta, chi, phi

    def findImageQs(self, angles, ub, en):
        '''
        Find the minimum/maximum q boundaries associated with each scan given 
        the angles, energy and UB matrix.
        :param angles: A list of angles used for Q calculations
        :param ub: sample UB matrix
        :param en: Incident Endergy
        '''
        qconv = xu.experiment.QConversion(self.getSampleCircleDirections(), 
                                          self.getDetectorCircleDirections(), 
                                          self.getPrimaryBeamDirection())
        hxrd = xu.HXRD(self.getInplaneReferenceDirection(), 
                       self.getSampleSurfaceNormalDirection(), 
                       en=en, 
                       qconv=qconv)

        cch = self.getDetectorCenterChannel() 
        nav = self.getNumPixelsToAverage()
        roi = self.getDetectorROI()
        detDims = self.getDetectorDimensions()
        hxrd.Ang2Q.init_area(self.getDetectorPixelDirection1(), 
                             self.getDetectorPixelDirection2(), 
                             cch1=cch[0], 
                             cch2=cch[1], 
                             Nch1=detDims[0], 
                             Nch2=detDims[1], 
                             pwidth1=self.detectorPixelWidth[0], 
                             pwidth2=self.detectorPixelWidth[1], 
                             distance = self.distanceToDetector,
                             Nav=self.getNumPixelsToAverage(), 
                             roi=self.getDetectorROI())

        rsMap3DConfig = RSMap3DConfig()
        maxImageMem = rsMap3DConfig.getMaxImageMemory()
        imageSize = self.getDetectorDimensions()[0] * \
                    self.getDetectorDimensions()[1]
        numImages = len(angles)
        if imageSize*4*numImages <= maxImageMem:
            self.progressMax = len( self.scans) * 100
            self.progressInc = 1.0 * 100.0
            if self.progressUpdater <> None:
                self.progressUpdater(self.progress, self.progressMax)
            self.progress += self.progressInc        
            angleList = []
            for i in range(len(angles[0])):
                angleList.append(angles[:,i])
            if ub == None:
                qx, qy, qz = hxrd.Ang2Q.area(*angleList, \
                                         roi=roi, \
                                         Nav=nav)
            else:
                qx, qy, qz = hxrd.Ang2Q.area(*angleList, \
                                         roi=roi, \
                                         Nav=nav, \
                                         UB = ub)
                
            qxTrans, qyTrans, qzTrans = self.transform.do3DTransform(qx, qy, qz)
            
            idx = range(len(qxTrans))
            xmin = [np.min(qxTrans[i]) for i in idx] 
            xmax = [np.max(qxTrans[i]) for i in idx] 
            ymin = [np.min(qyTrans[i]) for i in idx] 
            ymax = [np.max(qyTrans[i]) for i in idx] 
            zmin = [np.min(qzTrans[i]) for i in idx] 
            zmax = [np.max(qzTrans[i]) for i in idx] 
        else:
            nPasses = imageSize*4*numImages/ maxImageMem + 1
            xmin = []
            xmax = []
            ymin = []
            ymax = []
            zmin = []
            zmax = []
            for thisPass in range(nPasses):
                self.progressMax = len( self.scans) * 100.0
                self.progressInc = 1.0 / nPasses * 100.0
                if self.progressUpdater <> None:
                    self.progressUpdater(self.progress, self.progressMax)
                self.progress += self.progressInc        
                firstImageInPass = thisPass*numImages/nPasses
                lastImageInPass = (thisPass+1)*numImages/nPasses
                angleList = []
                for i in range(len(angles[0])):
                    angleList.append(angles[firstImageInPass:lastImageInPass,i])
                if ub == None:
                    qx, qy, qz = hxrd.Ang2Q.area(*angleList, \
                                             roi=roi, \
                                             Nav=nav)
                else:
                    qx, qy, qz = hxrd.Ang2Q.area(*angleList, \
                                             roi=roi, \
                                             Nav=nav, \
                                             UB = ub)
                    
                qxTrans, qyTrans, qzTrans = self.transform.do3DTransform(qx, qy, qz)
                
                idx = range(len(qxTrans))
                [xmin.append(np.min(qxTrans[i])) for i in idx] 
                [xmax.append(np.max(qxTrans[i])) for i in idx] 
                [ymin.append(np.min(qyTrans[i])) for i in idx] 
                [ymax.append(np.max(qyTrans[i])) for i in idx] 
                [zmin.append(np.min(qzTrans[i])) for i in idx] 
                [zmax.append(np.max(qzTrans[i])) for i in idx] 
                
            
        return (xmin, xmax, ymin, ymax, zmin, zmax)

    def fixGeoAngles(self, scan, angles):
        '''
        Fix the angles using a user selected function.
        :param scan: scan to set the angles for
        :param angles: Array of angles to set for this scan  
        '''

        needToCorrect = False
        refAngleNames = self.instConfig.getSampleAngleMappingReferenceAngles()
        for refAngleName in refAngleNames:
            if refAngleName in scan.cols:
                needToCorrect = True
                
        if needToCorrect:
            refAngles = self.getScanAngles(scan, refAngleNames)
            primaryAngles = self.instConfig.getSampleAngleMappingPrimaryAngles()
            functionName = self.instConfig.getSampleAngleMappingFunctionName()
            #Call a defined method to calculate angles from the reference angles.
            method = getattr(self, functionName)
            fixedAngles = method(primaryAngles=primaryAngles, 
                                   referenceAngles=refAngles)
            for i in range(len(primaryAngles)):
                angles[:,primaryAngles[i]-1] = fixedAngles[i]
        
    def getGeoAngles(self, scan, angleNames):
        """
        This function returns all of the geometry angles for the
        for the scan as a N-by-num_geo array, where N is the number of scan
        points and num_geo is the number of geometry motors.
        """
#        scan = self.sd[scanNo]
        geoAngles = self.getScanAngles(scan, angleNames)
        if not (self.instConfig.getSampleAngleMappingFunctionName() == ""):
            tb = None
            try:
                self.fixGeoAngles(scan, geoAngles)
            except Exception as ex:
                tb = traceback.format_exc()
                raise RSMap3DException("Handling exception in getGeoAngles." + \
                                       "\n" + \
                                       str(ex) + \
                                       "\n" + \
                                       str(tb))
        return geoAngles
    
    def getReferenceNames(self):
        '''
        '''
        names = []
        names.extend(self.getSampleAngleNames())
        names.extend(self.getDetectorAngleNames())
        return names
    
    def getReferenceValues(self, scan):
        '''
        '''
        angles = self.getGeoAngles(self.sd.scans[str(scan)], self.getReferenceNames())
        return angles

    def getScanAngles(self, scan, angleNames):
        """
        This function returns all of the geometry angles for the
        for the scan as a N-by-num_geo array, where N is the number of scan
        points and num_geo is the number of geometry motors.
        :param scan: scan from which to retrieve the angles
        :params angleNames: a list of names for the angles to be returned
        """
        geoAngles = np.zeros((len(scan.data[scan.data.keys()[0]]), len(angleNames)))
        for i, name in enumerate(angleNames):
            v = scan.data.get(name)
            p = scan.positioner.get(name)

            if v != None:
                if len(v) == 1:
                    v = np.ones(len(scan.data[scan.data.keys()[0]])) * v
            elif p != None:
                v = np.ones(len(scan.data[scan.data.keys()[0]])) * p
            else:
                raise InstConfigException("Could not find angle " + name + \
                                          " in scan parameters")
            geoAngles[:,i] = v
        
        return geoAngles
        
    def getUBMatrix(self, scan):
        """
        Read UB matrix from the #G3 line from the spec file. 
        """
        try:
            g3 = scan.G["G3"].strip().split()
            g3 = np.array(map(float, g3))
            ub = g3.reshape(-1,3)
            print ub
            return ub
        except:
            print("Unable to read UB Matrix from G3")
            print '-'*60
            traceback.print_exc(file=sys.stdout)
            print '-'*60
            
            
    def hotpixelkill(self, areaData):
        """
        function to remove hot pixels from CCD frames
        ADD REMOVE VALUES IF NEEDED!
        :param areaData: area detector data
        """
        
        for pixel in self.getBadPixels():
            badLoc = pixel.getBadLocation()
            replaceLoc = pixel.getReplacementLocation()
            areaData[badLoc[0],badLoc[1]] = \
                areaData[replaceLoc[0],replaceLoc[1]]
        
        return areaData

    def loadSource(self, mapHKL=False):
        '''
        This method does the work of loading data from the files.  This has been
        split off from the constructor to allow this to be threaded and later 
        canceled.
        :param mapHKL: boolean to mark if the data should be mapped to HKL
        '''
        # Load up the instrument configuration file
        try:
            self.instConfig = \
                InstReader.InstForXrayutilitiesReader(self.instConfigFile)
            self.sampleCirclesDirections = \
                self.instConfig.getSampleCircleDirections()
            self.detectorCircleDirections = \
                self.instConfig.getDetectorCircleDirections()
            self.primaryBeamDirection = \
                self.instConfig.getPrimaryBeamDirection()
            self.sampleInplaneReferenceDirection = \
                self.instConfig.getInplaneReferenceDirection()
            self.sampleSurfaceNormalDirection = \
                self.instConfig.getSampleSurfaceNormalDirection()
            self.sampleAngleNames = self.instConfig.getSampleCircleNames()
            self.detectorAngleNames = self.instConfig.getDetectorCircleNames()
            self.monitorName = self.instConfig.getMonitorName()
            self.monitorScaleFactor = self.instConfig.getMonitorScaleFactor()
            self.filterName = self.instConfig.getFilterName()
            self.filterScaleFactor = self.instConfig.getFilterScaleFactor()
            self.angleNames = self.instConfig.getSampleCircleNames() + \
                self.instConfig.getDetectorCircleNames()
            self.projectionDirection = self.instConfig.getProjectionDirection()
        except InstConfigException as ex:
            raise ex
        except RSMap3DException as ex:
            print ("---Error Reading instrument config")
            raise ex
        except Exception as ex:
            print "Unhandle Exception loading instrument config" + str(ex)
            raise ex
        #Load up the detector configuration file
        try:
            detConfig = \
                DetectorReader.DetectorGeometryForXrayutilitiesReader(
                                                      self.detConfigFile)
            detector = detConfig.getDetectorById("Pilatus")
            self.detectorCenterChannel = \
                detConfig.getCenterChannelPixel(detector)
            self.detectorDimensions = detConfig.getNpixels(detector)
            detectorSize = detConfig.getSize(detector)
            self.detectorPixelWidth = \
                [detectorSize[0]/self.detectorDimensions[0],\
                 detectorSize[1]/self.detectorDimensions[1]]
            self.distanceToDetector = detConfig.getDistance(detector) 
            if self.numPixelsToAverage == None:
                self.numPixelsToAverage = [1,1]
            if self.detectorROI == None:
                self.detectorROI = [0, self.detectorDimensions[0],  
                                    0, self.detectorDimensions[1]]
            self.detectorPixelDirection1 = \
                detConfig.getPixelDirection1(detector)
            self.detectorPixelDirection2 = \
                detConfig.getPixelDirection2(detector)
        except DetectorConfigException as ex:
            raise ex
        except RSMap3DException as ex:
            print ("---Error Reading detector config")
            raise ex
        except Exception as ex:
            print ("---Unhandled Exception in loading detector config")
            raise ex
        self.specFile = os.path.join(self.projectDir, self.projectName + \
                                     self.projectExt)
        imageDir = os.path.join(self.projectDir, \
                                IMAGE_DIR_MERGE_STR % self.projectName)
        self.imageFileTmp = os.path.join(imageDir, \
                                TIFF_FILE_MERGE_STR % 
                                (self.projectName))
        # if needed load up the bad pixel file.
        if not (self.badPixelFile == None):
            
            badPixelFile = PilatusBadPixelFile(self.badPixelFile)
            self.badPixels = badPixelFile.getBadPixels()
             
        # id needed load the flat field file
        if not (self.flatFieldFile == None):
            self.flatFieldData = np.array(Image.open(self.flatFieldFile)).T
        # Load scan information from the spec file
        try:
            self.sd = SpecDataFile(self.specFile)
            self.mapHKL = mapHKL
            maxScan = int(self.sd.getMaxScanNumber())
            print maxScan
            if self.scans  == None:
                self.scans = range(1, maxScan+1)
            imagePath = os.path.join(self.projectDir, 
                            IMAGE_DIR_MERGE_STR % self.projectName)
            
            self.imageBounds = {}
            self.imageToBeUsed = {}
            self.availableScans = []
            self.incidentEnergy = {}
            self.ubMatrix = {}
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
                    if (os.path.exists(os.path.join(imagePath, \
                                            SCAN_NUMBER_MERGE_STR % scan))):
                        curScan = self.sd.scans[str(scan)]
                        self.availableScans.append(scan)
                        angles = self.getGeoAngles(curScan, self.angleNames)
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
            if self.progressUpdater <> None:
                self.progressUpdater(self.progressMax, self.progressMax)
        except IOError:
            raise IOError( "Cannot open file " + str(self.specFile))
        if len(self.getAvailableScans()) == 0:
            raise ScanDataMissingException("Could not find scan data for " + \
                                           "input file \n" + self.specFile + \
                                           "\nOne possible reason for this " + \
                                           "is that the image files are " + \
                                           "missing.  Images are assumed " + \
                                           "to be in " + \
                                           os.path.join(self.projectDir, 
                                        IMAGE_DIR_MERGE_STR % self.projectName))


        
    
    def to_bool(self, value):
        """
        Note this method found in answer to:
        http://stackoverflow.com/questions/715417/converting-from-a-string-to-boolean-in-python
        Converts 'something' to boolean. Raises exception if it gets a string 
        it doesn't handle.
        Case is ignored for strings. These string values are handled:
          True: 'True', "1", "TRue", "yes", "y", "t"
          False: "", "0", "faLse", "no", "n", "f"
        Non-string values are passed to bool.
        """
        if type(value) == type(''):
            if value.lower() in ("yes", "y", "true",  "t", "1"):
                return True
            if value.lower() in ("no",  "n", "false", "f", "0", ""):
                return False
            raise Exception('Invalid value for boolean conversion: ' + value)
        return bool(value)

    def rawmap(self,scans, angdelta=[0,0,0,0,0],
            adframes=None, mask = None):
        """
        read ad frames and and convert them in reciprocal space
        angular coordinates are taken from the spec file
        or read from the edf file header when no scan number is given (scannr=None)
        """
        
        if mask == None:
            mask_was_none = True
            #mask = [True] * len(self.getImageToBeUsed()[scans[0]])
        else:
            mask_was_none = False
        #sd = spec.SpecDataFile(self.specFile)
        intensity = np.array([])
        
        # fourc goniometer in fourc coordinates
        # convention for coordinate system:
        # x: upwards;
        # y: along the incident beam;
        # z: "outboard" (makes coordinate system right-handed).
        # QConversion will set up the goniometer geometry.
        # So the first argument describes the sample rotations, the second the
        # detector rotations and the third the primary beam direction.
        qconv = xu.experiment.QConversion(self.getSampleCircleDirections(), \
                                    self.getDetectorCircleDirections(), \
                                    self.getPrimaryBeamDirection())
    
        # define experimental class for angle conversion
        #
        # ipdir: inplane reference direction (ipdir points into the primary beam
        #        direction at zero angles)
        # ndir:  surface normal of your sample (ndir points in a direction
        #        perpendicular to the primary beam and the innermost detector
        #        rotation axis)
        en = self.getIncidentEnergy()
        hxrd = xu.HXRD(self.getInplaneReferenceDirection(), \
                       self.getSampleSurfaceNormalDirection(), \
                       en=en[self.getAvailableScans()[0]], \
                       qconv=qconv)

        
        # initialize area detector properties
        if (self.getDetectorPixelWidth() != None ) and \
            (self.getDistanceToDetector() != None):
            hxrd.Ang2Q.init_area(self.getDetectorPixelDirection1(), \
                self.getDetectorPixelDirection2(), \
                cch1=self.getDetectorCenterChannel()[0], \
                cch2=self.getDetectorCenterChannel()[1], \
                Nch1=self.getDetectorDimensions()[0], \
                Nch2=self.getDetectorDimensions()[0], \
                pwidth1=self.getDetectorPixelWidth()[0], \
                pwidth2=self.getDetectorPixelWidth()[1], \
                distance=self.getDistanceToDetector(), \
                Nav=self.getNumPixelsToAverage(), \
                roi=self.getDetectorROI()) 
        else:
            hxrd.Ang2Q.init_area(self.getDetectorPixelDirection1(), \
                self.getDetectorPixelDirection2(), \
                cch1=self.getDetectorCenterChannel()[0], \
                cch2=self.getDetectorCenterChannel()[1], \
                Nch1=self.getDetectorDimensions()[0], \
                Nch2=self.getDetectorDimensions()[0], \
                chpdeg1=self.getDetectorChannelsPerDegree()[0], \
                chpdeg2=self.getDetectorChannelsPerDegree()[1], \
                Nav=self.getNumPixelsToAverage(), 
                roi=self.getDetectorROI()) 
            
        angleNames = self.getAngles()
        scanAngle = {}
        for i in xrange(len(angleNames)):
            scanAngle[i] = np.array([])
    
        offset = 0
        imageToBeUsed = self.getImageToBeUsed()
        monitorName = self.getMonitorName()
        monitorScaleFactor = self.getMonitorScaleFactor()
        filterName = self.getFilterName()
        filterScaleFactor = self.getFilterScaleFactor()
        for scannr in scans:
            if self.haltMap:
                raise ProcessCanceledException("Process Canceled")
            scan = self.sd.scans[str(scannr)]
            angles = self.getGeoAngles(scan, angleNames)
            scanAngle1 = {}
            scanAngle2 = {}
            for i in xrange(len(angleNames)):
                scanAngle1[i] = angles[:,i]
                scanAngle2[i] = []
            if monitorName != None:
                monitor_data = scan.data.get(monitorName)
                if monitor_data == None:
                    raise IOError("Did not find Monitor source '" + \
                                  monitorName + \
                                  "' in the Spec file.  Make sure " + \
                                  "monitorName is correct in the " + \
                                  "instrument Config file")
            if filterName != None:
                filter_data = scan.data.get(filterName)
                if filter_data == None:
                    raise IOError("Did not find filter source '" + \
                                  filterName + \
                                  "' in the Spec file.  Make sure " + \
                                  "filterName is correct in the " + \
                                  "instrument Config file")
            # read in the image data
            arrayInitializedForScan = False
            foundIndex = 0
            
            if mask_was_none:
                mask = [True] * len(self.getImageToBeUsed()[scannr])            
            
            for ind in xrange(len(scan.data[scan.data.keys()[0]])):
                if imageToBeUsed[scannr][ind] and mask[ind]:    
                    # read tif image
                    im = Image.open(self.imageFileTmp % (scannr, scannr, ind))
                    img = np.array(im.getdata()).reshape(im.size[1],im.size[0]).T
                    img = self.hotpixelkill(img)
                    ff_data = self.getFlatFieldData()
                    if not (ff_data == None):
                        img = img * ff_data
                    # reduce data siz
                    img2 = xu.blockAverage2D(img, 
                                            self.getNumPixelsToAverage()[0], \
                                            self.getNumPixelsToAverage()[1], \
                                            roi=self.getDetectorROI())

                    # apply intensity corrections
                    if monitorName != None:
                        img2 = img2 / monitor_data[ind] * monitorScaleFactor
                    if filterName != None:
                        img2 = img2 / filter_data[ind] * filterScaleFactor

                    # initialize data array
                    if not arrayInitializedForScan:
                        imagesToProcess = [imageToBeUsed[scannr][i] and mask[i] for i in range(len(imageToBeUsed[scannr]))]
                        if not intensity.shape[0]:
                            intensity = np.zeros((np.count_nonzero(imagesToProcess),) + img2.shape)
                            arrayInitializedForScan = True
                        else: 
                            offset = intensity.shape[0]
                            intensity = np.concatenate(
                                (intensity,
                                (np.zeros((np.count_nonzero(imagesToProcess),) + img2.shape))),
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
        if self.ubMatrix[scans[0]] == None:
            qx, qy, qz = hxrd.Ang2Q.area(*angleList,  \
                            roi=self.getDetectorROI(), 
                            Nav=self.getNumPixelsToAverage())
        else:
            qx, qy, qz = hxrd.Ang2Q.area(*angleList, \
                            roi=self.getDetectorROI(), 
                            Nav=self.getNumPixelsToAverage(), \
                            UB = self.ubMatrix[scans[0]])
            

        # apply selected transform
        qxTrans, qyTrans, qzTrans = \
            self.transform.do3DTransform(qx, qy, qz)

    
        return qxTrans, qyTrans, qzTrans, intensity
        
class LoadCanceledException(RSMap3DException):
    '''
    Exception Thrown when loading data is canceled.
    '''
    def __init__(self, message):
        super(LoadCanceledException, self).__init__(message)
        
class Sector33SpecFileException(RSMap3DException):
    '''
    Exception class to be raised if there is a problem loading information
    from a spec file
    file
    '''
    def __init__(self, message):
        super(Sector33SpecFileException, self).__init__(message)



