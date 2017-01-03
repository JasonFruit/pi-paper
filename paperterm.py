import os
import pty
from threading import Thread
import time
import pyte

from key_events import ExclusiveKeyReader
from keys import KeyHandler
from epaper import EPaper

class PaperTerm(ExclusiveKeyReader):
    def __init__(self, keyboard, display_tty, rows=18, cols=34, debug=False):
        self.fd = None

        ExclusiveKeyReader.__init__(self, keyboard)
        
        # set up an in-memory screen and its communication stream
        self.screen = pyte.Screen(cols, rows)
        self.stream = pyte.Stream()
        self.stream.attach(self.screen)

        self.debug = debug

        os.environ["COLUMNS"] = "34"
        os.environ["LINES"] = "18"

        self.paper = EPaper(display_tty, debug=self.debug)
        

    def _read_bash(self):
        while True:
            try:
                out = os.read(self.bash_fd, 4096)
                self.stream.feed(out.decode("utf-8"))
            except OSError:
                break # if there's nothing to read, kill the reader
                      # thread

    def _write_display(self):
        prev_screen = ""
        prev_x, prev_y = 100, 100 # off the screen

        while True:
            s = self.screen.display

            if (("\n".join(s) != prev_screen) or
                (prev_x != self.screen.cursor.x) or
                (prev_y != self.screen.cursor.y)):

                self.paper.cls()
                self.paper.draw_screen(s)
                self.paper.draw_cursor(self.screen.cursor.y,
                                       self.screen.cursor.x)
                paper.finalize()
                prev_screen = "\n".join(s)
                prev_x, prev_y = (self.screen.cursor.x,
                                  self.screen.cursor.y)
            time.sleep(2)
            
    def start(self):

        child_pid, self.fd = pty.fork()

        if child_pid == 0:
            os.execlp("/bin/bash", "PaperTerminal", "-i")
        else:
            self.bash_thread = Thread(target=self._read_bash)
            self.bash_thread.daemon = True
            self.bash_thread.start()

            self.display_thread = Thread(target=self._write_display)
            self.display_thread.daemon = True
            self.display_thread.start()

            def feed_fn(asc):
                os.write(self.fd, bytes(chr(asc), "utf-8"))

            key_handler = KeyHandler(self, feed_fn)
            key_handler.run()
            
if __name__ == "__main__":
    with PaperTerm("/dev/input/event1", "/dev/ttyS0") as term:
        term.start()
    
    
