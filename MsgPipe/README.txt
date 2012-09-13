This plugin listens on a socket (either network or UNIX) for an email message
(piped to it by e.g. procmail) from Glympse [http://glympse.com/].  It then
parses the message and dumps the enclosed URL on a channel.  It has no commands
and requires a bit of a configuration to be useful.

Installation:

1) Copy (or link) the 'MsgPipe' directory to your bot's plugin directory.

2) Configure the bot. First, set the channel (here, #mychan) to which the
   incoming messages are announced:

      !config channel #mychan supybot.plugins.MsgPipe.announce on

   Next, you need to configure where will the plugin listen for the incoming
   messages. There are two possibilities: it can either use unix socket, or a
   network socket. The network socket is preferable if the machine receiving
   the email is not the same machine where the bot is running.

   Using unix socket:

      !config supybot.plugins.MsgPipe.unix on
      !config supybot.plugins.MsgPipe.socketFile /path/to/the/socket

   Using network socket:

      !config supybot.plugins.MsgPipe.unix off
      !config supybot.plugins.MsgPipe.host 0.0.0.0
      !config supybot.plugins.MsgPipe.port 12345

   This will make the bot listen on all interfaces/addresses on port 12345. You
   may also want to set up a firewall so that no one else than the machine on
   which the mail is received can connect

   You have to reload the plugin to actually change those settings.

      !reload MsgPipe

3) Configure the email delivery. Example procmail configuration file that
   writes all messages from glympse.com to bot's unix socket is provided.

   Note that netcat cannot be used instead of socat as it waits for the plugin
   to close connection and the plugin waits for the other side to close
   connection (because it does not know where the message ends), which results
   in timeout error.
