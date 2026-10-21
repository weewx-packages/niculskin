#
# Copyright (c) 2015  Nick Dajda <nick.dajda@gmail.com>
# Modified 2026-10-22: load translations before WeeWX constructs formatters.
#
# Distributed under the terms of the GNU GENERAL PUBLIC LICENSE
#
"""Provides a way of easily overriding labels in skin.conf files with other languages.
Useful for skin designers who want to use multiple skin.conf files and easily make
the skins available in multiple languages.

1) Place this file in bin/user/translategenerator.py

2) Store each language specific file in skins/languages/[language].conf
   Take a look at an existing one to see how they work.

3) Add this section to each skin.conf:
[Language]

    #
    # Set a language below and labels will be overridden with any that are specified in
    # skins/languages/[language].conf
    #

    language = espanol

4) Replace any instances of CheetahGenerator or ImageGenerator in skin.conf with
these translation classes:

[Generators]
        # Change from this:
        # generator_list = weewx.cheetahgenerator.CheetahGenerator, weewx.imagegenerator.ImageGenerator, weewx.reportengine.CopyGenerator

        # To this:
        generator_list = user.translategenerator.CheetahGeneratorTranslated, user.translategenerator.ImageGeneratorTranslated, weewx.reportengine.CopyGenerator
"""

import copy
import logging
import os.path
from configobj import ConfigObj, ConfigObjError

from weewx.imagegenerator import ImageGenerator
from weewx.cheetahgenerator import CheetahGenerator

log = logging.getLogger(__name__)


class ImageGeneratorTranslated(ImageGenerator):
    """Apply language labels before constructing the image generator."""

    def __init__(self, config_dict, skin_dict, *args, **kwargs):
        translated = _translated_skin(skin_dict, config_dict)
        super(ImageGeneratorTranslated, self).__init__(config_dict, translated, *args, **kwargs)


class CheetahGeneratorTranslated(CheetahGenerator):
    """Apply language labels before WeeWX constructs its formatter."""

    def __init__(self, config_dict, skin_dict, *args, **kwargs):
        translated = _translated_skin(skin_dict, config_dict)
        super(CheetahGeneratorTranslated, self).__init__(config_dict, translated, *args, **kwargs)


def _translated_skin(skin_dict, config_dict):
    """Return a separate skin dictionary with the selected language merged.

    Args:
        skin_dict (ConfigObj): Report skin configuration.
        config_dict (ConfigObj): Station configuration.

    Returns:
        ConfigObj: Translated copy, leaving other reports unchanged.
    """
    translated = copy.deepcopy(skin_dict)
    language_dict = _get_language_dict(skin_dict, config_dict)
    if language_dict is not None:
        translated.merge(language_dict)
    return translated


def _get_language_dict(skin_dict, config_dict):
    """Read the selected legacy language file, or use the English skin defaults.

    Args:
        skin_dict (ConfigObj): Report skin configuration with optional Language section.
        config_dict (ConfigObj): Station configuration containing the skin root.

    Returns:
        ConfigObj|None: Language overrides, or None for English or an unavailable file.
    """
    language = skin_dict.get('Language', {}).get('language', 'english')
    if language == 'english':
        return None
    if os.path.basename(language) != language:
        raise ValueError('Language must name a file in skins/languages')
    skin_root = skin_dict.get('SKIN_ROOT', config_dict['StdReport']['SKIN_ROOT'])
    path = os.path.join(config_dict['WEEWX_ROOT'], skin_root, 'languages', language + '.conf')
    try:
        return ConfigObj(path, encoding='utf-8', file_error=True)
    except (OSError, ConfigObjError) as e:
        log.warning('Could not load language dictionary %s: %s', path, e)
        return None
