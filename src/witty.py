#!/usr/bin/env python
__author__ = 'Splitty'

import json
import logging
from os import path
import sys
from twisted.words.protocols import irc
from twisted.internet import protocol, reactor, ssl
from yapsy.PluginManager import PluginManagerSingleton


class WittyBot(irc.IRCClient):
    data_dir = ''
    config = None
    manager = None

    def __init__(self):
        self.nickname = 'witty'
        self.current_dir = path.abspath(path.dirname(__file__))
        self.data_dir = path.join(self.current_dir, 'data')

    def load_plugins(self):
        plugin_dir = path.join(self.current_dir, 'plugins')
        self.manager = PluginManagerSingleton.get()
        self.manager.app = self
        self.manager.setPluginPlaces([plugin_dir])
        self.manager.collectPlugins()
        for plugin in self.manager.getAllPlugins():
            logging.debug('Initializing plugin %s' % plugin.name)
            self.manager.activatePluginByName(plugin.name)

    def update_config(self):
        with open('config.json', 'w') as fconfig:
            json.dump(self.config, fconfig, indent=4, sort_keys=True)

    def connectionMade(self):
        logging.info('Connected to server.')
        irc.IRCClient.connectionMade(self)

    def signedOn(self):
        self.config = self.factory.config
        self.load_plugins()
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

    def __init__(self, config):
        self.quit = False
        self.config = config
        self.channels = ','.join(self.config['witty']['auto_join'])

    def clientConnectionFailed(self, connector, reason):
        logging.error('Failed to connect: %s' % reason)
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        if self.quit:
            reactor.stop()
        return
        logging.info('Lost connection (%s), reconnecting.' % reason)
        connector.connect()


if __name__ == '__main__':
    logging.basicConfig(filename='witty.log', level=logging.INFO)
    if not path.isfile('config.json'):
        default_config = {
            'witty': {
                'host': 'int0x10.com',
                'port': 6697,
                'ssl': True,
                'auto_join': [
                    '#int0x10'
                ],
                'administrators': [
                    'splitty_',
                    '[mobile]splitty_'
                ]
            },
            'plugins': {
                'brain': {
                    'chattiness': 250
                }
            }
        }
        with open('config.json', 'w') as f:
            json.dump(default_config, f, indent=4, sort_keys=True)
    with open('config.json', 'r') as f:
        config = json.load(f)
    witty = WittyBotFactory(config)
    if config['witty']['ssl']:
        reactor.connectSSL(config['witty']['host'], config['witty']['port'], witty, ssl.ClientContextFactory())
    else:
        reactor.connectTCP(config['witty']['host'], config['witty']['port'], config, witty)
    reactor.run()
