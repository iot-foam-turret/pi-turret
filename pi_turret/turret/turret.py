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
        self.pitch_motor = StepperMotor(StepperMotorSlot.STEPPER_TWO)
        self.yaw_motor = StepperMotor(StepperMotorSlot.STEPPER_ONE)

    def calibrate(self):
        """Calibrate the position of the stepper motors
        """

    def move_up(self):
        """Move up one step
        """
        self.pitch_motor.step_backward()


    def move_down(self):
        """Move down one step
        """
        self.pitch_motor.step_forward()


    def move_left(self):
        """Move left one step
        """
        self.yaw_motor.step_backward()


    def move_right(self):
        """Move right one step
        """
        self.yaw_motor.step_forward()
