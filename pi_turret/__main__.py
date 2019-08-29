"""This will be the main file that runs the automated turret"""
import sys, getopt
from pi_turret.test_scripts.keyboard_control import main as keyboard_main

print("Hello from Pi Turret")

try:
    opts, args = getopt.getopt(sys.argv[1:], "hc=", "controls=")
except getopt.GetoptError:
    print("Error getting options")

for opt, arg in opts:
    if opt == "-h":
        help_massage = "\tExample usage: python -m pi_turret -c <control>\n\tcontrols: keyboard, iot"
        print(help_massage)
        sys.exit()
    elif opt in ("-c", "--controls"):
        if arg == "keyboard":
            print("Use Keyboard")
            keyboard_main()
        elif arg == "iot":
            print("IoT Not Implemented")
            sys.exit()
