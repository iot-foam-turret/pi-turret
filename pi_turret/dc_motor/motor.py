import RPi.GPIO as GPIO
import time

flywheel_pin = 21
feed_pin = 19

GPIO.setmode(GPIO.BCM)

class DCMotor(object):
    """DC Motor commonly used in foam blasters.
    """

    def __init__(self, pin):
        self.gpio = pin
        GPIO.setup(self.gpio, GPIO.OUT)


    def on(self):
        GPIO.output(self.gpio, GPIO.HIGH)


    def off(self):
        GPIO.output(self.gpio, GPIO.LOW)


    def test(self):
        
        self.on()

        time.sleep(0.5)

        self.off()
    

    def cleanup():
        GPIO.cleanup()


if __name__ == "__main__":
    
    motor = DCMotor(feed_pin)
    motor.test()
    DCMotor.cleanup()
