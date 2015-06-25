__author__ = 'Splitty'

from bs4 import BeautifulSoup
from urllib2 import urlopen, HTTPError
from yapsy.PluginManager import PluginManagerSingleton
from yapsy.IPlugin import IPlugin

class NpmPlugin(IPlugin):
    usage = '_npm <package>'

    def privmsg(self, user, channel, msg):
        manager = PluginManagerSingleton.get()
        if str(msg).startswith('_npm'):
            pkg = msg[len('_npm'):].strip()
            print('Looking up npm package %s' % pkg)
            try:
                resp = urlopen('https://www.npmjs.com/package/%s' % pkg)
            except HTTPError:
                manager.app.say(channel, 'Silly %s, this package doesn\'t exist!' % user)
                return
            html = resp.read()
            soup = BeautifulSoup(html)
            version = soup.find('div', {'class': 'sidebar'}).find('strong').contents[0]
            description = soup.find('div', {'class': 'content-column'}).find('p').contents[0]
            manager.app.say(channel, 'Version: %s' % str(version).strip())
            manager.app.say(channel, 'Description: %s' % str(description).strip())
            manager.app.say(channel, 'URL: %s' % ('https://www.npmjs.com/package/%s' % pkg))
