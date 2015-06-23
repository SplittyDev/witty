__author__ = 'Splitty'

import re
from bs4 import BeautifulSoup
from urllib2 import urlopen, URLError
from yapsy.PluginManager import PluginManagerSingleton
from yapsy.IPlugin import IPlugin

class ImgurPlugin(IPlugin):
    def privmsg(self, user, channel, msg):
        manager = PluginManagerSingleton.get()
        expr = '.*http(?:s)?://(?:w{3}\.)?imgur.com/gallery/(?P<id>[0-9a-zA-Z_]*).*'
        if re.match(expr, msg, re.IGNORECASE):
            picture_id = re.match(expr, msg, re.IGNORECASE).group('id')
            url = 'https://imgur.com/gallery/%s' % picture_id
            print(url)
            try:
                html = urlopen(url)
            except URLError:
                return
            soup = BeautifulSoup(html)
            title = soup.find('h1', {'id': 'image-title'}).contents[0]
            manager.app.say(channel, 'Title: %s' % str(title).replace('\n', '').strip())
