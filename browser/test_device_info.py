"""Run on Linux: python3 browser/test_device_info.py."""
import http.client
import json
import socket
import threading
from device_info import Handler, ThreadingHTTPServer

with ThreadingHTTPServer(('127.0.0.1', 0), Handler) as server:
    worker = threading.Thread(target=server.serve_forever)
    worker.start()
    try:
        # Chromium can open an idle speculative connection before requesting a page.
        with socket.create_connection(server.server_address, timeout=2):
            connection = http.client.HTTPConnection(*server.server_address, timeout=2)
            connection.request('GET', '/status')
            response = connection.getresponse()
            assert response.status == 200
            assert 'Memory used' in json.loads(response.read())
            connection.request('GET', '/missing')
            assert connection.getresponse().status == 404
            connection.close()
    finally:
        server.shutdown()
        worker.join()
print('PASS: status API works while another browser connection is idle')
