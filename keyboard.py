import curses

import pyte

screen = pyte.Screen(80, 24)
stream = pyte.Stream()

stream.attach(screen)

def func(win):
    win = curses.initscr()
    curses.raw(True)

    while True:
        key = win.getch()
        if chr(key) == 'z':
            break
        stream.feed(chr(key))
        print(key)

curses.wrapper(func)

print("\n".join(screen.display))
