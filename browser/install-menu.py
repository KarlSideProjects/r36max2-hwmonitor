"""Add the Hardware Monitor artwork without changing other Ports entries."""
from pathlib import Path
import xml.etree.ElementTree as ET


def install(path):
    path = Path(path)
    tree = ET.parse(path) if path.exists() else ET.ElementTree(ET.Element('gameList'))
    root = tree.getroot()
    game = next((game for game in root.findall('game')
                 if game.findtext('path') == './Hardware Monitor.sh'), None)
    if game is None:
        game = ET.SubElement(root, 'game')
        ET.SubElement(game, 'path').text = './Hardware Monitor.sh'
    for tag, text in {'name': 'Hardware Monitor',
                      'desc': 'Meet your computer buddies! Live CPU, GPU, VRAM, memory, network and disk monitoring. A: details. B: overview. Select + B: exit.',
                      'image': './images/hardware-buddy.png',
                      'thumbnail': './images/hardware-buddy.png'}.items():
        element = game.find(tag)
        if element is None:
            element = ET.SubElement(game, tag)
        element.text = text
    temporary = path.with_suffix('.xml.tmp')
    ET.indent(tree, space='  ')
    tree.write(temporary, encoding='utf-8', xml_declaration=True)
    temporary.replace(path)


if __name__ == '__main__':
    install('/roms/ports/gamelist.xml')
