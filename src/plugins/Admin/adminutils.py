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

        # list operators
        if msg == '_ops':
            self.list_operators(channel)

        # help
        elif msg == '_help':
            self.help(channel)

        # plugin help
        elif msg.startswith('_help'):
            plugin_name = msg[5:].strip()
            self.help_plugin(channel, plugin_name)

        # reload config + rehash plugins
        elif authenticated and msg == '_rehash':
            self.manager.wittyconf.reload_config()
            self.rehash(channel)

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

        # send latest logs to user
        elif authenticated and msg.startswith('_log'):
            count = int(msg[5:].strip())
            self.send_logs(user, count)

    def list_operators(self, channel):
        if not self.config['admins']:
            self.app.say(channel, 'No administrators found.')
        else:
            msg = 'Operators: %s' % str(', '.join(self.config['admins']))
            self.app.say(channel, msg)

    def give_operator_status(self, channel, user):
        if user not in self.config['admins']:
            self.config['admins'].append(user)
            self.wittyconf.update_plugin_config(self.plugin_name, self.config)
            self.app.say(channel, 'Gave %s permission to use adminutils.' % user)

    def take_operator_status(self, channel, user):
        removed = 0
        while user in self.config['admins']:
            self.config['admins'].remove(user)
            removed += 1
        if removed > 0:
            self.app.say(channel, 'Took admin permissions from %s' % user)
            self.wittyconf.update_plugin_config(self.plugin_name, self.config)

    def rehash(self, channel):
        PluginManagerSingleton._PluginManagerSingleton__instance = None
        self.app.load_plugins()
        self.manager = PluginManagerSingleton.get()
        self.app.say(channel, 'Plugins rehashed.')

    def send_logs(self, user, count):
        f = open('witty.log', 'r')
        lines = []
        for line in f:
            lines.append(line)
        f.close()
        if count <= len(lines):
            result = []
            for i in range(len(lines) - count, len(lines), 1):
                result.append('%i %s' % (i, lines[i]))
                self.app.msg(user, '\n'.join(result))
            else:
                self.app.msg(user, 'Only %i lines in witty.log' % len(lines))

    def help(self, channel):
        plugins = []
        for plugin in self.manager.getAllPlugins():
            plugins.append(plugin.name)
        msg = 'Plugins: %s' % str(' | '.join(plugins))
        self.app.say(channel, msg)

    def help_plugin(self, channel, plugin_name):
        description = None
        usage = None
        for plugin in self.manager.getAllPlugins():
            if plugin_name == plugin.name:
                description = str(plugin.description)
                if hasattr(plugin.plugin_object, 'usage'):
                    usage = str(plugin.plugin_object.usage)
        if usage is not None:
            self.app.say(channel, 'Usage: %s' % usage)
        if description is not None:
            self.app.say(channel, 'Description: %s' % description)
