# This file is part of xrayutilities.
#
# xrayutilities is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# Copyright (C) 2012 Dominik Kriegner <dominik.kriegner@gmail.com>

# ALSO LOOK AT THE FILE xrayutilities_example_plot_3D_ESRF_ID01.py

import numpy
import math
import xrayutilities as xu
import os
import sys
import Image

#if not '/Users/cschlep/software/python/pyspec' in sys.path:
#    sys.path.insert(0,'/Users/cschlep/software/python/pyspec')
from pyspec import spec

# x-ray energy in eV
default_en=15200.0 

# cch describes the "zero" position of the detector. this means at
# "detector arm angles"=0 the primary beam is hitting the detector at some
# particular position. these two values specify this pixel position
default_cch = [206,85]

# channel per degree for the detector
# chpdeg specify how many pixels the beam position on the detector changes
# for 1 degree movement. basically this determines the detector distance
# and needs to be determined every time the distance is changed
#default_chpdeg = [106,106] 
default_chpdeg = [77,77] 

# reduce data: number of pixels to average in each detector direction
default_nav = [1,1] 

# region of interest on the detector
default_roi = [0,487,0,195] 


def hotpixelkill(ad_data):
    """
    function to remove hot pixels from CCD frames
    ADD REMOVE VALUES IF NEEDED!
    """
    
    #ad_data[44,159] = 0
    
    return ad_data

def rawmap(specfile,scans,imageToBeUsed, adfiletmp,roi=default_roi,angdelta=[0,0,0,0,0],
        en=default_en,cch=default_cch,chpdeg=default_chpdeg,nav=default_nav,
        adframes=None):
    """
    read ad frames and and convert them in reciprocal space
    angular coordinates are taken from the spec file
    or read from the edf file header when no scan number is given (scannr=None)
    """
    
    sd = spec.SpecDataFile(specfile)
    intensity = numpy.array([])
    tth = th = phi = chi = numpy.array([])

    # fourc goniometer
    # convention for coordinate system:
    # x: downstream;
    # z: upwards;
    # y: "outboard" (makes coordinate system right-handed).
    # QConversion will set up the goniometer geometry.
    # So the first argument describes the sample rotations, the second the
    # detector rotations and the third the primary beam direction.
    #qconv = xu.experiment.QConversion(['y-','x+','y-'], ['y-'], [1,0,0])

    # define experimental class for angle conversion
    #
    # ipdir: inplane reference direction (ipdir points into the primary beam
    #        direction at zero angles)
    # ndir:  surface normal of your sample (ndir points in a direction
    #        perpendicular to the primary beam and the innermost detector
    #        rotation axis)
    #hxrd = xu.HXRD([0,1,0], [0,0,1], en=en, qconv=qconv)
    
    # initialize area detector properties
    #hxrd.Ang2Q.init_area('z-', 'y+', cch1=cch[0], cch2=cch[1],
    #    Nch1=487, Nch2=195, chpdeg1=chpdeg[0], chpdeg2=chpdeg[1],
    #    Nav=nav, roi=roi) 
        
    
    # fourc goniometer in fourc coordinates
    # convention for coordinate system:
    # x: upwards;
    # y: along the incident beam;
    # z: "outboard" (makes coordinate system right-handed).
    # QConversion will set up the goniometer geometry.
    # So the first argument describes the sample rotations, the second the
    # detector rotations and the third the primary beam direction.
    qconv = xu.experiment.QConversion(['z-','y+','z-'], ['z-'], [0,1,0])

    # define experimental class for angle conversion
    #
    # ipdir: inplane reference direction (ipdir points into the primary beam
    #        direction at zero angles)
    # ndir:  surface normal of your sample (ndir points in a direction
    #        perpendicular to the primary beam and the innermost detector
    #        rotation axis)
    hxrd = xu.HXRD([0,1,0], [1,0,0], en=en, qconv=qconv)
    
    
    # initialize area detector properties
    hxrd.Ang2Q.init_area('x-', 'z+', cch1=cch[0], cch2=cch[1],
        Nch1=487, Nch2=195, chpdeg1=chpdeg[0], chpdeg2=chpdeg[1],
        Nav=nav, roi=roi) 
        
    print hxrd

    offset = 0
    
    for scannr in scans:
        scan = sd[scannr]
        scan.geo_angle_names = ['X2mtheta', 'theta', 'phi', 'chi']
        angles = scan.get_geo_angles()
        tth1 = angles[:,0]
        th1 = angles[:,1]
        chi1 = angles[:,3]
        phi1 = angles[:,2]
        th2 = []
        chi2 = []
        phi2 = []
        tth2 = []
        # read in the image data
        arrayInitializedForScan = False
        foundIndex = 0
        for ind in xrange(scan.data.shape[0]):
            if imageToBeUsed[scannr][ind]:    
                # read tif image
                img = numpy.array(Image.open(adfiletmp % (scannr, scannr, ind))).T
                img = hotpixelkill(img)
    
                # reduce data size
                #print img
                #print nav[0]
                #print nav[1]
                #print roi
                img2 = xu.blockAverage2D(img, nav[0],nav[1], roi=roi)
                #print "img2.shape: " +str(img2.shape)
                # initialize data array
                if not arrayInitializedForScan:
                    if not intensity.shape[0]:
                        intensity = numpy.zeros((numpy.count_nonzero(imageToBeUsed[scannr]),) + img2.shape)
                        arrayInitializedForScan = True
                    else: 
                        offset = intensity.shape[0]
                        intensity = numpy.concatenate(
                            (intensity,
                            (numpy.zeros((numpy.count_nonzero(imageToBeUsed[scannr]),) + img2.shape))),
                            axis=0)
                        arrayInitializedForScan = True
                # add data to intensity array
                intensity[foundIndex+offset,:,:] = img2
                #print sys.getsizeof(intensity)
                tth2.append(tth1[ind])
                th2.append(th1[ind])
                phi2.append(phi1[ind])
                chi2.append(chi1[ind])
                foundIndex += 1
        if len(tth2) > 0:
            tth = numpy.concatenate((tth, numpy.array(tth2)), axis = 0)
            th  = numpy.concatenate((th, numpy.array(th2)), axis = 0)
            phi = numpy.concatenate((phi, numpy.array(phi2)), axis = 0)
            chi = numpy.concatenate((chi, numpy.array(chi2)), axis = 0)
    # transform scan angles to reciprocal space coordinates for all detector pixels
    
    qx, qy, qz = hxrd.Ang2Q.area(th, chi, phi, tth,  roi=roi, Nav=nav)

    return qx, qy, qz, intensity

