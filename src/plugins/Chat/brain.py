__author__ = 'Splitty'

from bs4 import BeautifulSoup
from collections import defaultdict
from urllib2 import urlopen, URLError
from witty import WittyConf
from yapsy.PluginManager import PluginManagerSingleton
from yapsy.IPlugin import IPlugin
import logging
import os
import random
import re


class BrainPlugin(IPlugin):
    block = False
    chain_length = 1
    chattiness = 100
    config = None
    data_path = None
    data_dir = None
    manager = None
    markov = defaultdict(list)
    plugin_name = None

    def __init__(self):
        self.default_config = {
            'chattiness': 100
        }
        super(BrainPlugin, self).__init__()

    def init(self):
        self.chattiness = self.config['chattiness']
        self.manager = PluginManagerSingleton.get()
        self.data_dir = self.manager.app.data_dir
        self.data_path = os.path.join(self.data_dir, 'ext_brain.txt')
        if not os.path.isfile(self.data_path):
            open(self.data_path, 'a').close()
        self.post_init()

    def post_init(self):
        self.markov.clear()
        f = open(self.data_path, 'r')
        count = 0
        for line in f:
            self.ext_brain_save(line, self.chain_length)
            count += 1
        f.close()

    def ext_brain_save(self, msg, length, save_to_file=False):
        if save_to_file:
            f = open(self.data_path, 'a')
            f.write(msg + '\n')
            f.close()
        buf = ['\n'] * length
        for word in msg.split():
            self.markov[tuple(buf)].append(word)
            del buf[0]
            buf.append(word)
        self.markov[tuple(buf)].append('\n')

    def ext_brain_gen(self, msg, length, min_words=2, max_words=10):
        buf = [random.choice(msg.split())]
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
        if len(message) < min_words:
            message.append(random.choice(self.markov[tuple(buf)]))
        return ' '.join(message)

    def privmsg(self, user, channel, msg):
        if self.block:
            return
        if msg.startswith('_feed'):
            self.block = True
            url = msg[5:].strip()
            self.manager.app.say(channel, 'Eating %s...' % url)
            try:
                html = urlopen(url)
            except URLError, e:
                self.manager.app.say(channel, e)
                return
            soup = BeautifulSoup(html)
            text = soup.getText()
            f = open(self.data_path, 'a')
            f.write(text.encode('ascii', 'ignore'))
            f.close()
            logging.info('Reloading...')
            self.post_init()
            self.manager.app.say(channel, 'Done. So much wisdom!')
            self.block = False
        if msg == '_chattiness':
            self.manager.app.say(channel, 'Chattiness is at %s%%' % str(int((self.chattiness / 1000.0) * 100)))
        elif msg.startswith('_chattiness'):
            self.chattiness = int(str(msg[11:]).strip())
            self.config['chattiness'] = int(self.chattiness)

            #
            # Exception happens here
            WittyConf.get().update_plugin_config(self.plugin_name, self.config)
            #

            self.manager.app.say(channel, 'Set chattiness to %s%%' % str(int((self.chattiness / 1000.0) * 100)))
        if not user or user == self.manager.app.nickname or msg.startswith('_'):
            return
        if self.manager.app.nickname in msg:
            msg = re.compile(self.manager.app.nickname + '[:,]* ?', re.I).sub('', msg)
            prefix = user
        else:
            prefix = ''
        self.ext_brain_save(msg, self.chain_length, True)
        if random.randint(0, 1000) <= self.chattiness:
            sentence = self.ext_brain_gen(msg, self.chain_length)
            if sentence:
                if channel and sentence.strip() != msg.strip():
                    self.manager.app.say(channel, ('%s %s' % (prefix, sentence)).strip())
