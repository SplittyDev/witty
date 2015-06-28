__author__ = 'Splitty'

import re
from bs4 import BeautifulSoup
from urllib2 import urlopen, URLError
from yapsy.PluginManager import PluginManagerSingleton
from yapsy.IPlugin import IPlugin

class YoutubePlugin(IPlugin):
    def privmsg(self, user, channel, msg):
        manager = PluginManagerSingleton.get()
        expr = '.*http(?:s)?://(?:w{3}\.)?(?:youtube\.com|youtu\.be)/watch\?v=(?P<id>[0-9a-z_-]*).*'
        if re.match(expr, msg, re.IGNORECASE):
            video_id = re.match(expr, msg, re.IGNORECASE).group('id')
            url = 'https://www.youtube.com/watch/?v=%s' % video_id
            print(url)
            try:
                html = urlopen(url)
            except URLError:
                return
            soup = BeautifulSoup(html)
            title = soup.find('span', {'class': 'watch-title'}).contents[0].encode('ascii', 'ignore').decode('ascii')
            manager.app.say(channel, 'Title: %s' % str(title).replace('\n', '').strip())
