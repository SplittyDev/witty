#!/usr/bin/env python
__author__ = 'Splitty'

import random
from argparse import ArgumentParser
import logging
import os
from twisted.words.protocols import irc
from twisted.internet import protocol, reactor, ssl
from yapsy.PluginManager import PluginManagerSingleton


class WittyBot(irc.IRCClient):
    data_dir = ''
    manager = None

    def __init__(self):
        self.nickname = 'witty'
        self.current_dir = os.path.abspath(os.path.dirname(__file__))
        self.data_dir = os.path.join(self.current_dir, 'data')
        self.load_plugins()

    def load_plugins(self):
        plugin_dir = os.path.join(self.current_dir, 'plugins')
        self.manager = PluginManagerSingleton.get()
        self.manager.app = self
        self.manager.setPluginPlaces([plugin_dir])
        self.manager.collectPlugins()
        for plugin in self.manager.getAllPlugins():
            logging.info('Initializing plugin %s' % plugin.name)
            self.manager.activatePluginByName(plugin.name)

    def connectionMade(self):
        logging.info('Connected to server.')
        irc.IRCClient.connectionMade(self)

    def signedOn(self):
        for chan in str(self.factory.channels).split(','):
            logging.info('Joining %s' % chan)
            self.join(str(chan))

    def joined(self, chan):
        logging.info('Joined channel %s' % chan)

    def kickedFrom(self, channel, kicker, message):
        logging.info('Kicked from %s by %s (%s)' % (channel, kicker, message))
        logging.info('Rejoining %s' % channel)
        self.join(str(channel))

    def privmsg(self, user, channel, msg):
        username = user[:user.index('!')]
        if msg == '_rehash':
            PluginManagerSingleton._PluginManagerSingleton__instance = None
            self.load_plugins()
            logging.info('Plugins rehashed.')
        for plugin in self.manager.getAllPlugins():
            if hasattr(plugin.plugin_object, 'privmsg'):
                plugin.plugin_object.privmsg(username, channel, msg)

class WittyBotFactory(protocol.ClientFactory):
    protocol = WittyBot

    def __init__(self, chan):
        self.channels = chan

    def clientConnectionFailed(self, connector, reason):
        logging.error('Failed to connect: %s' % reason)
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        logging.info('Lost connection (%s), reconnecting.' % reason)
        connector.connect()


if __name__ == '__main__':
    logging.basicConfig(filename='witty.log', level=logging.INFO)
    parser = ArgumentParser(description='Witty IRC bot')
    parser.add_argument('-s', '--server', type=str, help='IRC server')
    parser.add_argument('-p', '--port', type=int, help='IRC port')
    parser.add_argument('-j', '--join', type=str, help='Channels to join')
    parser.add_argument('--ssl', action='store_true', help='Enable SSL')
    args = parser.parse_args()
    server = args.server
    port = args.port
    channels = args.join
    usessl = args.ssl
    if ':' in server:
        port = int(server[str(server).index(':') + 1:])
        server = server[:str(server).index(':')]
    print ('%s:%i %s %s' % (server, port, channels, 'ssl' if usessl else ''))
    witty = WittyBotFactory(channels)
    if usessl:
        reactor.connectSSL(server, port, witty, ssl.ClientContextFactory())
    else:
        reactor.connectTCP(server, port, witty)
    reactor.run()
