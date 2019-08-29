
"""Module for testing the turret with the keyboard controls
"""
import curses
try:
    from pi_turret.turret.turret import Turret
except:
    from pi_turret.turret.mock_turret import Turret

def main():
    """Main script to control the turret with the keyboard
    """
    turret = Turret()

    # get the curses screen window
    screen = curses.initscr()

    # turn off input echoing
    curses.noecho()

    # respond to keys immediately (don't wait for enter)
    curses.cbreak()

    # map arrow keys to special values
    screen.keypad(True)

    try:
        while True:
            char = screen.getch()
            if char == ord('q'):
                break
            elif char == curses.KEY_RIGHT:
                turret.move_right()
                # print doesn't work with curses, use addstr instead
                screen.addstr(0, 0, 'right')
            elif char == curses.KEY_LEFT:
                turret.move_left()
                screen.addstr(0, 0, 'left ')
            elif char == curses.KEY_UP:
                turret.move_up()
                screen.addstr(0, 0, 'up   ')
            elif char == curses.KEY_DOWN:
                turret.move_down()
                screen.addstr(0, 0, 'down ')
    finally:
        # shut down cleanly
        curses.nocbreak()
        screen.keypad(0)
        curses.echo()
        curses.endwin()

if __name__ == "__main__":
    main()
