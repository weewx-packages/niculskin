# installer for the Niculskin.
#
# Based on installer for boostrap skin
#
# Configured by Nico to install Niculskin, 2016-2020

import os.path
import configobj
import setup
import distutils

def loader():
    return NiculskinInstaller()

class NiculskinInstaller(setup.ExtensionInstaller):
    _skin_conf_files = ['niculskin/skin.conf', ]

    def __init__(self):
        files=[('skins/niculskin',
            ['skins/niculskin/history.html.tmpl',
             'skins/niculskin/index.html.tmpl',
             'skins/niculskin/month.html.tmpl',
             'skins/niculskin/week.html.tmpl',
             'skins/niculskin/year.html.tmpl',
             'skins/niculskin/skin.conf',
             'skins/niculskin/favicon.ico']),
           ('skins/niculskin/NOAA',
            ['skins/niculskin/NOAA/NOAA-YYYY.txt.tmpl',
             'skins/niculskin/NOAA/NOAA-YYYY-MM.txt.tmpl']),
           ('skins/niculskin/RSS',
            ['skins/niculskin/RSS/weewx_rss.xml.tmpl']),
           ('bin/user',
            ['bin/user/historygenerator.py',
             'bin/user/translategenerator.py']),
           ('skins/niculskin/css',
            ['skins/niculskin/css/main.css',
             'skins/niculskin/css/main.css.map',
             'skins/niculskin/css/bootstrap.min.css',
             'skins/niculskin/css/google-fonts-lato.css',
             'skins/niculskin/css/font-awesome.min.css',]),
           ('skins/niculskin/css/scss',
            ['skins/niculskin/css/scss/_dry.scss',
             'skins/niculskin/css/scss/main.scss',
             'skins/niculskin/css/scss/_mixins.scss',
             'skins/niculskin/css/scss/_normalize.scss',
             'skins/niculskin/css/scss/_site.scss',
             'skins/niculskin/css/scss/_variables.scss',
            ]),
           ('skins/niculskin/js',
            ['skins/niculskin/js/modernizr-2.6.2.min.js']),
           ('skins/niculskin/fonts',
            ['skins/niculskin/fonts/FontAwesome.otf',
             'skins/niculskin/fonts/fontawesome-webfont.eot',
             'skins/niculskin/fonts/fontawesome-webfont.svg',
             'skins/niculskin/fonts/fontawesome-webfont.ttf',
             'skins/niculskin/fonts/fontawesome-webfont.woff',
             'skins/niculskin/fonts/fontawesome-webfont.woff2',
            ]),           
           ('skins/languages',
            ['skins/languages/dutch.conf',
             'skins/languages/espanol.conf',
             'skins/languages/finnish.conf',
             'skins/languages/francais.conf',
             'skins/languages/german.conf',
             'skins/languages/italian.conf'])
            ]

        super(NiculskinInstaller, self).__init__(
            version="1.0",
            name='niculskin',
            description='A skin in responsive design using bootstrap and offering history tables',
            author="Nico Gulden",
            author_email="ngulden@gmx.de",
            files=files)

        print("")
        print("The following alternative languages are available:")
        self.language = None

        for f in files:
            if f[0] == 'skins/languages':
                for language in f[1]:
                    l = language.strip('conf').split('/')[-1]
                    print("   {}".format(l[:-1]))

        print("")
        print("Language changes can be made in skins/niculskin/skin.conf")

        print("")
        print("Default location for HTML and image files is public_html/")
        print("*** POINT YOUR BROWSER TO: public_html/index.html ***")
        print("")
