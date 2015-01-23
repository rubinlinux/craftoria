###
# Copyright (c) 2012, b42
# Published under WTFPL.
#
###

"""
Relays messages between MC and IRC.
"""

import supybot
import supybot.world as world

# Use this for the version of this plugin.  You may wish to put a CVS keyword
# in here if you're keeping the plugin in CVS or some similar system.
__version__ = "1.0"

# XXX Replace this with an appropriate author or supybot.Author instance.
__author__ = supybot.Author('rubin', 'rubin', 'AfterNET #minecraft')

# This is a dictionary mapping supybot.Author instances to lists of
# contributions.
supybot.authors.ps = supybot.Author('PseudoSean', 'ps', 'AfterNET #minecraft')
supybot.authors.gholms = supybot.Author('gholms', 'gholms', 'AfterNET #minecraft')
supybot.authors.vadtec = supybot.Author('Vadtec', 'Vadtec', 'AfterNET #minecraft')

__contributors__ = {
    supybot.authors.ps: ['Lots of stuff'],
    supybot.authors.gholms: ['Lots of stuff'],
    supybot.authors.vadtec: ['/me action from MC to IRC', 'Plugin reads MC log directly', 'Special actions from MC to IRC'],
    }


# This is a url where the most recent plugin package can be downloaded.
__url__ = 'https://github.com/rubinlinux/craftoria'

import config
import plugin
reload(plugin) # In case we're being reloaded.
# Add more reloads here if you add third-party modules and want them to be
# reloaded when this plugin is reloaded.  Don't forget to import them as well!

if world.testing:
    import test

Class = plugin.Class
configure = config.configure


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
