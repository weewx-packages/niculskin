# Niculskin

Niculskin provides translated weather pages, image plots and history tables as a skin for the [weewx project](http://weewx.com/). It is based on two other skins:

1. [Sofaskin for Weewx](http://neoground.com/projects/weewx/)
1. [Bootstrap skin for Weewx](https://github.com/brewster76/fuzzy-archer/)

## Independent continuation

This repository continues [ngulden/niculskin](https://gitlab.com/ngulden/niculskin)
from d9741244a2a42321d3e0f5802bfeeb2952156ffb. It retains the full upstream
history and GPLv2 license and is maintained separately.

Version 1.1.0 applies translations before WeeWX constructs unit formatters.
The additional English and German strings from upstream MR !10 are included
with their original commit history. Bootstrap 5.3.8 and Font Awesome Free 7.3.1
are bundled locally, including Font Awesome's v4 compatibility styles and fonts.
Version 1.1.1 copies these files to the public report output on every run,
including upgrades from 1.1.0. Complete Modernizr 2.6.2 and normalize.css 1.1.3
notices accompany the original JavaScript and CSS. Their complete licenses are in
`skins/niculskin/licenses`. No Bootstrap JavaScript is used by these templates.


## Installation

Version 1.1.1 is the independent continuation release. Its catalog requirements
are WeeWX 5.5.2–5.6 and Python 3.10–3.14. It uses WeeWX's Cheetah and image
report generators; no additional Python dependency is required.

For a pip installation, activate the existing virtual environment that runs
your WeeWX service before running these commands. Both `python` and `weectl`
must come from that environment. For a distribution package installation, use
its `weectl`, with `sudo` if required. Add `--config /path/to/weewx.conf` to the
extension command when your station configuration is not found automatically.

Install the published archive with WeeWX 5's extension installer:

```sh
weectl extension install https://github.com/weewx-packages/niculskin/releases/download/v1.1.1/niculskin-1.1.1.zip
```

Restart your WeeWX service after configuration, for example
`sudo systemctl restart weewx` on systemd. The installer does not restart it
for you.

The installer copies `skins/niculskin`, `skins/languages`,
`user.historygenerator` and `user.translategenerator`. It enables a separate
report, so you do not need to replace `StandardReport`:

```ini
[StdReport]
    [[Niculskin]]
        skin = niculskin
        enable = true
        HTML_ROOT = /var/www/html/weewx/niculskin
```

Choose a writable `HTML_ROOT` served by your web server. After restarting,
wait for an archive interval or run `weectl report run Niculskin`.
Back up custom skin files before reinstalling a newer archive. To remove it,
run `weectl extension uninstall niculskin` and restart WeeWX.

## Configuration

Set the language and site labels in the installed
[`skin.conf`](skins/niculskin/skin.conf):

```ini
[Language]
    language = german
[niculskinLabels]
    title = "My weather station"
    location_href = "#"
    footer = "My station"
```

The language files live in `skins/languages`, for example `german.conf`.
The image plot defaults refer to Droid Sans at
`/usr/share/fonts/truetype/droid/DroidSans-Bold.ttf`. Install that font or set
the plot `*_font_path` options to a font on your machine; otherwise Pillow
falls back to a default. Browser fonts are bundled separately with their
notices in [`skins/niculskin/licenses`](skins/niculskin/licenses).

## Customization

1. You may customize the labels in your language for your needs. The language labels can be found in the appropriate language file in the language skin, e.g. `$WEEWX_ROOT/skins/languages/german.conf` for the German language.
1. If your language is not available, simply copy one of the present language configuration files, change to labels appropriately and refer to it in the Niculskin skin.conf at `WEEWX_ROOT/skins/niculskin/skin.conf`. If you would like to contribute your language file, please open a merge request according to the [Contribution Guideline](CONTRIBUTING.md). Your contribution is welcome.

## Screenshots

![screenshot_1.png](screenshot_1.png)

![screenshot_2.png](screenshot_2.png)

## Contribution

Please see the [Contribution Guideline](CONTRIBUTING.md) for more details.

## License

See [LICENSE](LICENSE) file.

## Credits

Thanks to Sven Reifschneider, the creator of Sofaskin. I liked his skin most as I was looking for something different in the look and feel of weewx.

And thanks to Nick Dajda. He had the history for the weather data. I'm glad I found his code.

[gitlab]: https://gitlab.com/ngulden/niculskin


## Tests

Run `python -m pytest -q tests` with WeeWX and pytest installed. The tests create
an isolated SQLite archive and render every HTML template in German and English.
The installed-archive test runs all standard generators and checks that HTML
stylesheets, CSS font references and license files exist in the public output.
Physical station readings and the optional external radar links are not used.

The skin installs a shared `user.historygenerator` module. Another skin using
the same module name can replace it. Review that overlap before installing
Niculskin and NeoWX Material into the same station.
