import importlib
import json
from pathlib import Path
import re
import shutil
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
