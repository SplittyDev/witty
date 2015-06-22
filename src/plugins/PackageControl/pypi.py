__author__ = 'Splitty'

from bs4 import BeautifulSoup
from urllib2 import urlopen, HTTPError
from yapsy.PluginManager import PluginManagerSingleton
from yapsy.IPlugin import IPlugin

class PyPiPlugin(IPlugin):
    def privmsg(self, user, channel, msg):
        manager = PluginManagerSingleton.get()
        if str(msg).startswith('_pypi'):
            pkg = msg[len('_pypi'):].strip()
            print('Looking up PyPi package %s' % pkg)
            try:
                resp = urlopen('https://pypi.python.org/pypi/%s' % pkg)
            except HTTPError:
                manager.app.say(channel, 'Silly %s, this package doesn\'t exist!' % user)
                return
            html = resp.read()
            soup = BeautifulSoup(html)
            section = soup.find('div', {'class': 'section'})
            if 'Index' in section.find('h1').contents[0]:
                latest = section.find('table').find('a').contents[0].lower() \
                    .replace(pkg.lower(), '').encode('ascii', 'ignore')
                all_versions = section.find('table').find_all('a')
                versions = ''
                version_count = 0
                for version in all_versions:
                    separator = ', ' if version_count != 0 else ''
                    versions += '%s%s' % (separator, version.contents[0].lower().replace(pkg.lower(), ''))
                    version_count += 1
                    if 10 == version_count:
                        break
                versions = versions.encode('ascii', 'ignore')
                manager.app.say(channel, 'Please specify a version. Latest: %s' % str(latest))
                manager.app.say(channel, 'Available versions: %s' % str(versions))
                return
            version = section.find('h1').contents[0]
            description = section.find('p').contents[0]
            manager.app.say(channel, 'Package: %s' % str(version).strip())
            manager.app.say(channel, 'Description: %s' % str(description).strip())
            manager.app.say(channel, 'URL: %s' % ('https://pypi.python.org/pypi/%s' % pkg))