def gridmap(specfile,scannr, imageToBeUsed,adfiletmp,nx,ny,nz,**kwargs):
    """
    read ad frames and grid them in reciprocal space
    angular coordinates are taken from the spec file

    **kwargs are passed to the rawmap function
    """

    gridder = xu.Gridder3D(nx,ny,nz)
    gridder.KeepData(True)
    gridder.dataRange((kwargs['xmin'], kwargs['xmax']), 
                      (kwargs['ymin'], kwargs['ymax']), 
                      (kwargs['zmin'], kwargs['zmax']), 
                      True)
    kwargs1 = dict(kwargs)
    del kwargs1['xmin']
    del kwargs1['xmax']
    del kwargs1['ymin']
    del kwargs1['ymax']
    del kwargs1['zmin']
    del kwargs1['zmax']
    
    for scan in scannr:
        if True in imageToBeUsed[scan]:
            qx, qy, qz, intensity = rawmap(specfile,(scan,), imageToBeUsed, \
                                           adfiletmp,**kwargs1)
    
            # convert data to rectangular grid in reciprocal space
            gridder(qx,qy,qz,intensity)

    return gridder.xaxis,gridder.yaxis,gridder.zaxis,gridder.gdata,gridder


def polemap(specfile,scannr, imageToBeUsed, adfiletmp,nspx,nspy,nspq,**kwargs):
    """
    read ad frames and grid them in reciprocal space
    angular coordinates are taken from the spec file

    **kwargs are passed to the rawmap function
    """

    gridder = xu.Gridder3D(nspx,nspy,nspq)
    gridder.KeepData(True)
    qxmin = kwargs['xmin']
    qxmax = kwargs['xmax']
    qymin = kwargs['ymin']
    qymax = kwargs['ymax']
    qzmin = kwargs['zmin']
    qzmax = kwargs['zmax']
    
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
    kwargs1 = dict(kwargs)
    del kwargs1['xmin']
    del kwargs1['xmax']
    del kwargs1['ymin']
    del kwargs1['ymax']
    del kwargs1['zmin']
    del kwargs1['zmax']
    
    for scan in scannr:
        #print '---' + str(scan) + str(imageToBeUsed[scan])
        if True in imageToBeUsed[scan]:
            qx, qy, qz, intensity = rawmap(specfile, (scan,), imageToBeUsed, \
                                            adfiletmp, **kwargs1)
            
            # convert qx,qy,qz to stereographic projection
            spq = numpy.sqrt(qx**2 + qy**2 + qz**2)
            spx = qx / (spq + qz)
            spy = qy / (spq + qz)
            
        
            # convert data to rectangular grid in reciprocal space
            gridder(spx,spy,spq,intensity)

    return gridder.xaxis,gridder.yaxis,gridder.zaxis,gridder.gdata,gridder

