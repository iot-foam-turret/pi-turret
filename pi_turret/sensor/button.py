import RPi.GPIO as GPIO
import time


class Button:

    def __init__(self, pin):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def is_pressed(self):
        return not GPIO.input(self.pin)


def yaw_button():
    return Button(6)


def pitch_button():
    return Button(13)


def magazine_button():
    return Button(16)


if __name__ == "__main__":
    # 16 red - magazine
    # 13 yellow - pitch
    # 6 green - yaw
    BUTTON = Button(16)
    while True:
        if BUTTON.is_pressed():
            print('Button Pressed')
            time.sleep(0.2)
