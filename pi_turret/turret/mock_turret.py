"""Mock Turret that can be used when developing not on a Raspberry Pi
"""
from typing import Callable
from pi_turret.turret.mode import Mode

class Turret:
    """Mock Turret that can be used when developing not on a Raspberry Pi
    """

    def __init__(self):
        self.blaster = None
        self.pitch_motor = None
        self.yaw_motor = None
        self.pitch = 0
        self.yaw = 0
        self.ammo = 22
        self.mode = Mode.waiting

    def calibrate(self):
        """Calibrate the position of the stepper motors
        """
        self.pitch = 0
        self.yaw = 0

    def move(self, pitch: float, yaw: float):
        """
        Move the turret to the given pitch and yaw
        """
        self.pitch = pitch
        self.yaw = yaw


    def burst_fire(self, duration: float, completion: Callable = None):
        """
        Burst Fire
        """
        self.ammo = self.ammo - 22
        self.mode = Mode.waiting
        if completion is not None:
            completion()

    def move_up(self):
        """Move up one step
        """
        # self.pitch_motor.step_backward()

    def move_down(self):
        """Move down one step
        """
        # self.pitch_motor.step_forward()

    def move_left(self):
        """Move left one step
        """
        # self.yaw_motor.step_backward()

    def move_right(self):
        """Move right one step
        """
        # self.yaw_motor.step_forward()
