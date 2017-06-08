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
       <circleAxis number="1" specMotorName="Gamma" directionAxis="x+"/>
       <circleAxis number="2" specMotorName="Delta" directionAxis="z-"/>
    </detectorCircles>
     <sampleAngleMapFunction name="_calc_sum_gamma_mu" 
     module="rsMap3D.anglecalcexamples.sumgammamu"
     calcOnScannedRef="True">
          <primaryAngle number="5"/>
          <referenceAngle number="1" specMotorName="Mu"/>
          <referenceAngle number="2" specMotorName="Gamma"/>
     </sampleAngleMapFunction>

Here the reference angles specify the angles to be used in the calculations.
The angle "number" refers to an index (starting at one) for these angles.  This
index orders the angles going into the function.  The specMotorName will give t
the motor name used to grab angle values from the spec file.  Here Mu will go in 
as the first angle anf Gamma will go in as the second.

This function will add the angles and return a list of one list of angles, 
intended to replace the value of the angle Gamma (Gamma is stacked on top of Mu 
but Mu is stored as a reference from null on top of Gamma).  We need to feed the 
sum as Gamma since Gamma in considered an independant rotation of the detector 
axis.

Again we are returning values as a single angle/motor which should replace gamma.
Here the primaryAngle is number 5.  In this particular case, there are 4 sample
angles and 2 detector angles.  Gamma is the first detector angle.  The values in
"angles" are combination of sampleAngles then detector angles.  There are four
sample angles and two detector angles here.  Since Gamma is the first detector 
angle, the reference angle is 5 (4 sample angles +1 detector angle).  The output
values will therefore be used to replace the first detector angle.
'''

def calcSumGammaMu(primaryAngles=None,
                                   referenceAngles=None):
        """
        This is function will take in a list with the angle values for the
        diffractometer.  I will take in two angles in the reference angles,
        sum these angles and then return these to a single angle that should 
        be specified by the primary angles  
        :param primaryAngles:  list of sample axis numbers to be handled by 
        the conversion
        :param referenceAngles: list of reference angles to be used in angle 
        conversion
        """

        print ("Running conversion function calcSumGammaMu")
        mu = referenceAngles[:,0]
        gamma = referenceAngles[:,1]
        #muOut = mu
        gammaOut = gamma + mu
        
        return [gammaOut,]
                                   