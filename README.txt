[1]

This plugin provides a by-directional link between a Minecraft server and IRC.

It consists of 2 parts:

[1.1]

    The plugin does one of two things:
    
    [1.1.1] continuously polls the Minecraft log file, watching for chat
    messages, player actions (/me), player deaths, etc, and echoing them to the
    assigned channel(s).
    
    [1.1.2] receives log messages from log4j2, watching for chat
    messages, player actions (/me), player deaths, etc, and echoing them to the
    assigned channel(s).

[1.2]

    The plugin also relays messages sent to its assigned channel(s) to the
    Minecraft server. The plugin does this using RCON, which effectively is like
    typing directly into the Minecraft console.

[2]

Installation:

    [2.1] Copy (or link) the 'Craftoria' directory to your bot's plugin directory.

    [2.2] Configure the bot.
        
        [2.2.1] Configuring the bots IRC channels
        
        First, set the channel (here, #mychan) to which the messages coming from
        Minecraft are relayed and the messages coming from IRC will be related
        from:

            !config channel #mychan supybot.plugins.Craftoria.announce on

        [2.2.2] Using the Minecraft server log file
        
        Next, if you are going to use the Minecraft server log file, you need to
        configure where the Minecraft server log file is located. You should use
        an absolute path to the log file, otherwise unpredictable things might
        happen.
        
            !config supybot.plugins.Craftoria.minecraft_server_log /path/to/minecraft_server/logs/latest.log
        
        [2.2.3] Using log4j2 built into the Minecraft server
        
        [2.2.3.1] log4j2.xml
        
        If you are going to use log4j2 on the server, you need to edit the
        log4j2.xml file and set the host and port parameters of the Socket
        directive. The host will be the IP/host of the bot receiving the log
        entries from the Minecraft server. DO NOT set the protocol to anything
        other than UDP, because the bot only accepts log4j2 connections via UDP.
        Once you have edited the file, put it in the Minecraft server directory.
        When you run your Minecraft server, add
        -Dlog4j.configurationFile=log4j2.xml
        to your command for running the server BEFORE the -jar option. This will
        enable log4j2 and allow it to start sending log messages to the bot.
        
            !config supybot.plugins.Craftoria.use_log4j on
            !config supybot.plugins.Craftoria.log4j_host 0.0.0.0
            !config supybot.plugins.Craftoria.log4j_port 25585

        [2.2.3.2] In order to secure the bot and prevent malicious use, you will
        need to configure the IP that is allowed to send log traffic to the bot.
        This will be the IP of the Minecraft server sending the log traffic.
        
            !config supybot.plugins.Craftoria.log4j_host_accept 127.0.0.1
        
        [2.2.3.2.1] If traffic is received from an IP other than the one
        configured, it is simply ignored. No response is given, nothing is
        logged, the traffic simply disappears into the void.
        
        [2.2.3.3] If the bot is not running it will not cause a problem,
        because log4j2 will silently ignore failures to send the log messages.
        
        [2.2.4] RCON settings
        
        Then, configure the rcon settings. Make sure the rcon_host matches the
        IP the Minecraft server listens on.

            !config supybot.plugins.Craftoria.rcon_host 127.0.0.1
            !config supybot.plugins.Craftoria.rcon_port 12345
            !config supybot.plugins.Craftoria.rcon_pass yoursecretpass
        
        [2.2.5] Special Minecraft actions
        
        By default, the plugin does not relay special actions such as game mode
        changes or teleportations. This can be changed as follows:
        
            !config supybot.plugins.Craftoria.special_actions on
        
    [2.3] To avoid driving yourself nuts, it's best to reload the plugin and then
    restart the bot:
    
        !reload Craftoria
        quit
        (restart bot via your chosen method)

    [2.4] Configure the Minecraft server.
    
        Edit server.properties and set the following parameters:
        
        enable-rcon=True
        rcon_port 12345
        rcon_password=yoursecretpass
        
        Restart your Minecraft server to make sure rcon is enabled.

[3]

Running:

    Once you have configured everything, start supybot and make sure Craftoria
    is loaded. If everything is configured properly, you should get relay
    traffic between Minecraft and IRC.

----------------------------

[4]

Tips:

    [4.1] Do not make changes to the supybot's config while it is running. If it's
    running, make the changes via IRC, preferrably via query (private message).
    [4.2] Restart your supybot any time you make changes to the config.

----------------------------

[5]

Created by rubin, ps and gholms of AfterNET #minecraft

Modified by Vadtec of AfterNET #minecraft

Based on mmilata's supy-msgpipe plugin (https://github.com/mmilata/supy-msgpipe)
and barneygale's MCRcon python library (https://github.com/barneygale/MCRcon)

----------------------------

[6]

Some useful links for working on this...

http://supybook.fealdia.org/devel/
http://doc.supybot.aperio.fr/en/latest/develop/index.html
http://sourceforge.net/p/supybot/code/ci/master/tree/docs/PLUGIN_TUTORIAL.rst
http://sourceforge.net/p/gribble/wiki/Supybot_Resources/#plugin-coding

----------------------------

[7]

Minecraft<->IRC nick mapping

This plugin has a simple feature for mapping Minecraft player names to IRC
nicknames. While it currently doesn't do anything with UUIDs, the plugin tracks
Minecraft UUIDs. When a Minecraft user name changes, the plugin will
automatically update the Minecraft user name the next time the user connects.

These commands can be used by any user:

[7.1] !mcnicks [MC nick] - Lists all known IRC nicks for all Minecraft players, or
    the given Minecraft player

These commands require admin or higher access to the bot, to prevent spamming:

[7.2] !mcnickadd <MC nick> <IRC nick> - Adds the given IRC nick to the given
    Minecraft player

[7.3] !mcnickdel <MC nick> <IRC nick> - Removes the given IRC nick from the given
    Minecraft player

[7.4] !mcnickchange <MC old> <MC new> - Changes the old Minecraft player to the new
    Minecraft player