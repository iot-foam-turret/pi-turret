"""Main Blaster Turret
"""
from pi_turret.blaster.hyperfire import Hyperfire
from pi_turret.stepper_motor.stepper import StepperMotor
from pi_turret.stepper_motor.stepper_slot import StepperMotorSlot
from pi_turret.sensor.button import yaw_button, pitch_button

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
        yaw_sensor = yaw_button()
        while not yaw_sensor.is_pressed():
            self.move_left()
        for _ in range(75):
            self.move_right()

        pitch_sensor = pitch_button()
        while not pitch_sensor.is_pressed():
            self.move_up()
        for _ in range(21):
            self.move_down()

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

if __name__ == "__main__":
    TURRET = Turret()
    TURRET.calibrate()
    while True:
        pass
