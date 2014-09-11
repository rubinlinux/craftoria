#!/usr/bin/perl

use strict;
use warnings;

use IO::Socket::INET;

my $msg = $ARGV[0];

# [21:35:25] [Server thread/INFO]: rubinlinux joined the game
#Remove timestamp and [Server] lines
$msg =~ s/^\[[0-9:]+\] \[[^]]+\]: //;

#Someone speaking
if( $msg =~ /^(\<.+\> .+)/ ) {
    $msg = $1;
}
elsif($msg =~ /^(\w+) joined the game/) {
    $msg =  "$1 connected";
}
elsif($msg =~ /^(\w+) left the game/) {
    $msg =  "$1 left";
}
elsif($msg =~ /^(\w+ has just earned the achievement.*)/) {
    $msg =  "-$1";
}
elsif($msg =~ /^(\w+ was slain by .*)/) {
    $msg =  "-$1";
}
elsif($msg =~ /^\[(Server|Rcon)\] (.+)/) {
    $msg =  ": $2";
}
#[00:08:37] [Server thread/INFO]: peaceenz suffocated in a wall

else {
#    print "                 DEBUG: skipping '$msg'\n";
    exit 0; #skip this line
}

$msg = "[simplanet] $msg";

#$msg =~ s/\'/\\\\\'/;
#print "DEBUG: $msg\n";

my $socket = new IO::Socket::INET (
    PeerHost => 'localhost',
    PeerPort => '23236',
    Proto => 'tcp',
);
die "cannot connect to the server $!\n" unless $socket;

my $size = $socket->send("$msg\n");
shutdown($socket, 1);
$socket->close();

#system("echo '[simplanet] $msg' |nc ender.afternet.org 23236");
#print "MSG: $msg\n";

