__author__ = 'Splitty'

import re
from bs4 import BeautifulSoup
from urllib2 import urlopen, URLError
from yapsy.PluginManager import PluginManagerSingleton
from yapsy.IPlugin import IPlugin

class RedditPlugin(IPlugin):
    def privmsg(self, user, channel, msg):
        manager = PluginManagerSingleton.get()
        expr = '.*http(?:s)?://(?:w{3}\.)?reddit\.com/r/(?P<sub>[0-9a-z_]*)/comments/(?P<id>[0-9a-z_]*).*'
        if re.match(expr, msg, re.IGNORECASE):
            match = re.match(expr, msg, re.IGNORECASE)
            subreddit = match.group('sub')
            article = match.group('id')
            url = 'https://reddit.com/r/%s/comments/%s' % (subreddit, article)
            print(url)
            try:
                html = urlopen(url)
            except URLError:
                return
            soup = BeautifulSoup(html)
            title = soup.find('a', {'class': 'title'}).contents[0]
            manager.app.say(channel, 'Title: %s' % str(title).replace('\n', '').strip())
