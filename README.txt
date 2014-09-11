This plugin provides a by-directional link between a vanilla minecraft server and IRC.

It consists of 2 parts:

--Part 1--
Listens on a socket (either TCP or UNIX) and whenever someone sends
a message to the socket, it dumps it to a channel.  It has no commands and
requires a bit of a configuration to be useful. Included scripts in tools/ can follow 
the minecraft log, and forward important bits (like chat) to this plugin.

--Part 2--
Watch irc for PRIVMSG to a channel, and use an established RCON link to 'say' chat
to the minecraft console. 

Installation:

1) Copy (or link) the 'Craftoria' directory to your bot's plugin directory.

2) Configure the bot. First, set the channel (here, #mychan) to which the
   incoming messages are announced:

      !config channel #mychan supybot.plugins.Craftoria.announce on

   Next, you need to configure where will the plugin listen for the incoming
   messages. There are two possibilities: it can either use unix socket, or a
   network socket. The network socket is preferable if the machine receiving
   the email is not the same machine where the bot is running.

   Using unix socket:

      !config supybot.plugins.Craftoria.unix on
      !config supybot.plugins.Craftoria.socketFile /path/to/the/socket

   Using network socket:

      !config supybot.plugins.Craftoria.unix off
      !config supybot.plugins.Craftoria.host 0.0.0.0
      !config supybot.plugins.Craftoria.port 12345

   This will make the bot listen on all interfaces/addresses on port 12345. You
   may also want to set up a firewall so that no one else than the machine on
   which the mail is received can connect

      !config supybot.plugins.Craftoria.rcon_host 127.0.0.1
      !config supybot.plugins.Craftoria.rcon_port 12345
      !config supybot.plugins.Craftoria.rcon_pass yoursecretpas
     

   You have to reload the plugin to actually change those settings.

      !reload Craftoria


  Copy logwatch.sh and send.pl from tools/ into your minecraft log directory. Then run ./logwatch.sh


  Edit server.properties and enable rcon. enable-rcon, rcon.password, rcon.port all need configured. Restart
  your server to take effect.


----------------------------

Created by rubin, ps and gholms of AfterNET #minecraft

Based on mmilata's supy-msgpipe plugin (https://github.com/mmilata/supy-msgpipe) and barneygale's MCRcon
python library (https://github.com/barneygale/MCRcon)


----------------------------

Some useful links for working on this...

http://supybook.fealdia.org/devel/
http://doc.supybot.aperio.fr/en/latest/develop/index.html
http://sourceforge.net/p/supybot/code/ci/master/tree/docs/PLUGIN_TUTORIAL.rst
http://sourceforge.net/p/gribble/wiki/Supybot_Resources/#plugin-coding


