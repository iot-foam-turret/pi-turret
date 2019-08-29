
"""Module for testing the turret with the keyboard controls
"""
import curses
from pi_turret.turret.turret import Turret

TURRET = Turret()

# get the curses screen window
SCREEN = curses.initscr()

# turn off input echoing
curses.noecho()

# respond to keys immediately (don't wait for enter)
curses.cbreak()

# map arrow keys to special values
SCREEN.keypad(True)

try:
    while True:
        CHAR = SCREEN.getch()
        if CHAR == ord('q'):
            break
        elif CHAR == curses.KEY_RIGHT:
            TURRET.move_right()
            # print doesn't work with curses, use addstr instead
            SCREEN.addstr(0, 0, 'right')
        elif CHAR == curses.KEY_LEFT:
            TURRET.move_left()
            SCREEN.addstr(0, 0, 'left ')
        elif CHAR == curses.KEY_UP:
            TURRET.move_up()
            SCREEN.addstr(0, 0, 'up   ')
        elif CHAR == curses.KEY_DOWN:
            TURRET.move_down()
            SCREEN.addstr(0, 0, 'down ')
finally:
    # shut down cleanly
    curses.nocbreak()
    SCREEN.keypad(0)
    curses.echo()
    curses.endwin()
