"""This will be the main file that runs the automated turret"""
import sys
import getopt
from pi_turret.test_scripts.keyboard_control import main as keyboard_main
from pi_turret.iot.runner import main as iot_main


def main():
    """Main function run when module is executed."""
    print("Hello from Pi Turret")

    try:
        opts, _ = getopt.getopt(sys.argv[1:], "hc:", "controls=")
    except getopt.GetoptError:
        print("Error getting options")

    if len(opts) is 0:
        print("IoT Turret")
        iot_main()

    for opt, arg in opts:
        if opt == "-h":
            help_massage = "\tExample usage: python -m pi_turret -c <control>\n\t" + \
                "controls: keyboard, iot"
            print(help_massage)
            sys.exit()
        elif opt in ("-c", "--controls"):
            if arg == "keyboard":
                print("Use Keyboard")
                keyboard_main()
            elif arg == "iot":
                print("IoT Turret")
                iot_main()


if __name__ == "__main__":
    main()
