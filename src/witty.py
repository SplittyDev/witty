#!/usr/bin/env python
__author__ = 'Splitty'

import json
import logging
from os import makedirs, path
import sys
from twisted.words.protocols import irc
from twisted.internet import protocol, reactor, ssl
from yapsy.PluginManager import PluginManagerSingleton


class WittyBot(irc.IRCClient):
    data_dir = ''
    manager = None

    def __init__(self):
        self.nickname = str(WittyConf.get().config['witty']['nick'])
        self.current_dir = path.abspath(path.dirname(__file__))
        self.data_dir = path.join(self.current_dir, 'data')
        if not path.exists(self.data_dir):
            makedirs(self.data_dir)
        self.load_plugins()

    def load_plugins(self):
        plugin_dir = path.join(self.current_dir, 'plugins')
        self.manager = PluginManagerSingleton.get()
        self.manager.app = self
        self.manager.setPluginPlaces([plugin_dir])
        self.manager.collectPlugins()
        self.manager.wittyconf = WittyConf.get()
        for plugin in self.manager.getAllPlugins():
            logging.debug('Initializing plugin %s' % plugin.name)
            self.manager.activatePluginByName(plugin.name)
            plugin_name = plugin.name.strip().lower()
            plugin.plugin_object.plugin_name = plugin_name
            plugin.plugin_object.config = WittyConf.get().config['plugins'].get(plugin_name, {})
            if hasattr(plugin.plugin_object, 'init'):
                plugin.plugin_object.init()

    def connectionMade(self):
        logging.info('Connected to server.')
        irc.IRCClient.connectionMade(self)

    def signedOn(self):
        for chan in str(self.factory.channels).split(','):
            logging.debug('Joining %s' % chan)
            self.join(str(chan))

    def joined(self, chan):
        logging.debug('Joined channel %s' % chan)

    def kickedFrom(self, channel, kicker, message):
        logging.info('Kicked from %s by %s (%s). Rejoining.' % (channel, kicker, message))
        self.join(str(channel))

    def quit(self, message=''):
        self.update_config()
        self.factory.quit = True
        irc.IRCClient.quit(self, message)

    def privmsg(self, user, channel, msg):
        username = user[:user.index('!')]
        for plugin in self.manager.getAllPlugins():
            if hasattr(plugin.plugin_object, 'privmsg'):
                plugin.plugin_object.privmsg(username, channel, msg)

class WittyBotFactory(protocol.ClientFactory):
    protocol = WittyBot

    def __init__(self):
        self.quit = False
        self.channels = ','.join(WittyConf.get().config['witty']['auto_join'])

    def clientConnectionFailed(self, connector, reason):
        logging.error('Failed to connect: %s' % reason)
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        if self.quit:
            reactor.stop()
            return
        logging.info('Lost connection (%s), reconnecting.' % reason)
        connector.connect()


class WittyConf():
    _wittyconf_ = None

    def __init__(self):
        self.config = None

    @staticmethod
    def get():
        if WittyConf._wittyconf_ is None:
            WittyConf._wittyconf_ = WittyConf()
        return WittyConf._wittyconf_

    def update_config(self):
        with open('config.json', 'w') as fconfig:
            json.dump(self.config, fconfig, indent=4, sort_keys=True)

    def update_plugin_config(self, plugin_name, new_config):
        self.config['plugins'][plugin_name] = new_config
        self.update_config()

    @staticmethod
    def create_default_config():
        default_config = {
            'witty': {
                'nick': 'witty',
                'host': 'irc.freenode.com',
                'port': 6667,
                'ssl': False,
                'auto_join': [
                    '#freenode'
                ]
            },
            'plugins': {}
        }
        current_dir = path.abspath(path.dirname(__file__))
        plugin_dir = path.join(current_dir, 'plugins')
        manager = PluginManagerSingleton.get()
        manager.setPluginPlaces([plugin_dir])
        manager.collectPlugins()
        for plugin in manager.getAllPlugins():
            manager.activatePluginByName(plugin.name)
            if hasattr(plugin.plugin_object, 'default_config'):
                default_config['plugins'][plugin.name.strip().lower()] = plugin.plugin_object.default_config
        PluginManagerSingleton._PluginManagerSingleton__instance = None
        with open('config.json', 'w') as fconfig:
            json.dump(default_config, fconfig, indent=4, sort_keys=True)
        print('Created default config at ./config.json')
        sys.exit(0)

    def create_plugin_config(self):
        current_dir = path.abspath(path.dirname(__file__))
        plugin_dir = path.join(current_dir, 'plugins')
        manager = PluginManagerSingleton.get()
        manager.setPluginPlaces([plugin_dir])
        manager.collectPlugins()
        self.config.get('plugins', {})
        for plugin in manager.getAllPlugins():
            manager.activatePluginByName(plugin.name)
            if hasattr(plugin.plugin_object, 'default_config'):
                if plugin.name.strip().lower() not in self.config['plugins']:
                    self.config['plugins'][plugin.name.strip().lower()] = plugin.plugin_object.default_config
                else:
                    for k, v in plugin.plugin_object.default_config.items():
                        if k not in self.config['plugins'][plugin.name.strip().lower()]:
                            self.config['plugins'][plugin.name.strip().lower()][k] = v
        PluginManagerSingleton._PluginManagerSingleton__instance = None
        with open('config.json', 'w') as fconfig:
            json.dump(self.config, fconfig, indent=4, sort_keys=True)
        print('Updated default plugin config at ./config.json')

if __name__ == '__main__':
    logging.basicConfig(filename='witty.log', level=logging.INFO)
    if not path.isfile('config.json'):
        WittyConf.create_default_config()
    with open('config.json', 'r') as f:
        config = json.load(f)
    wittyconf = WittyConf.get()
    wittyconf.config = config
    wittyconf.create_plugin_config()
    host = wittyconf.config['witty']['host']
    port = wittyconf.config['witty']['port']
    witty = WittyBotFactory()
    if wittyconf.config['witty']['ssl']:
        reactor.connectSSL(str(host), int(port), witty, ssl.ClientContextFactory())
    else:
        reactor.connectTCP(str(host), int(port), witty)
    reactor.run()
