__author__ = 'Splitty'

from yapsy.PluginManager import PluginManagerSingleton
from yapsy.IPlugin import IPlugin

class AdminUtilsPlugin(IPlugin):
    app = None
    config = None
    manager = None
    wittyconf = None

    def __init__(self):
        self.default_config = {
            'admins': []
        }
        super(AdminUtilsPlugin, self).__init__()

    def init(self):
        self.manager = PluginManagerSingleton.get()
        self.app = self.manager.app
        self.wittyconf = self.manager.wittyconf

    def privmsg(self, user, channel, msg):
        authenticated = False if user not in self.config['admins'] else True

        # reload config + rehash plugins
        if authenticated and msg == '_rehash':
            self.manager.wittyconf.reload_config()
            self.rehash(channel)

        # list operators
        elif msg == '_ops':
            self.list_operators(channel)

        # give operator status
        elif authenticated and msg.startswith('_op'):
            _user = msg[3:].strip()
            self.give_operator_status(channel, _user)

        # take operator status
        elif authenticated and msg.startswith('_deop'):
            _user = msg[5:].strip()
            self.take_operator_status(channel, _user)

        # quit
        elif authenticated and msg == '_quit':
            self.app.quit('bye')

        # quit with message
        elif authenticated and msg.startswith('_quit'):
            self.app.quit(str(msg[5:]).strip())

        # not authenticated
        elif not authenticated:
            self.app.say(channel, 'You don\'t have permission to do that!')

    def list_operators(self, channel):
        if not self.config['admins']:
            self.app.say(channel, 'No administrators found.')
        else:
            msg = 'Operators: %s' % str(', '.join(self.config['admins']))
            self.app.say(channel, msg)

    def give_operator_status(self, channel, user):
        if user not in self.config['admins']:
            self.config['admins'].append(user)
            self.manager.wittyconf.update_plugin_config(self.plugin_name, self.config)
            self.app.say(channel, 'Gave %s permission to use adminutils.' % user)

    def take_operator_status(self, channel, user):
        removed = 0
        while user in self.config['admins']:
            self.config['admins'].remove(user)
            removed += 1
        if removed > 0:
            self.app.say(channel, 'Took admin permissions from %s' % user)
            self.manager.wittyconf.update_plugin_config(self.plugin_name, self.config)

    def rehash(self, channel):
        PluginManagerSingleton._PluginManagerSingleton__instance = None
        self.app.load_plugins()
        self.manager = PluginManagerSingleton.get()
        self.app.say(channel, 'Plugins rehashed.')
