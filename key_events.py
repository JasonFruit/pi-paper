from evdev import *

def keyboards():
    """Returns a list of likely keyboards.  Not infallible."""
    
    def dev_if_allowed(fn):
        try:
            return InputDevice(fn)
        except:
            return None
            
    devs = [dev_if_allowed(fn) for fn in list_devices()]
    return [dev for dev in devs if dev and "eybo" in dev.name]

class KeyReader(object):
    """Reads key events in an endless loop, calling the handler for
    each one."""
    def __init__(self, device_fn):
        self._device = InputDevice(device_fn)
    def event_loop(self, handler):
        for event in self._device.read_loop():
            if event.type == ecodes.EV_KEY:
                handler(categorize(event))


class ExclusiveKeyReader(KeyReader):
    """Like a KeyReader object, except grabs the device for exclusive
    access; must be used in a `with` block."""
    def __init__(self, device_fn):
        KeyReader.__init__(self, device_fn)
    def __enter__(self):
        self._device.grab()
        return self
    def __exit__(self, a, b, c):
        self._device.ungrab()

if __name__ == "__main__":
    print(keyboards())
    def handler(event):
        print(event.keycode, event.keystate)
        if event.keycode == "KEY_Z": # Quit if Z is pressed
            exit()
            
    with ExclusiveKeyReader("/dev/input/event6") as kr:
        kr.event_loop(handler)
