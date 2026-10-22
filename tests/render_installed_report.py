"""Exercise an installed skin without importing modules from its source checkout."""
from pathlib import Path
import logging
import sys

import weecfg
import weewx
import weewx.manager
import weewx.reportengine
import weewx.station

logging.basicConfig(level=logging.ERROR)
station_root = Path(sys.argv[1])
sys.path.insert(0, str(station_root / 'bin'))
_, config = weecfg.read_config(str(station_root / 'weewx.conf'))
config['Station'].update({'latitude': '40', 'longitude': '-70', 'altitude': ['10', 'meter'],
                          'location': 'Installed test station', 'rain_year_start': 1})
for report_name in config['StdReport'].sections:
    if report_name != 'Defaults':
        config['StdReport'][report_name]['enable'] = report_name == 'Niculskin'
config['StdReport']['HTML_ROOT'] = 'public_html'
config['Databases']['archive_sqlite']['database_name'] = str(station_root / 'weather.sdb')
config['DataBindings']['wx_binding']['schema'] = 'weewx.schemas.wview_extended.schema'
timestamp = 1720000200
with weewx.manager.open_manager_with_config(config, 'wx_binding', initialize=True) as database:
    for i in range(24):
        if database.getRecord(timestamp-(23-i)*300) is not None:
            continue
        database.addRecord({'dateTime': timestamp-(23-i)*300, 'usUnits': weewx.METRICWX,
            'interval': 5, 'outTemp': 12.0, 'outHumidity': 60, 'windSpeed': 0.0,
            'windGust': 0.0, 'windDir': 0.0, 'rain': 0.0, 'rainRate': 0.0,
            'barometer': 1000.0, 'inTemp': 20.0, 'inHumidity': 40.0})
station_info = weewx.station.StationInfo(**config['Station'])
weewx.reportengine.StdReportEngine(config, station_info, gen_ts=timestamp,
                                  first_run=sys.argv[2] == 'first').run()
