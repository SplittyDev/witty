__author__ = 'Splitty'

import logging
from yapsy.PluginManager import PluginManagerSingleton
from yapsy.IPlugin import IPlugin

class LogUtilsPlugin(IPlugin):
    def privmsg(self, user, channel, msg):
        manager = PluginManagerSingleton.get()
        if msg.startswith('_log'):
            f = open('witty.log', 'r')
            lines = []
            for line in f:
                lines.append(line)
            f.close()
            try:
                count = int(msg[5:].strip())
            except ValueError:
                manager.app.msg(user, '%s is not a number.' % str(msg[5:].strip()))
                return
            if count <= len(lines):
                result = []
                for i in range(len(lines) - count, len(lines), 1):
                    result.append('%i %s' % (i, lines[i]))
                manager.app.msg(user, '\n'.join(result))
            else:
                manager.app.msg(user, 'Only %i lines in witty.log' % len(lines))
