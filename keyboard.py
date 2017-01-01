import os
import pty
import pyte
from threading import Thread

from key_events import ExclusiveKeyReader
from keys import KeyHandler

screen = pyte.Screen(80, 24)
stream = pyte.Stream()

stream.attach(screen)

child_pid, fd = pty.fork()

if child_pid == 0:
    os.execlp("/bin/bash", "PaperTerminal", "-i")
else:
    def read_bash():
        while True:
            try:
                out = os.read(fd, 4096)
                stream.feed(out.decode("utf-8"))
            except OSError:
                break

    bash_thread = Thread(target=read_bash)
    bash_thread.daemon = True
    bash_thread.start()

    def displayer():
        prev_screen = ""
        while True:
            s = "\n".join(screen.display)
            if s != prev_screen:
                print("\n"*100)
                print(s)
                prev_screen = s

    display_thread = Thread(target=displayer)
    display_thread.daemon = True
    display_thread.start()
    
    def feed_fn(asc):
        os.write(fd, bytes(chr(asc), "utf-8"))

    with ExclusiveKeyReader("/dev/input/event1") as key_reader:
        key_handler = KeyHandler(key_reader, feed_fn)
        key_handler.run()
