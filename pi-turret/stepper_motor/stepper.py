from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
from stepper_slot import StepperMotorSlot
import time

kit = MotorKit()

step_degrees = 1.8

class StepperMotor(object):
    """The Stepper Motor offers semi precise control to control the turret.
    """

    def __init__(self, stepper):
        if stepper == StepperMotorSlot.STEPPER_ONE:
            self.motor = kit.stepper1

        if stepper == StepperMotorSlot.STEPPER_TWO:
            self.motor = kit.stepper2


    def test(self):

        for i in range(round(45/step_degrees)):
            result = self.motor.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
            print(result)
            time.sleep(0.02)
            
        # time.sleep(.5)
        
        for i in range(round(90/step_degrees)):
            result = self.motor.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
            print(result)
            time.sleep(0.02)
            
        # time.sleep(.5)
        
        for i in range(round(45/step_degrees)):
            result = self.motor.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
            print(result)
            time.sleep(0.02)
           
        # time.sleep(1)
        # self.motor.release()
    

if __name__ == "__main__":
    
    motor_one = StepperMotor(StepperMotorSlot.STEPPER_ONE)
    motor_one.test()

    # time.sleep(1)

    motor_two = StepperMotor(StepperMotorSlot.STEPPER_TWO)
    motor_two.test()
    
    motor_one.motor.release()
    motor_two.motor.release()
    # while True:
    #     time.sleep(1)