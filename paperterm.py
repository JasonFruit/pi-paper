import os
import pty
from threading import Thread
import time
import pyte

from key_events import ExclusiveKeyReader
from keys import KeyHandler
from epaper import EPaper

class PaperTerm(ExclusiveKeyReader):
    """Runs an in-memory instance of bash, communicating with an in-memory
    VT102 emulator, whose output is mirrored on an e-paper screen.  If
    debug==True, the responses to serial requests will be waited for
    and printed to the initiating terminal, slowing display
    considerably..

    """
    def __init__(self,
                 keyboard,
                 display_tty,
                 rows=18,
                 cols=34,
                 debug=False):
        
        ExclusiveKeyReader.__init__(self, keyboard)
        
        # set up an in-memory screen and its communication stream
        self.screen = pyte.Screen(cols, rows)
        self.stream = pyte.Stream()
        self.stream.attach(self.screen)

        self.debug = debug

        # not convinced this works.  TODO: test this
        os.environ["COLUMNS"] = "34"
        os.environ["LINES"] = "18"

        self.paper = EPaper(display_tty, debug=self.debug)
        

    def _read_bash(self):
        """To be run in a separate thread, reading from the Bash process and
        feeding the VT102 emulator.

        """
        while True:
            try:
                out = os.read(self.bash_fd, 4096)
                self.stream.feed(out.decode("utf-8"))
            except OSError:
                break # if there's nothing to read, kill the reader
                      # thread

    def _write_display(self):
        """To be run in a separate thread, reading from the VT102 emulator and
        feeding the serial e-paper display.

        """

        # previous values, allowing us to wait for change before
        # displaying
        prev_screen = ""
        prev_x, prev_y = 100, 100 # off the screen

        while True:
            s = self.screen.display

            # if the display or cursor position has changed, redraw
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
            time.sleep(2) # only check every couple seconds; this is
                          # not a fast-updating display
            
    def start(self):
        """Start driving the terminal emulator and display."""

        # bash will run in a separate thread
        child_pid, self.fd = pty.fork()

        if child_pid == 0:
            #if we're in the child thread, start bash
            os.execlp("/bin/bash", "PaperTerm", "-i")
            
        else:

            # otherwise, start reading from bash,
            self.bash_thread = Thread(target=self._read_bash)
            self.bash_thread.daemon = True # die if main thread ends
            self.bash_thread.start()

            # writing to the display, 
            self.display_thread = Thread(target=self._write_display)
            self.display_thread.daemon = True # die with main thread
            self.display_thread.start()

            # and reading from the keyboard
            def feed_fn(asc):
                os.write(self.fd, bytes(chr(asc), "utf-8"))

            key_handler = KeyHandler(self, feed_fn)
            key_handler.run() # loops until program end
            
if __name__ == "__main__":
    with PaperTerm("/dev/input/event1", "/dev/ttyS0") as term:
        term.start()
    
    
