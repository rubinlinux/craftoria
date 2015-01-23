This plugin provides a by-directional link between a Minecraft server and IRC.

It consists of 2 parts:

--Part 1--

    The plugin continuously polls the Minecraft log file, watching for chat
    messages, player actions (/me), player deaths, etc, and echoing them to the
    assigned channel(s).

--Part 2--

    The plugin also relays messages sent to its assigned channel(s) to the
    Minecraft server. The plugin does this using RCON, which effectively is like
    typing directly into the Minecraft console.

Installation:

    1) Copy (or link) the 'Craftoria' directory to your bot's plugin directory.

    2) Configure the bot.
    
        First, set the channel (here, #mychan) to which the messages coming from
        Minecraft are relayed and the messages coming from IRC will be related
        from:

            !config channel #mychan supybot.plugins.Craftoria.announce on

        Next, you need to configure where the Minecraft server log file is
        located. You must use an absolute path to the log file, otherwise
        unpredictable things might happen.
        
            !config supybot.plugins.Craftoria.minecraft_server_location /path/to/minecraft_server/logs/latest.log
        
        Then, configure the rcon settings. Make sure the rcon_host matches the
        IP the Minecraft server listens on.

            !config supybot.plugins.Craftoria.rcon_host 127.0.0.1
            !config supybot.plugins.Craftoria.rcon_port 12345
            !config supybot.plugins.Craftoria.rcon_pass yoursecretpass
        
        By default, the plugin does not relay special actions such as game mode
        changes or teleportations. This can be changed as follows:
        
            !config supybot.plugins.Craftoria.special_actions on
        
    3) To avoid driving yourself nuts, it's best to reload the plugin and then
    restart the bot:
    
        !reload Craftoria
        quit
        (restart bot via your chosen method)

    4) Configure the Minecraft server.
    
        Edit server.properties and set the following parameters:
        
        enable-rcon=True
        rcon_port 12345
        rcon_password=yoursecretpass
        
        Restart your Minecraft server to make sure rcon is enabled.

Running:

    Once you have configured everything, start supybot and make sure Craftoria
    is loaded. If everything is configured properly, you should get relay
    traffic between Minecraft and IRC.

----------------------------

Tips:

    1) Do not make changes to the supybot's config while it is running. If it's
    running, make the changes via IRC, preferrably via query (private message).
    2) Restart your supybot any time you make changes to the config.

----------------------------

Created by rubin, ps and gholms of AfterNET #minecraft

Modified by Vadtec of AfterNET #minecraft

Based on mmilata's supy-msgpipe plugin (https://github.com/mmilata/supy-msgpipe) and barneygale's MCRcon
python library (https://github.com/barneygale/MCRcon)

----------------------------

Some useful links for working on this...

http://supybook.fealdia.org/devel/
http://doc.supybot.aperio.fr/en/latest/develop/index.html
http://sourceforge.net/p/supybot/code/ci/master/tree/docs/PLUGIN_TUTORIAL.rst
http://sourceforge.net/p/gribble/wiki/Supybot_Resources/#plugin-coding
