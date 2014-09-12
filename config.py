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
    conf.registerPlugin('Craftoria', True)


Craftoria = conf.registerPlugin('Craftoria')
# This is where your configuration variables (if any) should go.  For example:
# conf.registerGlobalValue(Craftoria, 'someConfigVariableName',
#     registry.Boolean(False, """Help for someConfigVariableName."""))

conf.registerGlobalValue(Craftoria, 'unix',
    registry.Boolean(False, """Use UNIX domain socket instead of network
    socket."""))
conf.registerGlobalValue(Craftoria, 'host',
    registry.String('localhost', """Hostname to listen on. Ignored if UNIX
    socket is used."""))
conf.registerGlobalValue(Craftoria, 'port',
    registry.PositiveInteger(61739, """Port to listen on. Ignored if UNIX
    socket is used."""))
conf.registerGlobalValue(Craftoria, 'channels',
    registry.String('#minecraft', """Channel list to listen on, separate by comma or semicolor - [,;]."""))
conf.registerGlobalValue(Craftoria, 'rcon_host', registry.String('localhost', """rcon_host. """))
conf.registerGlobalValue(Craftoria, 'rcon_port', registry.String('localhost', """rcon_port. """))
conf.registerGlobalValue(Craftoria, 'rcon_pass', registry.String('localhost', """rcon_pass. """))
#conf.registerGlobalValue(Craftoria, 'socketFile',
#    registry.String('craftoria_socket', """Filename of the unix socket. Ignored
#    if network socket is used."""))
    
conf.registerChannelValue(Craftoria, 'announce',
    registry.Boolean(False, """Announce incoming message to the channel."""))


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
