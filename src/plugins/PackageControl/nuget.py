__author__ = 'Splitty'

from bs4 import BeautifulSoup
from urllib2 import urlopen, HTTPError
from yapsy.PluginManager import PluginManagerSingleton
from yapsy.IPlugin import IPlugin

class NugetPlugin(IPlugin):
    usage = '_nuget <package>'

    def privmsg(self, user, channel, msg):
        manager = PluginManagerSingleton.get()
        if str(msg).startswith('_nuget'):
            pkg = msg[len('_nuget'):].strip()
            print('Looking up NuGet package %s' % pkg)
            try:
                resp = urlopen('https://nuget.org/packages/%s' % pkg)
            except HTTPError:
                manager.app.say(channel, 'Silly %s, this package doesn\'t exist!' % user)
                return
            html = resp.read()
            soup = BeautifulSoup(html)
            package_page = soup.find('div', {'class': 'package-page'})
            version = package_page.find('div', {'class': 'package-page-heading'}).find('h2').contents[0]
            description = package_page.find('p').contents[0]
            manager.app.say(channel, 'Version: %s' % str(version).strip())
            manager.app.say(channel, 'Description: %s' % str(description).strip())
            manager.app.say(channel, 'URL: %s' % ('https://nuget.org/packages/%s' % pkg))
