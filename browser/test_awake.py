"""Run on the handheld with Hardware Monitor open: python3 test_awake.py."""
import re
import subprocess
from pathlib import Path

settings = subprocess.check_output(['xset', 'q'], env=dict(__import__('os').environ, DISPLAY=':0'), text=True)
assert re.search(r'timeout:\s+0\s+cycle:', settings), 'Screen saver timer enabled'
assert 'prefer blanking:  no' in settings, 'Blanking enabled'
assert 'DPMS is Disabled' in settings, 'Display power saving enabled'
locks = subprocess.check_output(['systemd-inhibit', '--list', '--no-pager'], text=True)
assert 'HardwareMonitor' in locks and 'sleep' in locks and 'idle' in locks, 'Monitoring sleep/idle inhibitor missing'
backlight = Path('/sys/class/backlight/backlight')
assert int((backlight / 'brightness').read_text()) > 0, 'Backlight is off'
if (backlight / 'bl_power').exists():
    assert int((backlight / 'bl_power').read_text()) == 0, 'Backlight power saving enabled'
print('PASS: no screen saver, no blanking, DPMS disabled, sleep/idle inhibited, backlight on')
