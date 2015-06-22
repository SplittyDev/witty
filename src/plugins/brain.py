__author__ = 'Splitty'

from collections import defaultdict
from yapsy.PluginManager import PluginManagerSingleton
from yapsy.IPlugin import IPlugin
import logging
import os
import random
import re

class BrainPlugin(IPlugin):
    markov = defaultdict(list)
    chain_length = 1
    chattiness = 250

    def __init__(self):
        self.manager = PluginManagerSingleton.get()
        self.data_dir = self.manager.app.data_dir
        self.data_path = os.path.join(self.data_dir, 'ext_brain.txt')
        super(BrainPlugin, self).__init__()
        self.post_init()

    def post_init(self):
        f = open(self.data_path, 'r')
        count = 0
        for line in f:
            self.ext_brain_save(line, self.chain_length)
            count += 1
        f.close()
        logging.info('Fed the brain with %i sentences' % count)

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

    def ext_brain_gen(self, msg, length, min_words=2, max_words=25):
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
        if len(message) < min_words:
            message.append(random.choice(self.markov[tuple(buf)]))
        return ' '.join(message)

    def privmsg(self, user, channel, msg):
        if msg.startswith('_chattiness'):
            self.chattiness = int(str(msg[11:]).strip())
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
