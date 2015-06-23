__author__ = 'Splitty'

import random
from yapsy.PluginManager import PluginManagerSingleton
from yapsy.IPlugin import IPlugin

class WisdomPlugin(IPlugin):
    def privmsg(self, user, channel, msg):
        manager = PluginManagerSingleton.get()
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
        if 'witty' in str(msg) and ('wisdom' in str(msg) or 'wise' in str(msg)):
            manager.app.say(channel, quotes[random.randint(0, len(quotes) - 1)])
