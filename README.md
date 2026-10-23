# Niculskin

Niculskin is a skin for [WeeWX](https://weewx.com/) with translated weather
pages, image plots and colour-coded history tables. It is based on
[Sofaskin for Weewx](http://neoground.com/projects/weewx/) and the
[Bootstrap skin for Weewx](https://github.com/brewster76/fuzzy-archer/).

This repository is an independent continuation of
[ngulden/niculskin](https://gitlab.com/ngulden/niculskin), started from
d9741244a2a42321d3e0f5802bfeeb2952156ffb with the full upstream history.

![screenshot_1.png](screenshot_1.png)

![screenshot_2.png](screenshot_2.png)

## Requirements

The skin uses WeeWX's Cheetah, image and copy generators. It needs no
additional Python package.

The image plots use Droid Sans at
`/usr/share/fonts/truetype/droid/DroidSans-Bold.ttf`. Install that font or set
the `*_font_path` options in `[ImageGenerator]` of `skin.conf` to a font on
your machine. Otherwise the plots use Pillow's default font.

## Installation

Install `niculskin` from the [WeeWX packages catalog](https://github.com/weewx-packages/catalog/blob/main/packages/niculskin.md).
The catalog page lists the current release, its WeeWX and Python
requirements, and the install, update and removal commands.

The installer copies the skin to `skins/niculskin`, the language files to
`skins/languages` and the modules `user.historygenerator` and
`user.translategenerator`. It adds a separate report next to your existing
reports:

```ini
[StdReport]
    [[Niculskin]]
        skin = niculskin
        enable = true
```

The installer does not set `HTML_ROOT` for this report. Without it, Niculskin
writes into the `[StdReport]` `HTML_ROOT`, where the Seasons report also
writes `index.html` and other pages. Give the report its own directory that
your web server serves, for example:

```ini
[StdReport]
    [[Niculskin]]
        skin = niculskin
        enable = true
        HTML_ROOT = /var/www/html/weewx/niculskin
```

Restart WeeWX. Then wait for an archive interval or run
`weectl report run Niculskin`. Back up custom skin files before an update.

## Configuration

The skin is configured in the installed `skins/niculskin/skin.conf`
([source](skins/niculskin/skin.conf)).

### Choose the language

```ini
[Language]
    language = german
```

`language` names a file in the `languages` directory of your skins directory,
without `.conf`. The skin ships `dutch`, `espanol`, `finnish`, `francais`,
`german` and `italian`. The default is `german`. Set `english` to use the
labels in `skin.conf` without a language file. If the file cannot be read,
WeeWX logs a warning and uses the labels in `skin.conf`.

### Change the labels

The page labels are in `[niculskinLabels]` of `skin.conf`, for example:

```ini
[niculskinLabels]
    title = "Current Weather Conditions"
    location_ref_label = "Show on map"
    footer = "&copy; 2016 by Nico Gulden"
```

A language file overrides any label it contains. With `language = german`,
`title` and `location_ref_label` come from `german.conf`, while `footer` comes
from `skin.conf`. Change a label in the language file you use, or in
`skin.conf` for `english`.

To add a language, copy one of the language files, translate the labels and
set `language` to the new file name. Contributions of language files are
welcome, see the [Contribution Guideline](CONTRIBUTING.md).

### Show radar and lightning images

The `[Extras]` section of `skin.conf` holds optional links and images for the
front page: `radar_img`, `radar_gif`, `radar_url`, `radar_url_alt`,
`radar_url_alt_text`, `lightning_map` and `lightning_url`. All except
`radar_url` are commented out. Uncomment and adjust them for your region.

### Colour the history tables

`[HistoryReport]` in `skin.conf` sets the value ranges and colours of the
monthly and yearly history tables, and `refresh_interval` in minutes sets how
often they are recalculated. The comments in that section describe each
option.

## Limitations

* The pages load the Lato font from `http://fonts.googleapis.com`. Browsers
  block this plain-HTTP request on pages served over HTTPS, and the page then
  uses a fallback font. Bootstrap, Font Awesome and its webfonts are bundled
  and copied to the report output. No Bootstrap JavaScript is used.
* The skin installs the shared module `user.historygenerator`. Another skin
  with a module of the same name, such as NeoWX Material, can replace it.
  Review that overlap before installing both into the same station.
* The tests use an isolated SQLite archive. Physical station readings and the
  external radar links are not tested.

## Development

Run the tests with WeeWX and pytest installed. The installed-archive test
calls the `weectl` next to the Python interpreter:

```sh
python -m pytest -q tests
```

The tests render the HTML templates in German and English. The installed-
archive test installs the skin into a new station, runs the report twice and
checks that stylesheets, CSS font references and license files exist in the
public output.

See the [Contribution Guideline](CONTRIBUTING.md) for issues and changes.

## License

Niculskin (c) 2016-2020 Nico Gulden. `skin.conf` also carries the notices of
Tom Keffer (2010) and Sven Reifschneider (Sofaskin, 2015). The generator
modules are (c) 2013-2016 and 2015 Nick Dajda. Distributed under the GNU
General Public License version 2. See [LICENSE](LICENSE).

The bundled Bootstrap, Font Awesome, Modernizr and normalize.css files keep
their own licenses, which are in
[`skins/niculskin/licenses`](skins/niculskin/licenses) and are copied to the
report output.

### Credits

Thanks to Sven Reifschneider, the creator of Sofaskin. I liked his skin most as I was looking for something different in the look and feel of weewx.

And thanks to Nick Dajda. He had the history for the weather data. I'm glad I found his code.
