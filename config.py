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

conf.registerGlobalValue(Craftoria, 'servername',
    registry.String('minecraft', """Name of minecraft server. Used in announcements."""))

conf.registerGlobalValue(Craftoria, 'use_log4j',
    registry.Boolean(False, """If true, receive log info from the Minecraft
    server from the log4j facility, otherwise read the local log file."""))
    
conf.registerGlobalValue(Craftoria, 'log4j_host', registry.String('localhost',
    """The host/IP to listen on for log4j connections."""))
conf.registerGlobalValue(Craftoria, 'log4j_port', registry.String('25585',
    """The port to listen on for log4j connections."""))

conf.registerGlobalValue(Craftoria, 'minecraft_server_log',
    registry.String('/path/to/minecraft_server/logs/latest.log',
    """The absolute path to the Minecraft server log file."""))

conf.registerGlobalValue(Craftoria, 'special_actions',
    registry.Boolean(False, """Show special actions such as players changing
    game mode or teleportation."""))

conf.registerGlobalValue(Craftoria, 'rcon_host', registry.String('localhost', """rcon_host. """))
conf.registerGlobalValue(Craftoria, 'rcon_port', registry.PositiveInteger(25575, """rcon_port. """))
conf.registerGlobalValue(Craftoria, 'rcon_pass', registry.String('password', """rcon_pass. """))

conf.registerChannelValue(Craftoria, 'announce',
    registry.Boolean(False, """Announce incoming message to the channel."""))


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
