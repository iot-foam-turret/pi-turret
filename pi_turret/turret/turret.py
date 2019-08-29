"""Main Blaster Turret
"""
from pi_turret.blaster.hyperfire import Hyperfire
from pi_turret.stepper_motor.stepper import StepperMotor
from pi_turret.stepper_motor.stepper_slot import StepperMotorSlot

class Turret:
    """Turret that can move left/right and up/down
    """

    def __init__(self):
        self.blaster = Hyperfire()
        self.pitch_motor = StepperMotor(StepperMotorSlot.STEPPER_ONE)
        self.yaw_motor = StepperMotor(StepperMotorSlot.STEPPER_TWO)


    def calibrate(self):
        """Calibrate the position of the stepper motors
        """
