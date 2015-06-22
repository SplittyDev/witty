#!/usr/bin/env python
__author__ = 'Splitty'

import random
from argparse import ArgumentParser
from collections import defaultdict
from bs4 import BeautifulSoup
from twisted.words.protocols import irc
from twisted.internet import protocol, reactor, ssl
from urllib2 import urlopen, HTTPError
import re


class WittyBot(irc.IRCClient):
    markov = defaultdict(list)
    chain_length = 1
    chattiness = 200.0
    muted = []

    def __init__(self):
        self.nickname = 'witty'
        self.plugins = {
            'nuget': self.ext_nuget,
            'pip': self.ext_pip,
            'npm': self.ext_npm,
            # 'witness': self.ext_witness,
            'wisdom': self.ext_wisdom,
            'brain': self.ext_brain,
            'mute': self.ext_mute,
        }
        self.ext_brain_init()

    def connectionMade(self):
        print ('Connected to server.')
        irc.IRCClient.connectionMade(self)

    def signedOn(self):
        for chan in str(self.factory.channels).split(','):
            print('Joining %s' % chan)
            self.join(str(chan))

    def joined(self, chan):
        print('Joined channel %s' % chan)

    def privmsg(self, user, channel, msg):
        username = user[:user.index('!')]
        for plugin in self.plugins:
            self.plugins[plugin](username, channel, msg)

    def ext_mute(self, user, channel, msg):
        if msg.startswith('_mute'):
            self.muted.append(channel)
        elif msg.startswith('_unmute'):
            self.muted.remove(channel)

    def ext_nuget(self, user, channel, msg):
        if str(msg).startswith('_nuget'):
            pkg = msg[len('_nuget'):].strip()
            print('Looking up NuGet package %s' % pkg)
            try:
                resp = urlopen('https://nuget.org/packages/%s' % pkg)
            except HTTPError:
                self.say(channel, 'Silly %s, this package doesn\'t exist!' % user)
                return
            html = resp.read()
            soup = BeautifulSoup(html)
            packagepage = soup.find('div', {'class': 'package-page'})
            version = packagepage.find('div', {'class': 'package-page-heading'}).find('h2').contents[0]
            description = packagepage.find('p').contents[0]
            self.say(channel, 'Version: %s' % str(version).strip())
            self.say(channel, 'Description: %s' % str(description).strip())

    def ext_pip(self, user, channel, msg):
        if str(msg).startswith('_pip'):
            pkg = msg[len('_pip'):].strip()
            print('Looking up PyPi package %s' % pkg)
            try:
                resp = urlopen('https://pypi.python.org/pypi/%s' % pkg)
            except HTTPError:
                self.say(channel, 'Silly %s, this package doesn\'t exist!' % user)
                return
            html = resp.read()
            soup = BeautifulSoup(html)
            section = soup.find('div', {'class': 'section'})
            if 'Index' in section.find('h1').contents[0]:
                latest = section.find('table').find('a').contents[0].lower() \
                    .replace(pkg.lower(), '').encode('ascii', 'ignore')
                all_versions = section.find('table').find_all('a')
                versions = ''
                version_count = 0
                for version in all_versions:
                    separator = ', ' if version_count != 0 else ''
                    versions += '%s%s' % (separator, version.contents[0].lower().replace(pkg.lower(), ''))
                    version_count += 1
                    if 10 == version_count:
                        break
                versions = versions.encode('ascii', 'ignore')
                self.say(channel, 'Please specify a version. Latest: %s' % str(latest))
                self.say(channel, 'Available versions: %s' % str(versions))
                return
            version = section.find('h1').contents[0]
            description = section.find('p').contents[0]
            self.say(channel, 'Package: %s' % str(version).strip())
            self.say(channel, 'Description: %s' % str(description).strip())
            self.say(channel, 'URL: %s' % ('https://pypi.python.org/pypi/%s' % pkg))

    def ext_npm(self, user, channel, msg):
        if str(msg).startswith('_npm'):
            pkg = msg[len('_npm'):].strip()
            print('Looking up npm package %s' % pkg)
            try:
                resp = urlopen('https://www.npmjs.com/package/%s' % pkg)
            except HTTPError:
                self.say(channel, 'Silly %s, this package doesn\'t exist!' % user)
                return
            html = resp.read()
            soup = BeautifulSoup(html)
            version = soup.find('div', {'class': 'sidebar'}).find('strong').contents[0]
            description = soup.find('div', {'class': 'content-column'}).find('p').contents[0]
            self.say(channel, 'Version: %s' % str(version).strip())
            self.say(channel, 'Description: %s' % str(description).strip())
            self.say(channel, 'URL: %s' % ('https://www.npmjs.com/package/%s' % pkg))

    def ext_witness(self, user, channel, msg):
        if 'religion' in str(msg):
            self.say(channel, 'All hail splitty_')

    def ext_brain(self, user, channel, msg):
        if msg.startswith('_chattiness'):
            self.chattiness = int(str(msg[11:]).strip())
            self.say(channel, 'Set chattiness to %s' % str((self.chattiness / 1000.0) * 100))
        if not user:
            return
        if self.nickname in msg:
            msg = re.compile(self.nickname + '[:,]* ?', re.I).sub('', msg)
            prefix = user
        else:
            prefix = ''
        self.ext_brain_save(msg, self.chain_length, True)
        if random.randint(0, 1000) <= self.chattiness:
            sentence = self.ext_brain_gen(msg, self.chain_length)
            if sentence:
                if channel not in self.muted and sentence.strip() != msg.strip():
                    self.say(channel, ('%s %s' % (prefix, sentence)).strip())

    def ext_brain_init(self):
        print('Feeding the brain...')
        f = open('ext_brain.txt', 'r')
        count = 0
        for line in f:
            self.ext_brain_save(line, self.chain_length)
            count += 1
        f.close()
        print('Fed the brain with %i sentences' % count)

    def ext_brain_save(self, msg, length, save_to_file=False):
        if save_to_file:
            f = open('ext_brain.txt', 'a')
            f.write(msg + '\n')
            f.close()
        buf = ['\n'] * length
        for word in msg.split():
            self.markov[tuple(buf)].append(word)
            del buf[0]
            buf.append(word)
        self.markov[tuple(buf)].append('\n')

    def ext_brain_gen(self, msg, length, max_words=50):
        buf = msg.split()[:length]
        if len(str(msg).split()) > length:
            message = buf[:]
        else:
            message = []
            for i in xrange(length):
                message.append(random.choice(self.markov[random.choice(self.markov.keys())]))
        for i in xrange(max_words):
            try:
                next_word = random.choice(self.markov[tuple(buf)])
            except IndexError:
                continue
            if next_word == '\n':
                break
            message.append(next_word)
            del buf[0]
            buf.append(next_word)
        return ' '.join(message)

    def ext_wisdom(self, user, channel, msg):
        quotes = [
            "Home is where you hang your @.",
            "The email of the species is more deadly than the mail.",
            "A journey of a thousand sites begins with a single click.",
            "You can't teach a new mouse old clicks.",
            "Great groups from little icons grow.",
            "Speak softly and carry a cellular phone.",
            "In some places, C:\ is the root of all directories.",
            "Oh, what a tangled Website we weave when first we practice.",
            "Pentium wise, pen and paper foolish.",
            "The modem is the message.",
            "Too many clicks spoil the browse.",
            "The geek shall inherit the earth.",
            "Don't byte off more than you can view.",
            "Fax is stranger than fiction.",
            "What boots up, must come down.",
            "Windows will never cease.",
            "Virtual reality is its own reward.",
            "Modulation in all things.",
            "Give a man a fish and you feed him for a day, teach him to use the Net and he won't bother you for weeks.",
            "There's no place like your homepage.",
            "He who laughs last ... probably has a Mac!"
            "Disdain people who use low baud rates.",
            "Back up your data every day.",
            "Jokes about being unable to program a VCR are stupid.",
            "Al Gore strikes you as an 'intriguing' fellow.",
            "Rotate your screen savers more frequently than your automobile tires.",
            "'Hard drive' - Trying to climb a steep, " +
            "muddy hill with 3 flat tires and pulling a trailer load of fertilizer.",
            '"Keyboard" - Place to hang your truck keys.',
            '"Window" - Place in the truck to hang your guns.',
            '"Modem" - How you got rid of your dandelions.',
            '"ROM" - Delicious when you mix it with coca cola.',
            '"Byte" - First word in a kiss-off phrase.',
            '"Reboot" - What you do when the first pair gets covered with barnyard stuff.',
            '"Network" - Activity meant to provide bait for your trout line.',
            '"Mouse" - Fuzzy, soft thing you stuff in your beer bottle in order to get a free case.',
            '"LAN" - To borrow as in, "Hey Delbert! LAN me yore truck."',
            '"Cursor" - What some guys do when they are mad at their wife and/or girlfriend.',
            '"bit" - A wager as in, "I bit you can\'t spit that watermelon seed across the porch long ways."',
        ]
        if 'wisdom' in str(msg):
            self.say(channel, quotes[random.randint(0, len(quotes) - 1)])


class WittyBotFactory(protocol.ClientFactory):
    protocol = WittyBot

    def __init__(self, chan):
        self.channels = chan

    def clientConnectionFailed(self, connector, reason):
        print ('Failed to connect: %s' % reason)
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print ('Lost connection (%s), reconnecting.' % reason)
        connector.connect()


if __name__ == '__main__':
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
