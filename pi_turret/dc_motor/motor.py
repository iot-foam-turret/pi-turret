"""DCMotor
"""
import time
import RPi.GPIO as GPIO

FLYWHEEL_PIN = 21
FEED_PIN = 19

GPIO.setmode(GPIO.BCM)

class DCMotor:
    """DC Motor commonly used in foam blasters.
    """

    def __init__(self, pin):
        self.gpio = pin
        GPIO.setup(self.gpio, GPIO.OUT)


    def power(self):
        """Signal DC motor to turn on
        """
        GPIO.setmode(GPIO.BCM)
        GPIO.output(self.gpio, GPIO.HIGH)


    def off(self):
        """Signal DC motor to turn off
        """
        GPIO.setmode(GPIO.BCM)
        GPIO.output(self.gpio, GPIO.LOW)


    def test(self):
        """Signal DC motor to turn on, wait, then turn off
        """
        self.power()

        time.sleep(0.5)

        self.off()

    @staticmethod
    def cleanup():
        """Reset GPIO. Should be called at the end of the program
        """
        GPIO.cleanup()


if __name__ == "__main__":

    MOTOR = DCMotor(FLYWHEEL_PIN)
    MOTOR.test()
    DCMotor.cleanup()
