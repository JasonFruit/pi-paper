import struct
import serial
from threading import Thread

def get_parity(cmd_part):
    parity = 0
    for c in cmd_part:
        parity = parity ^ c
    return parity

class EPaper(serial.Serial):
    def __init__(self, device, baudrate=115200, timeout=0.1, debug=False):
        serial.Serial.__init__(self, device, baudrate=baudrate, timeout=timeout)
        self.debug = debug
        self.row_spacing = 32
        self.column_spacing = 23
    def transmit_command(self, cmd):
        self.write(cmd)
        if self.debug:
            print(cmd)
            print(self.read(10))
        else:
            try:
                # read from serial in a separate thread so it doesn't
                # get blocked and we don't have to wait
                t = Thread(target=self.read, args=[2,])
                t.start()
            except:
                pass
    def cls(self):
        return self.transmit_command(b"\xA5\x00\x09\x2E\xCC\x33\xC3\x3C\x82")
    def handshake(self):
        return self.transmit_command(b"\xa5\x00\x09\x00\xcc\x33\xc3\x3c\xac")
    def _row_to_pixels(self, row):
        return row * self.row_spacing
    def _column_to_pixels(self, column):
        return column * self.column_spacing
    def _draw_char(self, char, row, column):
        if char != " ":
            self.draw_text_dynamic(char, row, column)
    def _ensure_byte_length(self, data, length):
        return bytes(length - len(data)) + data
    def draw_text_dynamic(self, text, row=0, column=0):
        x, y = self._column_to_pixels(column), self._row_to_pixels(row)
        
        y = struct.pack(">I", y)[2:]
        x = struct.pack(">I", x)[2:]

        length = self._ensure_byte_length(bytes([9 + len(text) + 5,]), 2)

        cmd = b"\xA5" + length + b"\x30" + x + y + bytes(text, "ascii") + b"\x00\xCC\x33\xC3\x3C"
        cmd = cmd + bytes([get_parity(cmd)])

        return self.transmit_command(cmd)

    def draw_screen(self, screen):
        """Draw an array of strings to the screen as fixed-width text"""
        for row in range(len(screen)):
            for col in range(len(screen[row])):
                self._draw_char(screen[row][col], row, col)
        
    
    def finalize(self):
        return self.transmit_command(b"\xA5\x00\x09\x0A\xCC\x33\xC3\x3C\xA6")


if __name__ == "__main__":
    display = EPaper("/dev/ttyS0", debug=False)
    display.handshake()
    display.cls()

    screen = """Dear Anne,

    I hope you and the kids are having
     a good time with your family.  I
    love you very much and hope to see
     you soon.

    HERE IS A ROW IN ALL UPPER-CASE!

                        Love,

                        Jason""".split("\n")

    display.draw_screen(screen)
    display.finalize()
