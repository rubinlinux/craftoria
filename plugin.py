###
# Copyright (c) 2014, 2015, Afternet.org, #minecraft
# Published under WTFPL.
#
###

import os
import sys
import threading
import SocketServer
import time
import datetime
import json
import copy

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
    This plugin continuously reads the Minecraft log file and processes the
    contents of the file, or receives the log entries via log4j2, dumping
    messages to the configured channel(s). It has no commands and needs to know
    the location of the Minecraft log file.
    """
    
    class UDPConnectionHandler(SocketServer.BaseRequestHandler):
        def handle(self):
            data = self.request[0].strip()
            client = self.client_address[0]
            
            # if the client sending the data is allowed, process it, otherwise
            # do nothing
            # (don't respond, don't acknowledge, don't process, simply ignore it)
            # TODO: support CIDR
            if str(client) == str(self.config.log4j_host_accept):
                self.handle_message(data.strip(","), True)
    
    def __init__(self, irc):
        self.__parent = super(Craftoria, self)
        self.__parent.__init__(irc)
        
        self.data_dir = conf.supybot.directories.data
        self.mc_irc_data_file = '%s/mc_irc_nicks.json' % self.data_dir
        
        self.mcnicks_check_data_file()
        
        self.irc = irc
        self.log_read = True # so we can bail out later if necessary
        self.log4j_read = True # so we can bail out later if necessary
        
        self.config = conf.supybot.plugins.Craftoria
        
        self.special_actions = self.config.special_actions()
        self.use_log4j = self.config.use_log4j()
        
        if self.use_log4j:
            self.UDPConnectionHandler.irc = self.irc
            self.UDPConnectionHandler.log = self.log
            self.UDPConnectionHandler.handle_message = self.handle_message
            self.UDPConnectionHandler.config = self.config
        
            self.log4j_host = self.config.log4j_host()
            if self.log4j_host == None:
                raise "Configuration not complete - Minecraft server 'log4j_host' DNS/IP not set"
            self.log4j_port = int(self.config.log4j_port())
            if self.log4j_port == None:
                raise "Configuration not complete - Minecraft server 'log4j_port' port number not set"
            self.log4j_host_accept = self.config.log4j_host_accept()
            if self.log4j_host_accept == None:
                raise "Configuration not complete - Minecraft server 'log4j_host_accept' IP not set"
        else:
            self.mc_log = self.config.minecraft_server_log()
            if self.mc_log == None:
                raise "Configuration not complete - Minecraft server 'minecraft_server_log' path not set"
            
        self.rcon_host = self.config.rcon_host()
        if self.rcon_host == None:
            raise "Configuration not complete - Minecraft server 'rcon_host' DNS/IP not set"
        self.rcon_port = int(self.config.rcon_port())
        if self.rcon_port == None:
            raise "Configuration not complete - Minecraft server 'rcon_port' port number not set"
        self.rcon_pass = self.config.rcon_pass()
        if self.rcon_pass == None:
            raise "Configuration not complete - Minecraft server 'rcon_pass' password not set"
        self.rcon = mcrcon.MCRcon(self.rcon_host, self.rcon_port, self.rcon_pass) 
        if self.rcon:
            self.log.info('Craftoria: successfully connected to rcon')
        else:
            raise "Connection to Minecraft server using rcon impossible"
            self.log.info('Craftoria: could not connect to rcon')
        
        if self.use_log4j:
            self.server = SocketServer.UDPServer((self.log4j_host, self.log4j_port), self.UDPConnectionHandler)
            
            t = threading.Thread(
                    target = self.server.serve_forever,
                    name = "CraftoriaThread"
                )
            t.setDaemon(True)
            t.start()
            world.threadsSpawned += 1
        else:
            t = threading.Thread(
                    target = self.read_forever,
                    name = "CraftoriaThread"
                )
            t.setDaemon(True)
            t.start()
            world.threadsSpawned += 1
    
    def clean(self, content):
        return re.sub(r'[\r\n]', '', content)
    
    def die(self):
        self.rcon.close()
        self.log.info('Craftoria: shutting down socketserver')
        self.log_read = False
        self.log4j_read = False

        self.__parent.die()
    
    def read_forever(self):
        """
        This function reads the log file one line at a time, reopening it if it
        changes (due to logrotate for example).
        This function will loop until the program ends or is explicitly told to
        stop reading the log file.
        """
        try:
            self.mc_log_fh = open(self.mc_log, 'r')
            
            self.curinode = os.fstat(self.mc_log_fh.fileno()).st_ino
            
            while self.log_read:
                while self.log_read:
                    self.buf = self.mc_log_fh.readline()
                    if self.buf == "":
                        break
                    
                    self.handle_message(self.buf, False)
                try:
                    if os.stat(self.mc_log).st_ino != self.curinode:
                        self.mc_new_fh = open(self.mc_log, "r")
                        self.mc_log_fh.close()
                        self.mc_log_fh = self.mc_new_fg
                        self.curinode = os.fstat(self.mc_log_fh.fileno()).st_ino
                        continue # dont bother sleeping since there is a new log file
                except IOError:
                    pass
                time.sleep(0.1)
        except:
            self.log.error('Craftoria: unable to open or read log file %s: %s',
                sys.exc_type, sys.exc_value)
    
    def handle_message(self, message, json_format=False):
        if json_format:
            data = json.loads(message)
            message = self.filterLogToIRC(self.clean(data['message']))
        else:
            message = self.filterLogToIRC(self.clean(message))
        
        if message:
            # Announce the location to all configured channels
            for channel in self.irc.state.channels.keys():
                if conf.supybot.plugins.Craftoria.announce.get(channel)():
                    #print channel, message
                    message = "[%s] %s" % (conf.supybot.plugins.Craftoria.servername, message)
                    self.irc.queueMsg(ircmsgs.privmsg(channel, message))
    
    def filterLogToIRC(self, message):
        #rubin's regex's go here
        message = re.sub(r'^\[[0-9:]+\] \[[^]]+\]: ', '', message)

        m = ReCheck()
        # chat msgs
        if m.check(r'^(\<.+\> .+)$', message):
            return m.result.group(1)
        elif m.check(r'^(\[Rcon\] .+)$', message):
            return False  #dont ever act on rcon since it could get us in a loop
        elif m.check(r'^(\[.+\] .+)$', message):
            return m.result.group(1)
        
        # join part
        elif m.check(r'(\w+) joined the game', message):
            return "- %s connected"%m.result.group(1)
        elif m.check(r'(\w+) left the game', message):
            return "- %s left"%m.result.group(1)
        
        # actions (/me)
        elif m.check(r'(\*.*)', message):
            return "%s" % m.result.group(1)
        
        # not white-listed
        elif m.check(r'^com\.mojang\.authlib.*name\=([^,]+).*\(\/([0-9.]+).*lost connection\: You are not white-listed', message):
            return "- Connection from %s rejected (not whitelisted: '%s')"%(m.result.group(2), m.result.group(1))
        
        # achievements
        elif m.check(r'^(\w+ has just earned the achievement.*)', message):
            return "- %s"%m.result.group(1)
        
        # special actions
        elif m.check(r'\[(.*: .*)\]', message):
            return False
            # This is letting exception strings slip through!
            #if self.special_actions:
            #    return m.result.group(1)
            #else:
            #    return False
        
        # UUID mapping for nicks
        elif m.check(r'UUID of player (.*) is ([0-9a-zA-Z-]+)', message):
            self.mcnicks_check_add_nick_on_join(m.result.group(1), m.result.group(2))
        
        # things to ignore
        elif m.check(r'.*\[/[0-9\.:]+\] logged in with entity id [0-9]+ at \(.*\)', message) or \
            m.check(r'.* lost connection:.*', message):
            return False
        
        #Deaths
        else:
            phrases = [
                r'^\w+ was slain',
                r'^\w+ suffocated',
                r'^\w+ was blown up',
                r'^\w+ withered away',
                r'^\w+ fell out',
                r'^\w+ fell from a high place',
                r'^\w+ was knocked into the void',
                r'^\w+ was pummeled by',
                r'^\w+ starved to death',
                r'^\w+ got finished off',
                r'^\w+ tried to swim in lava',
                r'^\w+ was shot',
                r'^\w+ was killed',
                r'^\w+ died',
                r'^\w+ was struck by lightning',
                r'^\w+ was squashed',
                r'^\w+ was fireballed by',
                r'^\w+ went up in flames',
                r'^\w+ burned to death',
                r'^\w+ was burnt to a crisp',
                r'^\w+ walked into a fire',
                r'^\w+ hit the ground too hard',
                r'^\w+ fell off',
                r'^\w+ fell into',
                r'^\w+ was doomed to fall',
                r'^\w+ was blown from a high place',
                r'^\w+ drowned.*$',
            ]

            for x in phrases:
                try:
                    m = re.search(x, message)
                    if m:
                        return "- %s"%message
                except(E):
                    self.log.info(str(E))

            #if no match then debug it
            self.log.info('DEBUG: no match on (%s)'%message)

        return False
    
    def inFilter(self, irc, msg):
        return self.filterIRCToRCON(msg);
    
    def filterIRCToRCON(self, content):
        #If it's a private message from an authorized channel, channels are separated by , or ;
        if content.command == 'PRIVMSG' and conf.supybot.plugins.Craftoria.announce.get(content.args[0])():
            if re.search(ur'^[\u0001]ACTION\s?(.*)[\u0001]$', content.args[1], re.UNICODE):
                self.formatMinecraftActionOutput(content.nick, content.args[1])
            else:
                self.formatMinecraftOutput(content.nick, content.args[1])
        return content

    def formatMinecraftActionOutput(self, nick, action):
        output = 'say * ' + self.clean(nick) + ' ' + self.clean(re.sub(ur'^[\u0001]ACTION\s?(.*)[\u0001]$', r'\1', action, re.UNICODE))
        self.rcon.send(output)
        #print output

    def formatMinecraftOutput(self, nick, msg):
        output = 'say <' + self.clean(nick) + '> ' + self.clean(msg)
        self.rcon.send(output)
        # print "DEBUG: Formatted output %s"%output

    # BEGIN RCON Commands
    def cmd(self, irc, msg, args, command):
        """
        Passes commands directly to RCON.
        """

        irc.reply(self.rcon.send(command))
    cmd = wrap(cmd, ['admin', 'text'])
    
    def whitelist(self, irc, msg, args, command):
        """
        White list related commands.
        """
        
        irc.reply(self.rcon.send("whitelist %s" % command))
    whitelist = wrap(whitelist, ['admin', optional('text')])
    
    def players(self, irc, msg, args):
        """
        Lists players connected to minecraft server
        """

        irc.reply(self.rcon.send("list"))
    players = wrap(players, [])
    # END RCON Commands
    
    # BEGIN Minecraft<->IRC nick association
    #
    # This code is used to associate any number of IRC nicks with a single
    # Minecraft nick. The intent behind this is to allow the bot to help track
    # which IRC users are which player in Minecraft.
    #
    # Due to the nature of this list, there is no easy way to check it for
    # integrity. Any errors in the list will need to be handled by the bot
    # admins/owner.
    #
    # The data for these commands are stored in simple text files in JSON
    # format within the configured data directory.
    # (supybot.directories.data)
    #
    # The intent of this code is not to mangle the names used when relaying
    # messages between Minecraft and IRC, but instead to provide a simple way
    # for users to find out who on Minecraft is who on IRC and vice versa.
    #
    def mcnicks_check_data_file(self):
        # these are needed to make sure the data file is consistent
        self.mcnicks_version = 2
        self.mcnicks_version2_data = {"version": 2, "Minecraft": {}, "UUID": {}}
        self.mcnicks_version2_nick_data = {"preferred": "", "irc_nicks": [], 'last_seen': -1}
        
        # Check to see if the Minecraft<->IRC nicks data file exists, creating
        # it if it doesn't.
        if not os.path.exists(self.mc_irc_data_file):
            self.log.info("Creating version 1 Minecraft<->IRC data file")
            
            with open(self.mc_irc_data_file, 'a') as f:
                f.close()
        
        # make sure the Minecraft<->IRC nicks data file is in the correct format
        with open(self.mc_irc_data_file, 'r') as f:
            data = f.read()
        
        try:
            data = json.loads(data)
        except ValueError:
            data = {}
        
        # BEGIN VERSION 1 conversion
        if "version" not in data:
            self.log.info("Converting Minecraft<->IRC data file to version 2\n")
            
            temp_data = self.mcnicks_version2_data
            
            for nick in data:
                self.log.info("Converting Minecraft nick %s to version 2\n" % nick)
                
                if nick not in temp_data['Minecraft']:
                    temp_data['Minecraft'][nick] = copy.deepcopy(self.mcnicks_version2_nick_data)
                
                temp_data['Minecraft'][nick]['irc_nicks'] = data[nick]
            
            data = temp_data
        # END VERSION 1 conversion
        
        data = json.dumps(data)
            
        with open(self.mc_irc_data_file, 'w') as f:
            f.write(data)
    
    def mcnicks_check_add_nick_on_join(self, nick, uuid):
        with open(self.mc_irc_data_file, 'r') as f:
            data = f.read()
        
        data = json.loads(data)
        
        if data['version'] == 2:
            # handle new users connecting
            if uuid not in data['UUID']:
                data['UUID'][uuid] = nick
                
                if nick not in data['Minecraft']:
                    data['Minecraft'][nick] = copy.deepcopy(self.mcnicks_version2_nick_data)
            
            # handle nick changes from the MC side
            if data['UUID'][uuid] != nick:
                old_nick = data['UUID'][uuid]
                data['UUID'][uuid] = nick
                
                if nick not in data['Minecraft']:
                    data['Minecraft'][nick] = data['Minecraft'][old_nick]
                    del data['Minecraft'][old_nick]
            
            data['Minecraft'][nick]['last_seen'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        data = json.dumps(data)
            
        with open(self.mc_irc_data_file, 'w') as f:
            f.write(data)
    
    def mcnicks(self, irc, msg, args, mc_nick=None):
        """
        Lists all Minecraft nicks, or the given Minecraft nick, and their
        associated IRC nicks.
        """
        
        with open(self.mc_irc_data_file, 'r') as f:
            data = f.read()
        
        data = json.loads(data)
        
        if data['version'] == self.mcnicks_version:
            # build the list of known MC<->IRC nicks
            nick_list = {}
            
            for nick in data['Minecraft']:
                if len(data['Minecraft'][nick]['irc_nicks']) > 0:
                    nick_list[nick] = data['Minecraft'][nick]['irc_nicks']
            
            if mc_nick:
                if mc_nick in nick_list:
                    nicks = []
                    for nick in nick_list[mc_nick]:
                        nicks.append(nick)
                    
                    irc.reply("Minecraft player %s is known by these nicknames on IRC: %s" % (mc_nick, ", ".join(nicks)))
                else:
                    irc.reply("I do not know who Minecraft player %s is" % mc_nick)
            else:
                if len(nick_list) > 0:
                    irc.reply("I know the following Minecraft players by the following IRC nicks:")
                    
                    lines = []
                    for mc_nick in nick_list:
                        nicks = []
                        for nick in nick_list[mc_nick]:
                            nicks.append(nick)
                        
                        lines.append("%s: %s" % (mc_nick, ", ".join(nicks)))
                    
                    temp_lines = []
                    temp_len = 0
                    
                    temp = ""
                    for line in lines:
                        if temp_len + len(line) < 200:
                            temp_len = temp_len + len(line)
                            temp_lines.append(line)
                        else:
                            irc.reply(" | ".join(temp_lines))
                            temp_len = len(line)
                            temp_lines = []
                            temp_lines.append(line)
                    
                    if len(temp_lines) > 0:
                        irc.reply(" | ".join(temp_lines))
                else:
                    irc.reply("No Minecraft player<->IRC nickname mappings")
        else:
            # this should never be reached, if it is, someone is screwing with
            # the data file, shame on them
            irc.reply("Minecraft player<->IRC data file error. Please contact the admins.")
    mcnicks = wrap(mcnicks, [optional('text')])
    
    def mcnickadd(self, irc, msg, args, mc_nick, irc_nick):
        """
        Adds an IRC nick to a Minecraft nick. Multiple IRC nicks can be added
        to a single Minecraft nick.
        If the mc_nick does not exist it is added to the list.
        """
        
        with open(self.mc_irc_data_file, 'r') as f:
            data = f.read()
        
        data = json.loads(data)
        
        if data['version'] == self.mcnicks_version:
            if mc_nick in data['Minecraft']:
                if irc_nick not in data['Minecraft'][mc_nick]['irc_nicks']:
                    data['Minecraft'][mc_nick]['irc_nicks'].append(irc_nick)
                    irc.reply("Minecraft player %s mapped to IRC nick %s" % (mc_nick, irc_nick))
                else:
                    irc.reply("I already know Minecraft player %s by IRC nick %s" %(mc_nick, irc_nick))
            else:
                # the Minecraft nick doesn't exist yet, create it
                data['Minecraft'][mc_nick] = copy.deepcopy(self.mcnicks_version2_nick_data)
                data['Minecraft'][mc_nick]['irc_nicks'].append(irc_nick)
                
                irc.reply("Minecraft player %s mapped to IRC nick %s" % (mc_nick, irc_nick))
        else:
            # this should never be reached, if it is, someone is screwing with
            # the data file, shame on them
            irc.reply("Minecraft player<->IRC data file error. Please contact the admins.")
            
        data = json.dumps(data)
            
        with open(self.mc_irc_data_file, 'w') as f:
            f.write(data)
    mcnickadd = wrap(mcnickadd, ['admin', 'something', 'something'])
    
    def mcnickdel(self, irc, msg, args, mc_nick, irc_nick):
        """
        Deletes an IRC nick from a Minecraft nick.
        If the mc_nick becomes empty after deleting irc_nick, it is removed
        from the list.
        """
        
        with open(self.mc_irc_data_file, 'r') as f:
            data = f.read()
        
        data = json.loads(data)
        
        if data['version'] == self.mcnicks_version:
            if mc_nick in data['Minecraft']:
                if irc_nick in data['Minecraft'][mc_nick]['irc_nicks']:
                    data['Minecraft'][mc_nick]['irc_nicks'].remove(irc_nick)
                    irc.reply("I no longer know Minecraft player %s as IRC nick %s" % (mc_nick, irc_nick))
                else:
                    irc.reply("I did not know Minecraft player %s as IRC nick %s to being with" % (mc_nick, irc_nick))
            else:
                irc.reply("I do not know who Minecraft player %s is")
        else:
            # this should never be reached, if it is, someone is screwing with
            # the data file, shame on them
            irc.reply("Minecraft player<->IRC data file error. Please contact the admins.")
        
        data = json.dumps(data)
            
        with open(self.mc_irc_data_file, 'w') as f:
            f.write(data)
    mcnickdel = wrap(mcnickdel, ['admin', 'something', 'something'])
    
    def mcnickchange(self, irc, msg, args, mc_old, mc_new):
        """
        Changes a Minecraft nick from it's old entry to it's new entry.
        (To support the future nick change feature of Minecraft.)
        """
        
        with open(self.mc_irc_data_file, 'r') as f:
            data = f.read()
        
        data = json.loads(data)
        
        if data['version'] == self.mcnicks_version:
            if mc_old in data['Minecraft']:
                data['Minecraft'][mc_new] = data['Minecraft'][mc_old]
                del data['Minecraft'][mc_old]
                
                for uuid in data['UUID']:
                    if data['UUID'][uuid] == mc_old:
                        data['UUID'][uuid] = mc_new
                
                irc.reply("I now know Minecraft player %s as Minecraft player %s" % (mc_old, mc_new))
            else:
                irc.reply("I do not know who Minecraft player %s is" % mc_old)
        else:
            # this should never be reached, if it is, someone is screwing with
            # the data file, shame on them
            irc.reply("Minecraft player<->IRC data file error. Please contact the admins.")
        
        data = json.dumps(data)
            
        with open(self.mc_irc_data_file, 'w') as f:
            f.write(data)
    mcnickchange = wrap(mcnickchange, ['admin', 'something', 'something'])
    # END Minecraft<->IRC nick association

Class = Craftoria

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
