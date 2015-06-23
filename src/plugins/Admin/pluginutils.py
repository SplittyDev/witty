__author__ = 'Splitty'

import logging
from yapsy.PluginManager import PluginManagerSingleton
from yapsy.IPlugin import IPlugin


class PluginUtilsPlugin(IPlugin):
    def __init__(self):
        self.manager = PluginManagerSingleton.get()
        self.app = self.manager.app
        super(PluginUtilsPlugin, self).__init__()

    def privmsg(self, user, channel, msg):
        if msg == '_rehash':
            self.rehash(channel)

    def rehash(self, channel):
        PluginManagerSingleton._PluginManagerSingleton__instance = None
        self.app.load_plugins()
        self.manager = PluginManagerSingleton.get()
        self.app.say(channel, 'Plugins rehashed.')
