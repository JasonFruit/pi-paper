import os
import pty
from threading import Thread
import time
import pyte

from key_events import ExclusiveKeyReader
from keys import KeyHandler
import epd, pervasive
from PIL import Image, ImageFont, ImageDraw

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
                 rows=24,
                 cols=80,
                 debug=False):
        
        ExclusiveKeyReader.__init__(self, keyboard)
        
        # set up an in-memory screen and its communication stream
        self.screen = pyte.Screen(cols, rows)
        self.stream = pyte.Stream()
        self.stream.attach(self.screen)

        self.display = pervasive.PervasiveDisplay()
        self.converter = epd.ImageConverter()
        
        self.debug = debug

        # not convinced this works.  TODO: test this
        os.environ["COLUMNS"] = "%s" % cols
        os.environ["LINES"] = "%s" % rows
        

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

        draw_num = 0

        os.system("rm screens/*")
        
        while True:
            s = self.screen.display
            
            # if the display or cursor position has changed, redraw
            if (("\n".join(s) != prev_screen) or
                (prev_x != self.screen.cursor.x) or
                (prev_y != self.screen.cursor.y)):

                image = Image.new("1", (800, 480), 1)
                font = ImageFont.truetype("fonts/RobotoMono-Regular.ttf", size=15)
                drawer = ImageDraw.Draw(image)
                
                for row_ind in range(len(s)):
                    drawer.text((14, 18 * row_ind), s[row_ind], font=font)

                # image.save("screens/screen-%s.png" % draw_num)
                # draw_num += 1

                image = image.rotate(270)
                
                epd_data = self.converter.convert(image)
                self.display.reset_data_pointer()
                self.display.send_image(epd_data)
                self.display.update_display()
                
                prev_screen = "\n".join(s)
                prev_x, prev_y = (self.screen.cursor.x,
                                  self.screen.cursor.y)
            time.sleep(2) # only check every couple seconds; this is
                          # not a fast-updating display

    def _subterm(self, rows, columns, rows_above_cursor=1, columns_before_cursor=5):
        screen = self.screen.display
        x, y = (self.screen.cursor.x,
                self.screen.cursor.y)
        subscreen = screen[
            self.screen.cursor.y - rows_above_cursor:
            self.screen.cursor.y - rows_above_cursor + rows]
        for row_index in range(len(subscreen)):
            subscreen[row_index] = subscreen[row_index][
                self.screen.cursor.x - columns_before_cursor,
                self.screen.cursor.x - columns_before_cursor, + columns]

        return subscreen
            
                           
            
    def start(self):
        """Start driving the terminal emulator and display."""

        # bash will run in a separate thread
        child_pid, self.bash_fd = pty.fork()

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
                os.write(self.bash_fd, bytes(chr(asc), "utf-8"))

            key_handler = KeyHandler(self, feed_fn)
            key_handler.run() # loops until program end
            
if __name__ == "__main__":
    with PaperTerm("/dev/input/event0", "/dev/ttyS0") as term:
        term.start()
