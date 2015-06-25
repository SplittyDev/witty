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
        manager = PluginManagerSingleton.get()
        app = manager.app
        authenticated = True
        if user not in self.config['admins']:
            authenticated = False
        if msg == '_ops':
            if not self.config['admins']:
                app.say(channel, 'No administrators found.')
            else:
                for operator in self.config['admins']:
                    msg = 'Operators: %s' % ', '.join(operator)
                    app.say(channel, msg)
        elif msg.startswith('_op'):
            _user = msg[3:].strip()
            if _user not in self.config['admins']:
                self.config['admins'].append(_user)
                self.manager.wittyconf.update_plugin_config(self.plugin_name, self.config)
                app.say(channel, 'Gave %s permission to use adminutils.' % _user)
        if msg.startswith('_deop'):
            _user = msg[3:].strip()
            removed = 0
            while _user in self.config['admins']:
                self.config['admins'].remove(_user)
                removed += 1
            if removed > 0:
                app.say(channel, 'Took admin permissions from %s' % _user)
                self.manager.wittyconf.update_plugin_config(self.plugin_name, self.config)
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
