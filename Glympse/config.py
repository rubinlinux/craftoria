###
# Copyright (c) 2012, b42
# Published under WTFPL.
#
###

import supybot.conf as conf
import supybot.registry as registry

def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified himself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    from supybot.questions import expect, anything, something, yn
    conf.registerPlugin('Glympse', True)


Glympse = conf.registerPlugin('Glympse')
# This is where your configuration variables (if any) should go.  For example:
# conf.registerGlobalValue(Glympse, 'someConfigVariableName',
#     registry.Boolean(False, """Help for someConfigVariableName."""))

conf.registerGlobalValue(Glympse, 'unix',
    registry.Boolean(False, """Use UNIX domain socket instead of network
    socket."""))
conf.registerGlobalValue(Glympse, 'host',
    registry.String('localhost', """Hostname to listen on. Ignored if UNIX
    socket is used."""))
conf.registerGlobalValue(Glympse, 'port',
    registry.PositiveInteger(61739, """Port to listen on. Ignored if UNIX
    socket is used."""))
conf.registerGlobalValue(Glympse, 'socketFile',
    registry.String('glympse_socket', """Filename of the unix socket. Ignored
    if network socket is used."""))
    
conf.registerChannelValue(Glympse, 'announce',
    registry.Boolean(False, """Announce incoming Glympse to the channel."""))


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
