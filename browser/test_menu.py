"""Run: python3 browser/test_menu.py."""
import tempfile
from pathlib import Path
import xml.etree.ElementTree as ET
import importlib.util
spec = importlib.util.spec_from_file_location('menu', Path(__file__).with_name('install-menu.py'))
menu = importlib.util.module_from_spec(spec)
spec.loader.exec_module(menu)
with tempfile.TemporaryDirectory() as directory:
    path = Path(directory) / 'gamelist.xml'
    path.write_text('<gameList><game><path>./Device Info.sh</path><playcount>7</playcount></game><game><path>./Hardware Monitor.sh</path><playcount>2</playcount></game></gameList>')
    menu.install(path)
    menu.install(path)
    games = ET.parse(path).getroot().findall('game')
    assert len(games) == 2 and games[0].findtext('playcount') == '7'
    assert games[1].findtext('playcount') == '2'
    assert games[1].findtext('image') == './images/hardware-buddy.png'
print('PASS: menu artwork, existing entries/history preserved, idempotent update')
