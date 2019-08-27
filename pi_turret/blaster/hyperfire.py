from pi_turret.dc_motor.motor import DCMotor, feed_pin, flywheel_pin
import time


class Hyperfire(object):

    def __init__(self):
        self.flywheels = DCMotor(flywheel_pin)
        self.feeder = DCMotor(feed_pin)

    
    def burst_fire(self):
        self.flywheels.on()
        time.sleep(0.2)
        self.feeder.on()
        # Firing duration
        time.sleep(0.2)
        self.feeder.off()
        # Spindown time
        time.sleep(1) # Check this
        self.flywheels.off()


if __name__ == "__main__":
    blaster = Hyperfire()
    blaster.burst_fire()
    DCMotor.cleanup()
    