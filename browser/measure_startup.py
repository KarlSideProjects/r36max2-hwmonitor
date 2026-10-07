"""Run on the handheld while a dashboard is open; detects Xorg/client startup stalls."""
import os
from pathlib import Path

ticks = os.sysconf('SC_CLK_TCK')
servers, clients = [], []
for path in Path('/proc').glob('[0-9]*/cmdline'):
    try:
        args = path.read_bytes().split(b'\0')
        if not args or not args[0]:
            continue
        stat = (path.parent / 'stat').read_text()
        started = int(stat[stat.rindex(')') + 2:].split()[19]) / ticks
        if args[0] == b'/usr/lib/xorg/Xorg':
            servers.append(started)
        if args[:2] == [b'python3', b'monitor.py']:
            clients.append(started)
    except (OSError, ValueError):
        continue
assert servers and clients, 'Open Hardware Monitor before measuring'
delay = max(clients) - max(servers)
print(f'Xorg process -> dashboard process: {delay:.2f} seconds', flush=True)
assert 0 <= delay < 2, f'Startup stall: {delay:.2f}s (target <2s)'
