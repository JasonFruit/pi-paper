import struct
import serial

def get_parity(cmd_part):
    parity = 0
    for c in cmd_part:
        parity = parity ^ c
    return parity

class EPaper(serial.Serial):
    def __init__(self, device, baudrate=115200, timeout=0.1):
        serial.Serial.__init__(self, device, baudrate=baudrate, timeout=timeout)
    def transmit_command(self, cmd):
        self.write(cmd)
        return self.read(10)
    def cls(self):
        return self.transmit_command(b"\xA5\x00\x09\x2E\xCC\x33\xC3\x3C\x82")
    def handshake(self):
        return self.transmit_command(b"\xa5\x00\x09\x00\xcc\x33\xc3\x3c\xac")
    def draw_text_dynamic(self, text, line=0, column=0):
        y = struct.pack(">I", line * 32)[2:]
        x = struct.pack(">I", column * 28)[2:]

        length = bytes([9 + len(text) + 5,])
        if len(length) == 1:
            length = bytes([0,]) + length

        cmd = b"\xA5" + length + b"\x30" + x + y + bytes(text, "ascii") + b"\x00\xCC\x33\xC3\x3C"
        cmd = cmd + bytes([get_parity(cmd)])

        return self.transmit_command(cmd)
    def finalize(self):
        return self.transmit_command(b"\xA5\x00\x09\x0A\xCC\x33\xC3\x3C\xA6")

display = EPaper("/dev/ttyS0")
print(display.handshake())
print(display.cls())
print(display.draw_text_dynamic("Dear Anne,", 1, 1))
print(display.draw_text_dynamic("Do you know that I love you very much?  I do!", 3, 1))
print(display.draw_text_dynamic("I hope that you and the kids managed to have a good time", 5, 1))
print(display.draw_text_dynamic("despite everything", 6, 1))
print(display.draw_text_dynamic("Love,", 8, 14))
print(display.draw_text_dynamic("Jason", 10, 14))
print(display.finalize())
