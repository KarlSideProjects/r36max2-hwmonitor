#!/usr/bin/env python3
"""Local handheld status page; Select+B closes the browser session."""
import glob
import json
import os
import platform
import select
import socket
import struct
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PAGE = b'''<!doctype html><html><meta charset="utf-8"><title>R36 MAX 2 Device Info</title>
<style>body{margin:0;background:#101820;color:#edf4fa;font:24px sans-serif;padding:40px}h1{font-size:38px;margin:0 0 12px}p{color:#9bafbd}main{display:grid;grid-template-columns:1fr 1fr;gap:18px}article{background:#20303e;border-radius:12px;padding:20px}small{display:block;color:#9bafbd;margin-bottom:10px}strong{font-size:27px}footer{margin-top:24px;color:#9bafbd}</style>
<h1>R36 MAX 2</h1><p>Live device information | 1024 x 768</p><main id="cards"></main>
<footer>Select + B: return to game menu <span id="status"></span></footer>
<script>async function update(){try{let r=await fetch('/status');if(!r.ok)throw Error(r.status);let data=await r.json();let root=document.getElementById('cards');root.replaceChildren();for(let [label,value] of Object.entries(data)){let card=document.createElement('article'),k=document.createElement('small'),v=document.createElement('strong');k.textContent=label;v.textContent=value;card.append(k,v);root.append(card)}document.getElementById('status').textContent=' | Updated '+new Date().toLocaleTimeString()}catch(e){document.getElementById('status').textContent=' | Connection unavailable'}}update();setInterval(update,2000)</script></html>'''


def status():
    memory = {k: int(v.split()[0]) for k, v in
              (line.split(':', 1) for line in Path('/proc/meminfo').read_text().splitlines())}
    disk = os.statvfs('/')
    temperatures = glob.glob('/sys/class/thermal/thermal_zone*/temp')
    temp = f'{int(Path(temperatures[0]).read_text()) / 1000:.1f} C' if temperatures else 'Unavailable'
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        try:
            sock.connect(('192.168.5.1', 9))
            ip = sock.getsockname()[0]
        except OSError:
            ip = 'Offline'
    battery = glob.glob('/sys/class/power_supply/*/capacity')
    return {'System': 'dArkOS / Debian 13', 'Kernel': platform.release(),
            'CPU load (1 min)': f'{os.getloadavg()[0]:.2f}', 'Temperature': temp,
            'Memory used': f"{(memory['MemTotal'] - memory['MemAvailable']) / 1024:.0f} / {memory['MemTotal'] / 1024:.0f} MiB",
            'Storage free': f'{disk.f_bavail * disk.f_frsize / 2**30:.2f} GiB',
            'IP address': ip,
            'Battery': Path(battery[0]).read_text().strip() + '%' if battery else 'Unavailable'}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ('/', '/status'):
            self.send_error(404)
            return
        content = PAGE if self.path == '/' else json.dumps(status()).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8' if self.path == '/' else 'application/json')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, *_):
        pass


def exit_buttons(server):
    # GO-Super Gamepad's SDL back:b12 is Linux code 704; b:b0 is code 304.
    device = '/dev/input/by-path/platform-odroidgo3-joypad-event-joystick'
    event = struct.Struct('@llHHi')
    pressed = set()
    try:
        with open(device, 'rb', buffering=0) as stream:
            while True:
                select.select([stream], [], [])
                raw = stream.read(event.size)
                if len(raw) != event.size:
                    break
                _, _, kind, code, value = event.unpack(raw)
                if kind == 1:
                    if value:
                        pressed.add(code)
                    else:
                        pressed.discard(code)
                    if {704, 304} <= pressed:
                        server.shutdown()
                        return
    except OSError as error:
        print(f'Exit buttons unavailable: {error}', flush=True)


if __name__ == '__main__':
    import sys
    if '--check' in sys.argv:
        data = status()
        assert len(data) == 8 and 'MiB' in data['Memory used']
        assert struct.calcsize('@llHHi') == 24
        print(json.dumps(data))
    else:
        with ThreadingHTTPServer(('127.0.0.1', 8765), Handler) as server:
            threading.Thread(target=exit_buttons, args=(server,), daemon=True).start()
            server.serve_forever()
