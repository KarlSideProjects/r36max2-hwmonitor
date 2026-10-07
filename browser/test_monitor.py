"""Run: python3 browser/test_monitor.py."""
import json
import time
from monitor import Monitor, normalize

now = time.monotonic()
payload = {'cpu': {'percent_total': 42, 'percent_per_core': [25, 59]},
           'memory': {'ram': {'percent': 63, 'used': 8 * 2**30, 'total': 16 * 2**30}},
           'gpus': [{'usage_percent': 37, 'temperature_celsius': 62}],
           'temperatures': {'coretemp': [{'current': 55}]},
           'network_io': {'total': {'rate': {'rx_bytes_per_s': 1000, 'tx_bytes_per_s': 500}}},
           'disk_io': {'sda': {'rate': {'read_bytes_per_s': 2000, 'write_bytes_per_s': 750}}}}

def publish(state, host, timestamp):
    return state.receive(f'sys/agents/{host}/metrics', json.dumps(dict(payload, host=host)), now=timestamp)

state = Monitor()
for i in range(7):
    assert publish(state, f'host-{i}', now)
assert state.snapshot()['count'] == 7
assert len(state.snapshot()['hosts']) == 3
state.action('next', now)
assert state.selected == 'host-3' and state.paused
state.action('down', now)
state.action('detail', now)
assert state.detail == 'host-4'
state.action('down', now)
assert state.scroll == 0 and state.detail == 'host-4'
state.action('back', now)
assert state.detail is None and state.paused
state.action('next', now)
assert state.selected == 'host-6' and len(state.snapshot()['hosts']) == 1
# Fresh messages do not resume a manual pause, even beyond the auto interval.
for i in range(7):
    publish(state, f'host-{i}', now + 8)
state.tick(now + 16)
assert state.selected == 'host-6' and state.paused
state.action('toggle', now + 16)
for i in range(7):
    publish(state, f'host-{i}', now + 16)
for i in range(7):
    publish(state, f'host-{i}', now + 24)
for i in range(7):
    publish(state, f'host-{i}', now + 30)
state.tick(now + 31)
assert state.selected == 'host-0' and not state.paused
state.action('detail', now + 31)
publish(state, 'host-1', now + 39)
state.tick(now + 40)
assert state.detail is None and state.selected == 'host-1' and state.paused
state.tick(now + 49)
assert not state.hosts and state.selected is None
assert not state.receive('topic', b'[]', now=now)
assert not state.receive('topic', b'{bad', now=now)
assert not state.receive('topic', b'{"host":null}', now=now)
assert not state.receive('topic', json.dumps(dict(payload, host='stale', ts=time.time()-60)), retained=True)
assert normalize(payload)['cpu_temp'] == 55
assert normalize(payload)['gpu'] == 37
assert normalize(payload)['read'] == 2000
assert normalize({'gpu': None, 'cpu': []})['cpu'] is None
# Raw host names remain data; the web page escapes text before inserting HTML.
assert publish(state, '<script>bad</script>', now)
json.dumps(state.snapshot(), allow_nan=False)
print('PASS: 7-host pagination, pause/resume, auto rotation, detail/offline, payload validation')

# Three-level navigation, direct clicks, card switching, and offline fallback.
state = Monitor()
publish(state, 'drilldown', time.monotonic())
state.action('detail')
assert state.snapshot()['panel'] == 'cpu' and state.focus is None
state.action('detail')
assert state.focus == 'cpu'
state.action('next')
assert state.focus == 'gpu'
state.action('back')
assert state.detail == 'drilldown' and state.focus is None
state.action('down')
assert state.snapshot()['panel'] == 'memory' and state.scroll == 0
state.action('detail')
assert state.focus == 'memory'
state.action('back')
state.action('focus:network')
assert state.focus == 'network'
state.tick(time.monotonic() + 10)
assert state.detail is None and state.focus is None
print('PASS: overview/device/metric navigation, click actions, metric switching, offline fallback')
