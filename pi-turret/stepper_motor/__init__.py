from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
from enum import Enum
import time

kit = MotorKit()

step_degrees = 1.8

class StepperMotors(Enum):
    STEPPER_ONE = 1
    STEPPER_TWO = 2

class StepperMotor(object):
    """The Stepper Motor offers semi precise control to control the turret.
    """

    def __init__(self, stepper):
        if stepper == StepperMotors.STEPPER_ONE:
            self.motor = kit.stepper1

        if stepper == StepperMotors.STEPPER_TWO:
            self.motor = kit.stepper2
        
        print(self.motor)

    def test(self):
        for i in range(round(90/step_degrees)):
            self.motor.onestep(style=stepper.DOUBLE)
            
        time.sleep(1)
        
        for i in range(round(180/step_degrees)):
            self.motor.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
            
        time.sleep(1)
        
        for i in range(round(90/step_degrees)):
            self.motor.onestep(style=stepper.DOUBLE)
           
        time.sleep(1)
        self.motor.release()
    

if __name__ == "__main__":
    
    motor_one = StepperMotor(StepperMotors.STEPPER_ONE)
    motor_one.test()

    motor_two = StepperMotor(StepperMotors.STEPPER_TWO)
    motor_two.test()
    