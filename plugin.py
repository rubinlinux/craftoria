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

class ReCheck(object):
    def __INIT__(self):
        self.result = None
    def check(self, pattern, text):
        self.result = re.search(pattern, text)
        return self.result

class Craftoria(callbacks.Plugin):
    """
    This plugin listens on a socket (either TCP or UNIX) and whenever
    someone sends a message to the socket, it dumps it to a channel.
    It has no commands and requires a bit of a configuration to be useful.
    """

    class ConnectionHandler(SocketServer.StreamRequestHandler):
        def handle(self):
            if type(self.client_address) == tuple:
                self.log.info('Craftoria.ConnectionHandler: network connect from: %s', self.client_address)

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
                    message = self.filterTCPToIRC(reply)
                    if message:
                        #print channel, message
                        message = "[%s] %s"%(conf.supybot.plugins.Craftoria.servername, message)
                        self.irc.queueMsg(ircmsgs.privmsg(channel, message))
                        
        def filterTCPToIRC(self, message):
            #rubin's regex's go here

            m = ReCheck()
            if (m.check(r'^(\<.+\> .+)$', message)):
                return m.result.group(1)
            elif (m.check(r'^(\[Rcon\] .+)$', message)):
                return False  #dont ever act on rcon since it could get us in a loop
            elif (m.check(r'^(\[.+\] .+)$', message)):
                return m.result.group(1)
            elif (m.check(r'(\w+) joined the game', message)):
                return "- %s connected"%m.result.group(1)
            elif (m.check(r'(\w+) left the game', message)):
                return "- %s left"%m.result.group(1)
            elif (m.check(r'^com\.mojang\.authlib.*name\=([^,]+).*\(\/([0-9.]+).*lost connection\: You are not white-listed', message)):
                return "- Connection from %s rejected (not whitelisted: '%s')"%(m.result.group(2), m.result.group(1))
            #achievements
            elif (m.check(r'^(\w+ has just earned the achievement.*)', message)):
                return "- %s"%m.result.group(1)

            #Deaths
            elif (m.check(r'^(\w+ was slain by .*)', message)):
                return "- %s"%m.result.group(1)
            elif (m.check(r'^(\w+ suffocated .*)', message)):
                return "- %s"%m.result.group(1)
            
            else:
                self.log.info('DEBUG: no match on (%s)'%message)

            return False


    def __init__(self, irc):
        self.__parent = super(Craftoria, self)
        self.__parent.__init__(irc)

        self.ConnectionHandler.irc = irc
        self.ConnectionHandler.log = self.log

        config = conf.supybot.plugins.Craftoria
        self.unixsock = None

        host = config.rcon_host()
        if host == None:
            raise "Configuration not complete - Minecraft server 'rcon_host' DNS/IP not set"
        port = int(config.rcon_port())
        if port == None:
            raise "Configuration not complete - Minecraft server 'rcon_port' port number not set"
        rconpass = config.rcon_pass()
        if rconpass == None:
            raise "Configuration not complete - Minecraft server 'rcon_pass' password not set"
        self.rcon = mcrcon.MCRcon(host, port, rconpass) 
        if self.rcon:
            self.log.info('Craftoria: successfully connected to rcon')
        else:
            raise "Connection to Minecraft server using rcon impossible"
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
        #return True


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
        if conf.supybot.plugins.Craftoria.announce.get(content.args[0])() and content.command == 'PRIVMSG':
            if re.search(ur'^[\u0001]ACTION\s?(.*)[\u0001]$', content.args[1], re.UNICODE):
                self.formatMinecraftActionOutput(content.nick, content.args[1])
            else:
                self.formatMinecraftOutput(content.nick, content.args[1])
        return content

    def formatMinecraftActionOutput(self, nick, msg):
        output = 'say * ' + self.clean(nick) + ' ' + self.clean(re.sub(ur'^[\u0001]ACTION\s?(.*)[\u0001]$', r'\1', msg, re.UNICODE))
        self.rcon.send(output)
        #print output

    def formatMinecraftOutput(self, nick, action):
        output = 'say <' + self.clean(nick) + '> ' + self.clean(action)
        self.rcon.send(output)
        print "DEBUG: Formatted output %s"%output
        
    def clean(self, content):
        return re.sub(r'[\n\r]', '', content)
        

Class = Craftoria

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
