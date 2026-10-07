"""Handheld regression check: time a real D-pad press until its selection highlight repaints."""
import ctypes as c
import json
import os
import struct
import time
import urllib.request

x = c.CDLL('libX11.so.6')
x.XOpenDisplay.restype = c.c_void_p
x.XDefaultRootWindow.argtypes = [c.c_void_p]
x.XDefaultRootWindow.restype = c.c_ulong
x.XGetImage.argtypes = [c.c_void_p, c.c_ulong, c.c_int, c.c_int, c.c_uint, c.c_uint, c.c_ulong, c.c_int]
x.XGetImage.restype = c.c_void_p
x.XGetPixel.argtypes = [c.c_void_p, c.c_int, c.c_int]
x.XGetPixel.restype = c.c_ulong
x.XDestroyImage.argtypes = [c.c_void_p]
x.XCloseDisplay.argtypes = [c.c_void_p]
display = x.XOpenDisplay(b':0')
assert display, 'Open Hardware Monitor before measuring'
root = x.XDefaultRootWindow(display)

def state():
    with urllib.request.urlopen('http://127.0.0.1:8766/status', timeout=2) as response:
        return json.load(response)

def pixel(y):
    image = x.XGetImage(display, root, 30, y, 1, 1, c.c_ulong(-1).value, 2)
    assert image
    value = x.XGetPixel(image, 0, 0) & 0xffffff
    x.XDestroyImage(image)
    return value

fd = os.open('/dev/input/event2', os.O_WRONLY)
samples = []
try:
    for _ in range(5):
        s = state()
        assert not s['detail'] and len(s['hosts']) == 3, 'Use the three-host overview'
        index = [h['host'] for h in s['hosts']].index(s['selected'])
        y = [150, 350, 550][index]
        deadline = time.monotonic() + 3
        while pixel(y) != 0xfff1b7:
            assert time.monotonic() < deadline, 'Selection highlight not found'
            time.sleep(.01)
        started = time.monotonic()
        for value in (1, 0):
            os.write(fd, struct.pack('@llHHi', 0, 0, 1, 545, value) + struct.pack('@llHHi', 0, 0, 0, 0, 0))
        while pixel(y) == 0xfff1b7:
            assert time.monotonic() - started < 3, 'Selection did not repaint'
            time.sleep(.01)
        samples.append((time.monotonic() - started) * 1000)
    print('D-pad -> visible highlight, milliseconds:', [round(v) for v in samples], flush=True)
    assert max(samples) < 200, f'Slow selection: {max(samples):.0f} ms (target <200ms)'
finally:
    os.close(fd)
    x.XCloseDisplay(display)
