# Installer for the independent Niculskin continuation.
# Modified 2026-10-22: WeeWX 5 installer and complete local asset manifest.
import os

from weecfg.extension import ExtensionInstaller


def loader():
    return NiculskinInstaller()


class NiculskinInstaller(ExtensionInstaller):
    def __init__(self):
        files = []
        root = os.path.dirname(os.path.abspath(__file__))
        for directory, dirs, names in os.walk(os.path.join(root, 'skins')):
            relative = os.path.relpath(directory, root)
            paths = [os.path.join(relative, name) for name in sorted(names)]
            if paths:
                files.append((relative, paths))
        files.append(('bin/user', ['bin/user/historygenerator.py', 'bin/user/translategenerator.py']))
        super(NiculskinInstaller, self).__init__(
            version='1.1.0',
            name='niculskin',
            description='Responsive skin with translated labels and history tables.',
            author='Nico Gulden',
            author_email='ngulden@gmx.de',
            config={'StdReport': {'Niculskin': {'skin': 'niculskin', 'enable': True}}},
            files=files)
