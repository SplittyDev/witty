#!/usr/bin/env python
__author__ = 'Splitty'

import imp
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
        # nick of the bot
        self.nickname = str(WittyConf.get().config['witty']['nick'])

        # get current directory and the plugin data directory
        self.current_dir = path.abspath(path.dirname(__file__))
        self.data_dir = path.join(self.current_dir, 'data')
        if not path.exists(self.data_dir):
            makedirs(self.data_dir)

        # load plugins
        self.load_plugins()

    def load_plugins(self):
        # plugin directory
        plugin_dir = path.join(self.current_dir, 'plugins')

        # configure plugin manager
        self.manager = PluginManagerSingleton.get()
        self.manager.app = self
        self.manager.setPluginPlaces([plugin_dir])
        self.manager.collectPlugins()
        self.manager.wittyconf = WittyConf.get()

        # iterate over all plugins
        for plugin in self.manager.getAllPlugins():
            logging.debug('Initializing plugin %s' % plugin.name)
            self.manager.activatePluginByName(plugin.name)

            # attach plugin name and plugin configuration to the plugin
            plugin_name = plugin.name.strip().lower()
            plugin.plugin_object.plugin_name = plugin_name
            plugin.plugin_object.config = WittyConf.get().config['plugins'].get(plugin_name, {})

            # call init function of the plugin if present
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
        self.factory.quit = True
        irc.IRCClient.quit(self, message)

    def privmsg(self, user, channel, msg):
        # extract nick from nick!username@host
        nick = user[:user.index('!')]

        # iterate over all plugins
        for plugin in self.manager.getAllPlugins():

            # call privmsg function of the plugin if present
            if hasattr(plugin.plugin_object, 'privmsg'):
                plugin.plugin_object.privmsg(nick, channel, msg)

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


class WittyConf:
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
        # default configuration
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

        # get current directory and plugin directory
        current_dir = path.abspath(path.dirname(__file__))
        plugin_dir = path.join(current_dir, 'plugins')

        # configure plugin manager
        manager = PluginManagerSingleton.get()
        manager.setPluginPlaces([plugin_dir])
        manager.collectPlugins()

        # iterate over all plugins
        for plugin in manager.getAllPlugins():
            manager.activatePluginByName(plugin.name)

            # get default config of plugin if available
            if hasattr(plugin.plugin_object, 'default_config'):
                default_config['plugins'][plugin.name.strip().lower()] = plugin.plugin_object.default_config

        # reset plugin manager
        PluginManagerSingleton._PluginManagerSingleton__instance = None

        # write config file
        with open('config.json', 'w') as fconfig:
            json.dump(default_config, fconfig, indent=4, sort_keys=True)
        print('Created default config at ./config.json')

        sys.exit(0)

    def reload_config(self):
        with open('config.json', 'r') as fconfig:
            self.config = json.load(fconfig)

    def create_plugin_config(self):
        # get current directory and plugin directory
        current_dir = path.abspath(path.dirname(__file__))
        plugin_dir = path.join(current_dir, 'plugins')

        # configure plugin manager
        manager = PluginManagerSingleton.get()
        manager.setPluginPlaces([plugin_dir])
        manager.collectPlugins()

        # set default value for plugin key
        self.config.get('plugins', {})

        # iterate over all plugins
        for plugin in manager.getAllPlugins():
            manager.activatePluginByName(plugin.name)

            # get the default config if the plugin if available
            if hasattr(plugin.plugin_object, 'default_config'):
                # create the default config if not already in the config
                if plugin.name.strip().lower() not in self.config['plugins']:
                    self.config['plugins'][plugin.name.strip().lower()] = plugin.plugin_object.default_config
                else:
                    # update keys
                    for k, v in plugin.plugin_object.default_config.items():
                        if k not in self.config['plugins'][plugin.name.strip().lower()]:
                            self.config['plugins'][plugin.name.strip().lower()][k] = v

        # reset plugin manager
        PluginManagerSingleton._PluginManagerSingleton__instance = None

        self.update_config()
        print('Updated default plugin config at ./config.json')

if __name__ == '__main__':
    # configure logger
    logging.basicConfig(filename='witty.log', level=logging.INFO)

    missing_modules = []

    def check_module(module_name):
        try:
            imp.find_module(module_name)
        except ImportError:
            missing_modules.append(module_name)

    check_module('bs4')
    check_module('cryptography')
    check_module('twisted')
    check_module('yapsy')

    if missing_modules:
        for module in missing_modules:
            print('Could not find module \'%s\'.' % module)
        sys.exit(1)

    # load the configuration if it exists
    # if not: create a default configuration
    if not path.isfile('config.json'):
        WittyConf.create_default_config()
    with open('config.json', 'r') as f:
        config = json.load(f)

    # configure wittyconf
    wittyconf = WittyConf.get()
    wittyconf.config = config
    wittyconf.create_plugin_config()

    # get host and port from the config
    host = wittyconf.config['witty']['host']
    port = wittyconf.config['witty']['port']
    witty = WittyBotFactory()

    # connect to the irc server
    if wittyconf.config['witty']['ssl']:
        reactor.connectSSL(str(host), int(port), witty, ssl.ClientContextFactory())
    else:
        reactor.connectTCP(str(host), int(port), witty)
    reactor.run()
