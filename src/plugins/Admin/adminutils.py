__author__ = 'Splitty'

import logging
from witty import WittyConf
from yapsy.PluginManager import PluginManagerSingleton
from yapsy.IPlugin import IPlugin

class AdminUtilsPlugin(IPlugin):
    config = None

    def __init__(self):
        self.default_config = {
            'admins': []
        }
        super(AdminUtilsPlugin, self).__init__()

    def privmsg(self, user, channel, msg):
        app = PluginManagerSingleton.get().app
        authenticated = True
        if user not in self.config['admins']:
            authenticated = False
        if msg == '_quit':
            if authenticated:
                app.quit('bye')
            else:
                app.say(channel, 'You shall not pass')
        elif msg.startswith('_quit'):
            if authenticated:
                app.quit(str(msg[5:]).strip())
            else:
                app.say(channel, 'You shall not pass')
