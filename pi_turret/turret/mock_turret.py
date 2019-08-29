
class Turret:
    """Mock Turret that can be used when developing not on a Raspberry Pi
    """

    def __init__(self):
        self.blaster = None
        self.pitch_motor = None
        self.yaw_motor = None

    def calibrate(self):
        """Calibrate the position of the stepper motors
        """

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
