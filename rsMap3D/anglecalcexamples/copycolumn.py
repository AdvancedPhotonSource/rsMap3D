'''
 Copyright (c) 2017, UChicago Argonne, LLC
 See LICENSE file.
'''
'''
This function is to be used by fixGeoAngles in the selected data source.
The function is configured in the instrument configuration file.  Inside
the instrument configuration file there should be a <sampleAngleMapFunction>
Dispite the name, this function can operate across all of the angles in the 
diffractometer since they are fed into the angles argument.  An example, 
related to this function, along with the angle definitions are shown here:

    <sampleCircles numCircles="4">
       <circleAxis number="1" specMotorName="Mu" directionAxis="x+"/>
       <circleAxis number="2" specMotorName="Theta" directionAxis="z-"/>
       <circleAxis number="3" specMotorName="Chi" directionAxis="y+"/>
       <circleAxis number="4" specMotorName="Phi" directionAxis="z-"/>
    </sampleCircles>

    <!-- Define the detector circles as a series of axes. -->
    <detectorCircles numCircles="2">
       <circleAxis number="1" specMotorName="Mu2" directionAxis="x+"/>
       <circleAxis number="2" specMotorName="Gamma" directionAxis="x+"/>
       <circleAxis number="3" specMotorName="Delta" directionAxis="z-"/>
    </detectorCircles>
     <sampleAngleMapFunction name="calcCopyColumn" 
     module="rsMap3D.anglecalcexamples.copycolumn"
     calcOnScannedRef="True">
          <primaryAngle number="5"/>
          <referenceAngle number="1" specMotorName="Mu"/>
     </sampleAngleMapFunction>

Here the reference angles specify the angles to be used in the calculations.
The angle "number" refers to an index (starting at one) for these angles.  This
index orders the angles going into the function.  The specMotorName will give t
the motor name used to grab angle values from the spec file.  Here Mu will go in 
as the first angle and Gamma will go in as the second.

This function is meant to replace one angle column (the primaryAngle)with 
the the values in another column (the reference column).  Here we have a 
case where both the sample circles and detector circles share a common 
motor Mu.  The first detector angle can be any column at the start.  It 
is just a placeholder for the Mu values (store in a single column in the 
spec file) to be used for the detector circles.  This function &  config 
file are meant to copy the Mu values from the first sample angle (Mu) into 
a "dummy" column Mu2 (which is in the spec file but not needed elsewhere).
A similar means of doing this is to have a copy of this angle in the spec
file with a different name.  It is just not possible to reuse an angle 
name in the list of circles.

A copy of Mu is made and is returned in the list of primary angles.  Per 
the instrument config, these angles will be placed in the 5th circle, Mu 
since 4sample detector + 1 places us at Mu2, which again has just been
a placeholder for this purpose.
'''
import logging
logger = logging.getLogger(__name__)
def calcCopyColumn(primaryAngles=None,
                                   referenceAngles=None):
        """
        This is function will take in a list with the angle values for the
        diffractometer.  This takes one reference angle, a copy is made 
        to replace the single primary angle.  
        :param primaryAngles:  list of sample axis numbers to be handled by 
        the conversion
        :param referenceAngles: list of reference angles to be used in angle 
        conversion
        """

        logger.debug ("Running conversion function calcCopyColumn")
        toCopy = referenceAngles[:,0]
        copyOut = toCopy[:]
        
        return [copyOut,]
                                   