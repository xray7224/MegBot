#!/usr/bin/env python
##
#   This file is part of MegBot.
#
#   MegBot is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   MegBot is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with MegBot.  If not, see <http://www.gnu.org/licenses/>.
##

import sys
import os

from threading import Thread
from time import sleep
import traceback

from megbot.configuration import configuration
from megbot.loader import MasterLoader


class Bot(object):
    def __init__(self, name, config, thread, run=True):
        """Initalises bot"""
        self.name = name
        self.config = config
        self.settings = config["networks"][name]
        self.running = False
        self.channels = {}
        self.thread = thread

        # allow the main thread to call us
        self.thread["object"] = self
        self.alive = True

        # load loaders - yeh i know.
        MasterLoader(self, self.config[u"paths"]) # returns None.

        self.core["Coreconnect"].main(self)

        if run:
            self.server = self.libraries["IRCObjects"].Server(self)
            self.server.__setuphooks__(self)
            self.run()


    def run(self):
        """This will run the bot.

        It loops (indefinitly) asking the parser for messages from the IRC
        It'll then split them up indevidually by \r\n (end of an IRC message)
        Once it has each message it'll pass it along to the delegator which
        will validate and then deluege if needed to the correct
        part of the bot
        """

        while self.alive:
            while not self.running and self.alive:
                sleep(1)
            while self.running and self.alive:
                try:
                    data = self.core["Coreparser"].main(self, [])
                except Exception:
                    traceback.print_exc()
                    self.running = False
                    break
                for line in data.split(u"\r\n"):
                    self.core["Coredelegator"].main(self, line)
            try:
                self.sock.close()
            except Exception:
                pass
            if self.alive:
                self.__init__(self.name,
                        self.config,
                        self.thread,
                        False)

    def quit(self):
        self.core["Coreraw"].main(self, "QUIT")


def main():
    # since there is no good logging and/or way of talking to the
    # bot this is set to not ready as it shouldn't be used
    DaemonNotReady = True
    if "-d" in sys.argv and not DaemonNotReady:
        print "[Warning] Daemon mode isn't ready yet - see https://github.com/xray7224/MegBot/issues/31"
        # add a ticket number?
        sys.exit() # they can start me again if they still want to run me

    if "-d" in sys.argv and DaemonNotReady:
        # daemon process
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except Exception:
            # failed to daemonise
            print "[ErrorLine] Failed to daemonise - quitting."
            sys.exit()

    bots = {}

    for network in configuration["networks"]:
        if not "active" in configuration["networks"][network].keys() or (
                configuration["networks"][network]["active"]):
            connection = {}
            connection["thread"] = Thread(target=Bot, args=(network, configuration, connection))
            connection["object"] = None
            connection["thread"].daemon = True
            connection["thread"].start()
            bots[network] = connection

    try:
        while True:
            sleep(2)
    except KeyboardInterrupt:
        print "\nCtrl-C been hit, run for your lives!"
        for network, bot in bots.items():
            if bot["object"]:
                bot["object"].alive = False
                if bot["object"].running:
                    bot["object"].quit()
                bot["thread"].join()
