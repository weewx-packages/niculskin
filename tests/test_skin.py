import importlib
from pathlib import Path
import re
import shutil
import os
import subprocess
import zipfile
import sys

import configobj
import pytest
import weewx
import weewx.manager
import weewx.reportengine
import weewx.station

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / 'bin'))


@pytest.mark.parametrize('language,heading,unit', [('german', 'Aktuelle Bedingungen', ' Tag'),
                                                  ('english', 'Current Conditions', ' Day')])
def test_actual_report_and_formatter(tmp_path, language, heading, unit):
    shutil.copytree(ROOT / 'skins', tmp_path / 'skins')
    skin_path = tmp_path / 'skins/niculskin/skin.conf'
    skin = configobj.ConfigObj(str(skin_path), encoding='utf-8')
    skin['Language']['language'] = language
    skin['Generators']['generator_list'] = ['user.translategenerator.CheetahGeneratorTranslated',
                                           'weewx.reportengine.CopyGenerator']
    skin.write()
    config = configobj.ConfigObj({
        'WEEWX_ROOT': str(tmp_path),
        'Station': {'latitude': '40', 'longitude': '-70', 'altitude': ['10', 'meter'],
                    'location': 'Test station', 'rain_year_start': 1},
        'StdReport': {'SKIN_ROOT': 'skins', 'HTML_ROOT': 'html', 'data_binding': 'wx_binding',
                      'Niculskin': {'skin': 'niculskin', 'enable': True}},
        'DataBindings': {'wx_binding': {'database': 'archive', 'table_name': 'archive',
                         'manager': 'weewx.manager.DaySummaryManager',
                         'schema': 'weewx.schemas.wview_extended.schema'}},
        'Databases': {'archive': {'database_name': str(tmp_path / 'weather.sdb'), 'driver': 'weedb.sqlite'}}})
    timestamp = 1720000200
    with weewx.manager.open_manager_with_config(config, 'wx_binding', initialize=True) as database:
        for i in range(24):
            database.addRecord({'dateTime': timestamp-(23-i)*300, 'usUnits': weewx.METRICWX,
                'interval': 5, 'outTemp': 12.0, 'outHumidity': 60, 'windSpeed': 0.0,
                'windGust': 0.0, 'windDir': 0.0, 'rain': 0.0, 'rainRate': 0.0,
                'barometer': 1000.0, 'inTemp': 20.0, 'inHumidity': 40.0})
    station = weewx.station.StationInfo(**config['Station'])
    translation = importlib.import_module('user.translategenerator')
    skin_dict = weewx.reportengine.build_skin_dict(config, 'Niculskin')
    generator = translation.CheetahGeneratorTranslated(config, skin_dict, timestamp, True, station)
    assert generator.formatter.unit_label_dict['day'][0] == unit
    generator.finalize()
    weewx.reportengine.StdReportEngine(config, station, gen_ts=timestamp).run()
    for name in ['index.html', 'week.html', 'month.html', 'year.html', 'history.html']:
        text = (tmp_path / 'html' / name).read_text()
        assert 'Test station' in text
        assert 'maxcdn.bootstrapcdn.com' not in text
        assert 'fonts.googleapis.com' not in text
        if name == 'index.html':
            assert heading in text
            assert ('Almanach' if language == 'german' else 'Almanac') in text


def test_local_css_dependencies_exist():
    skin = ROOT / 'skins/niculskin'
    for css in (skin / 'css').glob('*.css'):
        for url in re.findall(r'url\([\'\"]?([^\)\'\"]+)', css.read_text()):
            if url.startswith(('http:', 'https:', 'data:')):
                continue
            assert (css.parent / url.split('#')[0].split('?')[0]).exists(), (css, url)


def test_language_files_have_no_replacement_characters():
    for path in (ROOT / 'skins/languages').glob('*.conf'):
        assert '\ufffd' not in path.read_text(encoding='utf-8'), path


def test_installed_archive_publishes_dependencies_and_notices(tmp_path):
    archive = tmp_path / 'niculskin-test.zip'
    with zipfile.ZipFile(archive, 'w') as package:
        for name in ['install.py', 'LICENSE']:
            package.write(ROOT / name, 'niculskin/' + name)
        for directory in ['skins', 'bin']:
            for path in (ROOT / directory).rglob('*'):
                if path.is_file() and '__pycache__' not in path.parts:
                    package.write(path, 'niculskin/' + path.relative_to(ROOT).as_posix())
    station = tmp_path / 'station'
    weectl = str(Path(sys.executable).parent / 'weectl')
    for command in [[weectl, 'station', 'create', str(station), '--no-prompt', '--register=n'],
                    [weectl, 'extension', 'install', str(archive), '--config',
                     str(station / 'weewx.conf'), '--yes']]:
        completed = subprocess.run(command, capture_output=True, text=True)
        assert completed.returncode == 0, completed.stdout + completed.stderr
    installed = configobj.ConfigObj(str(station / 'weewx.conf'), encoding='utf-8')
    assert installed['StdReport']['Niculskin']['HTML_ROOT'] == 'public_html/niculskin'
    public = station / 'public_html/niculskin'
    helper = ROOT / 'tests/render_installed_report.py'
    environment = dict(os.environ, PYTHONPATH=str(station / 'bin'))
    for first_run in ['first', 'upgrade']:
        if first_run == 'upgrade':
            for path in [public / 'css/bootstrap.min.css', public / 'css/font-awesome.min.css',
                         public / 'css/v4-shims.min.css']:
                path.write_text('old installed dependency')
            shutil.rmtree(public / 'webfonts')
            shutil.rmtree(public / 'licenses')
        completed = subprocess.run([sys.executable, str(helper), str(station), first_run],
                                   cwd=tmp_path, env=environment, capture_output=True, text=True)
        assert completed.returncode == 0, completed.stdout + completed.stderr
        assert 'ERROR' not in completed.stderr, completed.stderr
        for name in ['index.html', 'week.html', 'month.html', 'year.html', 'history.html']:
            text = (public / name).read_text()
            assert 'Installed test station' in text
            for asset in re.findall(r'(?:href|src)="((?:css|js)/[^"?#]+)', text):
                assert (public / asset).is_file(), (name, asset)
        for css in (public / 'css').glob('*.css'):
            assert css.read_text() != 'old installed dependency'
            for url in re.findall(r'url\([\'\"]?([^\)\'\"]+)', css.read_text()):
                if not url.startswith(('http:', 'https:', 'data:')):
                    assert (css.parent / url.split('#')[0].split('?')[0]).is_file(), (css, url)
        skin = station / 'skins/niculskin'
        for directory, pattern in [('webfonts', '*'), ('licenses', '*'), ('css', 'LICENSE*')]:
            sources = list((skin / directory).glob(pattern))
            assert sources
            for source in sources:
                assert (public / source.relative_to(skin)).read_bytes() == source.read_bytes()
        assert 'Nicolas Gallagher and Jonathan Neal' in (public / 'licenses/normalize.css-1.1.3-MIT.txt').read_text()
        assert 'Faruk Ates, Paul Irish, Alex Sexton' in (public / 'licenses/modernizr-2.6.2-MIT.txt').read_text()
        assert 'Permission is hereby granted' in (public / 'licenses/modernizr-2.6.2-MIT.txt').read_text()
        assert (public / 'daytempdew.png').is_file()
