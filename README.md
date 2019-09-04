# pi-turret
Raspberry Pi Automated Foam Turret

Inspired by [https://www.hackster.io/hackershack/raspberry-pi-motion-tracking-gun-turret-77fb0b](https://www.hackster.io/hackershack/raspberry-pi-motion-tracking-gun-turret-77fb0b)

# Setup
This project uses Python 3. The best way to set that up is to first create a virtual environment using Python 3. [Instructions](https://realpython.com/python-virtual-environments-a-primer/)

The [stepper motor hat](https://learn.adafruit.com/adafruit-dc-and-stepper-motor-hat-for-raspberry-pi/overview) requires I2C to be enabled on the Raspberry Pi. [Instructions](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c)

Before creating a virtual env:
```
sudo apt install python3-opencv
```
After OpenCV is install, create your virtual environment
```
mkvirtualenv --system-site-packages pi_turret
```

Required packages are included in the requirements.txt file so install using `pip install -r requirements.txt` or 
```
make init
```
