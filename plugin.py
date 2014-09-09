###
# Copyright (c) 2014, Afternet.org, #minecraft
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
import getpass
import mcrcon
import re

class Craftoria(callbacks.Plugin):
    """
    This plugin listens on a socket (either TCP or UNIX) and whenever
    someone sends a message to the socket, it dumps it to a channel.
    It has no commands and requires a bit of a configuration to be useful.
    """

    class ConnectionHandler(SocketServer.StreamRequestHandler):
        def handle(self):
            if type(self.client_address) == tuple:
                self.log.info('Craftoria: network connect from: %s', self.client_address)

            try:
                reply = self.rfile.readline()
                reply = reply.rstrip()
            except:
                self.log.error('Craftoria: exception %s: %s', sys.exc_type,
                        sys.exc_value)
                reply = "Craftoria: failed to read data from socket, see log for details"

            # Announce the location to all configured channels
            for channel in self.irc.state.channels.keys():
                if conf.supybot.plugins.Craftoria.announce.get(channel)():
                    #message = self.filterTCPToIRC(self, reply)
                    message = reply;
                    if message:
                        print channel, message
                        self.irc.queueMsg(ircmsgs.privmsg(channel, message))
                        
                        #This doesn't belong here, but in a similar message handler of the opposite type
                        #self.rcon.send(message)

    def __init__(self, irc):
        self.__parent = super(Craftoria, self)
        self.__parent.__init__(irc)

        self.ConnectionHandler.irc = irc
        self.ConnectionHandler.log = self.log

        config = conf.supybot.plugins.Craftoria
        self.unixsock = None

        self.rcon = mcrcon.MCRcon(config.rcon_host(), int(config.rcon_port()), config.rcon_pass()) 
        if self.rcon:
            self.log.info('Craftoria: successfully connected to rcon')
        else:
            self.log.info('Craftoria: could not connect to rcon')


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
            self.server = SocketServer.TCPServer((host, port), self.ConnectionHandler)

        t = threading.Thread(
                target = self.server.serve_forever,
                name = "CraftoriaThread"
            )
        t.setDaemon(True)
        t.start()
        world.threadsSpawned += 1

    def inFilter(self, irc, msg):
        return self.filterIRCToMinecraft(msg);


    def die(self):
        self.rcon.close()
        self.log.info('Craftoria: shutting down socketserver')
        self.server.shutdown()
        self.server.server_close()

        if self.unixsock:
            os.unlink(self.unixsock)

        self.__parent.die()

    def filterIRCToMinecraft(self, content):
        #If it's a private message from an authorized channel, channels are separated by , or ;
        if content.command == 'PRIVMSG' and content.args[0] in re.split('[\;\,]', config.channels()):
            self.formatMinecraftOutput(content.nick, content.args[1])
        return content

    def formatMinecraftOutput(self, nick, msg):
        self.rcon.send('say ' + nick + ': ' + me.sub(r'[\r\n]', '', msg) )

    def filterTCPToIRC(self, content):
        #rubin's regex's go here
        self.log.info('Craftoria: filterTCPToIRC (%s)'%content)
        return content

Class = Craftoria

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
