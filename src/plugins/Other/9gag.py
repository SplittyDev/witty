__author__ = 'Splitty'

import re
from bs4 import BeautifulSoup
from urllib2 import urlopen, URLError
from yapsy.PluginManager import PluginManagerSingleton
from yapsy.IPlugin import IPlugin

class YoutubePlugin(IPlugin):
    def privmsg(self, user, channel, msg):
        manager = PluginManagerSingleton.get()
        expr = '.*http(?:s)?://(?:w{3}\.)?9gag.com/gag/(?P<id>[0-9a-zA-Z_]*).*'
        if re.match(expr, msg, re.IGNORECASE):
            picture_id = re.match(expr, msg, re.IGNORECASE).group('id')
            url = 'http://9gag.com/gag/%s' % picture_id
            print(url)
            try:
                html = urlopen(url)
            except URLError:
                return
            soup = BeautifulSoup(html)
            title = soup.find('h2', {'class': 'badge-item-title'}).contents[0]
            manager.app.say(channel, 'Title: %s' % str(title).replace('\n', '').strip())
