###
# Copyright (c) 2012, b42
# Published under WTFPL.
#
###

import os
import sys
import threading
import SocketServer

import supybot.conf as conf
import supybot.ircmsgs as ircmsgs
import supybot.world as world
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

class MsgPipe(callbacks.Plugin):
    """
    This plugin listens on a socket (either TCP or UNIX) and whenever
    someone sends a message to the socket, it dumps it to a channel.
    It has no commands and requires a bit of a configuration to be useful.
    """

    class ConnectionHandler(SocketServer.StreamRequestHandler):
        def handle(self):
            if type(self.client_address) == tuple:
                self.log.info('MsgPipe: network connect from: %s', self.client_address)

            try:
                reply = self.rfile.readline()
                reply = reply[:-1]
            except:
                self.log.error('MsgPipe: exception %s: %s', sys.exc_type,
                        sys.exc_value)
                reply = "MsgPipe: failed to read data from socket, see log for details"

            # Announce the location to all configured channels
            for channel in self.irc.state.channels.keys():
                if conf.supybot.plugins.MsgPipe.announce.get(channel)():
                    print channel, reply
                    self.irc.queueMsg(ircmsgs.privmsg(channel, reply))

    def __init__(self, irc):
        self.__parent = super(MsgPipe, self)
        self.__parent.__init__(irc)

        self.ConnectionHandler.irc = irc
        self.ConnectionHandler.log = self.log

        config = conf.supybot.plugins.MsgPipe
        self.unixsock = None

        if config.unix():
            self.unixsock = config.socketFile()

            # delete stale socket
            try:
                os.unlink(self.unixsock)
            except OSError:
                pass

            self.server = SocketServer.UnixStreamServer(self.unixsock,
                    self.ConnectionHandler)
        else:
            host = config.host()
            port = config.port()
            self.server = SocketServer.TCPServer((host, port),
                    self.ConnectionHandler)

        t = threading.Thread(
                target = self.server.serve_forever,
                name = "MsgPipeThread"
            )
        t.setDaemon(True)
        t.start()
        world.threadsSpawned += 1

    def die(self):
        self.log.info('MsgPipe: shutting down socketserver')
        self.server.shutdown()
        self.server.server_close()

        if self.unixsock:
            os.unlink(self.unixsock)

        self.__parent.die()

Class = MsgPipe

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
