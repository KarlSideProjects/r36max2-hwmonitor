"""Run on the handheld with Hardware Monitor open: python3 test_awake.py."""
import re
import subprocess
from pathlib import Path

settings = subprocess.check_output(['xset', 'q'], env=dict(__import__('os').environ, DISPLAY=':0'), text=True)
assert re.search(r'timeout:\s+0\s+cycle:', settings), 'Screen saver timer enabled'
assert 'prefer blanking:  no' in settings, 'Blanking enabled'
assert 'DPMS is Enabled' in settings, 'Manual DPMS unavailable'
assert re.search(r'Standby:\s+0\s+Suspend:\s+0\s+Off:\s+0', settings), 'Automatic DPMS timer enabled'
assert 'Monitor is On' in settings, 'Monitor is manually sleeping'
locks = subprocess.check_output(['systemd-inhibit', '--list', '--no-pager'], text=True)
assert 'HardwareMonitor' in locks and 'sleep' in locks and 'idle' in locks, 'Monitoring sleep/idle inhibitor missing'
backlight = Path('/sys/class/backlight/backlight')
assert int((backlight / 'brightness').read_text()) > 0, 'Backlight is off'
if (backlight / 'bl_power').exists():
    assert int((backlight / 'bl_power').read_text()) == 0, 'Backlight power saving enabled'
print('PASS: no screen saver, no blanking, manual DPMS enabled with all timers zero, sleep/idle inhibited, backlight on')
