"""Main Blaster Turret
"""
import time
from pi_turret.blaster.hyperfire import Hyperfire
from pi_turret.stepper_motor.stepper import StepperMotor, STEP_DEGREES
from pi_turret.stepper_motor.stepper_slot import StepperMotorSlot
from pi_turret.sensor.button import yaw_button, pitch_button

class Turret:
    """Turret that can move left/right and up/down
    """

    def __init__(self):
        self.blaster = Hyperfire()
        self.pitch_motor = StepperMotor(StepperMotorSlot.STEPPER_TWO)
        self.yaw_motor = StepperMotor(StepperMotorSlot.STEPPER_ONE)
        self.pitch = None
        self.yaw = None

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

        self.pitch = 0
        self.yaw = 0

    def move(self, pitch: float, yaw: float):
        move_pitch = pitch - self.pitch
        move_yaw = yaw - self.yaw

        while move_pitch is not 0 or move_yaw is not 0:
            if move_pitch > 0:
                self.pitch_motor.one_step_backwards()
                move_pitch -= STEP_DEGREES
            elif move_pitch < 0:
                self.pitch_motor.one_step_forward()
                move_pitch += STEP_DEGREES
            if abs(move_pitch) < (STEP_DEGREES / 2):
                move_pitch = 0

            if move_yaw > 0:
                self.yaw_motor.one_step_backwards()
                move_yaw -= STEP_DEGREES
            elif move_pitch < 0:
                self.yaw_motor.one_step_forward()
                move_yaw += STEP_DEGREES
            if abs(move_yaw) < (STEP_DEGREES / 2):
                move_yaw = 0

            time.sleep(0.02)


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
