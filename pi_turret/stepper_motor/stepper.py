"""StepperMotor
"""
import time
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
from stepper_slot import StepperMotorSlot

KIT = MotorKit()

STEP_DEGREES = 1.8

class StepperMotor:
    """The Stepper Motor offers semi precise control to control the turret.
    """

    def __init__(self, stepperMotorSlot):
        if stepperMotorSlot == StepperMotorSlot.STEPPER_ONE:
            self.motor = KIT.stepper1

        if stepperMotorSlot == StepperMotorSlot.STEPPER_TWO:
            self.motor = KIT.stepper2

    def step_forward(self, degrees):
        """Converts the given degrees to steps and moves the motor forward
        """
        for i in range(round(degrees/STEP_DEGREES)):
            result = self.motor.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
            print(f"{i}: {result}")
            time.sleep(0.02)


    def step_backward(self, degrees):
        """Converts the given degrees to steps and moves the motor backward
        """
        for i in range(round(degrees/STEP_DEGREES)):
            result = self.motor.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
            print(f"{i}: {result}")
            time.sleep(0.02)


    def test(self):
        """Method for basic test of functionality
        """

        self.step_forward(45)


        for i in range(round(45/STEP_DEGREES)):
            result = self.motor.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
            print(f"{i}: {result}")
            time.sleep(0.02)

        # time.sleep(.5)
        self.step_backward(90)
        for i in range(round(90/STEP_DEGREES)):
            result = self.motor.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
            print(f"{i}: {result}")
            time.sleep(0.02)

        # time.sleep(.5)

        for i in range(round(45/STEP_DEGREES)):
            result = self.motor.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
            print(f"{i}: {result}")
            time.sleep(0.02)

        # time.sleep(1)
        # self.motor.release()


if __name__ == "__main__":

    MOTOR_ONE = StepperMotor(StepperMotorSlot.STEPPER_ONE)
    MOTOR_ONE.test()

    # time.sleep(1)

    MOTOR_TWO = StepperMotor(StepperMotorSlot.STEPPER_TWO)
    MOTOR_TWO.test()

    MOTOR_ONE.motor.release()
    MOTOR_TWO.motor.release()
    # while True:
    #     time.sleep(1)
