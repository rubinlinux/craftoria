###
# Copyright (c) 2012, b42
# Published under WTFPL.
#
###

import os
import sys
import email
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

class Glympse(callbacks.Plugin):
    """
    This plugin listens on a socket (either network or UNIX) for an email
    message (piped to it by e.g. procmail) from Glympse [http://glympse.com/].
    It then parses the message and dumps the enclosed URL on a channel.
    It has no commands and requires a bit of a configuration to be useful.
    """

    class ConnectionHandler(SocketServer.StreamRequestHandler):
        def handle(self):
            if type(self.client_address) == tuple:
                self.log.info('Glympse: network connect from: %s', self.client_address)

            try:
                msgstr = self.rfile.read()
                message = email.message_from_string(msgstr)
                msg_id = message.get('Message-ID', 'Unknown')
                whose = message['Subject'].split()[1]

                # The message may have multiple parts
                for part in message.walk():
                    if part.is_multipart():
                        continue

                    # The URL will hopefully be in first text/plain part
                    if part.get_content_type().lower() != 'text/plain':
                        continue

                    payload = part.get_payload(decode=True)
                    decoded = payload.decode(part.get_content_charset())

                    for word in decoded.split():
                        if word.startswith('http:'):
                            url = str(word)
                            break
                    else:
                        raise RuntimeError, 'No URL found'
                    break

                else:
                    raise RuntimeError, 'The message has no text/plain part'

                reply = "{0} location: {1}".format(whose, url)
            except:
                self.log.error('Glympse: exception %s: %s', sys.exc_type,
                        sys.exc_value)
                reply = "Something wrong happened when parsing glympse message, see log for details"

            # Announce the location to all configured channels
            for channel in self.irc.state.channels.keys():
                if conf.supybot.plugins.Glympse.announce.get(channel)():
                    self.irc.queueMsg(ircmsgs.privmsg(channel, reply))

    def __init__(self, irc):
        self.__parent = super(Glympse, self)
        self.__parent.__init__(irc)

        self.ConnectionHandler.irc = irc
        self.ConnectionHandler.log = self.log

        config = conf.supybot.plugins.Glympse
        self.unixsock = None

        if config.unix():
            self.unixsock = config.socketFile()
            self.server = SocketServer.UnixStreamServer(self.unixsock,
                    self.ConnectionHandler)
        else:
            host = config.host()
            port = config.port()
            self.server = SocketServer.TCPServer((host, port),
                    self.ConnectionHandler)

        t = threading.Thread(
                target = self.server.serve_forever,
                name = "GlympseThread"
            )
        t.setDaemon(True)
        t.start()
        world.threadsSpawned += 1

    def die(self):
        self.log.info('Glympse: shutting down socketserver')
        self.server.shutdown()
        self.server.server_close()

        if self.unixsock:
            os.unlink(self.unixsock)

        self.__parent.die()

Class = Glympse

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
