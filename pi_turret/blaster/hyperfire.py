"""Hyperfire Class to model the actual BLASTER.
"""
import time
from pi_turret.dc_motor.motor import DCMotor, FEED_PIN, FLYWHEEL_PIN


class Hyperfire:
    """Hyperfire Class to model the actual BLASTER.
    """

    def __init__(self):
        self.flywheels = DCMotor(FLYWHEEL_PIN)
        self.feeder = DCMotor(FEED_PIN)

    def flywheels_on(self):
        """Signal flywheels to turn on
        """
        self.flywheels.power()

    def flywheels_off(self):
        """Signal flywheels to turn off
        """
        self.flywheels.off()

    def feed_on(self):
        """Signal feeder to turn on
        """
        self.feeder.power()

    def feed_off(self):
        """Signal feeder to turn off
        """
        self.feeder.off()

    def burst_fire(self, duration=0.2):
        """Signals the flywheels to rev then the feeder for the given duration
        """
        self.flywheels_on()
        time.sleep(0.2)
        self.feed_on()
        # Firing duration
        time.sleep(duration)
        self.feed_off()
        # Spindown time
        time.sleep(1) # Check this
        self.flywheels_off()


if __name__ == "__main__":
    BLASTER = Hyperfire()
    BLASTER.burst_fire()
    DCMotor.cleanup()
    