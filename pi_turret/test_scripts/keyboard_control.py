"""Module for testing the turret with the keyboard controls"""
import curses
import threading
import time
import queue as Queue
from pi_turret.turret import Turret

UP = "UP"
DOWN = "DOWN"
LEFT = "LEFT"
RIGHT = "RIGHT"
FIRE = "FIRE"

THREAD_STOP = False

def turret_thread(tQueue):
    global THREAD_STOP
    turret = Turret()
    # turret.calibrate()
    while True:
        if THREAD_STOP:
            turret = None
            break
        try:
            command = tQueue.get(block=False, timeout= 0.1)
        except Queue.Empty:
            # Don't peg the CPU
            time.sleep(0.02)
            continue
        if command == UP:
            turret.move_up()
        elif command == DOWN:
            turret.move_down()
        elif command == LEFT:
            turret.move_left()
        elif command == RIGHT:
            turret.move_right()
        elif command == FIRE:
            turret.burst_fire(0.5)
            # turret.blaster.burst_fire(0.5)

def main():
    """Main script to control the turret with the keyboard
    """
    queue = Queue.Queue()
    thread = threading.Thread(target=turret_thread, args=[queue], daemon=True)
    thread.start()

    # get the curses screen window
    screen = curses.initscr()

    # turn off input echoing
    curses.noecho()

    # respond to keys immediately (don't wait for enter)
    curses.cbreak()

    # map arrow keys to special values
    screen.keypad(True)
    global THREAD_STOP
    try:
        while True:
            char = screen.getch()
            if char == ord('q'):
                THREAD_STOP = True
                break
            elif char == curses.KEY_RIGHT:
                # print doesn't work with curses, use addstr instead
                queue.put(RIGHT)
                screen.addstr(0, 0, 'right')
            elif char == curses.KEY_LEFT:
                queue.put(LEFT)
                screen.addstr(0, 0, 'left ')
            elif char == curses.KEY_UP:
                queue.put(UP)
                screen.addstr(0, 0, 'up   ')
            elif char == curses.KEY_DOWN:
                queue.put(DOWN)
                screen.addstr(0, 0, 'down ')
            elif char == ord(' '):
                queue.put(FIRE)
                screen.addstr(0, 0, 'FIRE!')
    finally:
        # shut down cleanly
        curses.nocbreak()
        screen.keypad(0)
        curses.echo()
        curses.endwin()

if __name__ == "__main__":
    main()
