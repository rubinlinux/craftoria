#!/usr/bin/python

import sys
import email
import socket
import os.path

def parse_email(msgstr):
    message = email.message_from_string(msgstr)
    msg_id = message.get('Message-ID', 'Unknown')
    whose = message['Subject'].split()[1]

    # The message may have multiple parts
    for part in message.walk():
        if part.is_multipart():
            continue

        # The URL will hopefully be in first text/plain part
        if part.get_content_type().lower() != 'text/plain':
            continue

        payload = part.get_payload(decode=True)
        decoded = payload.decode(part.get_content_charset())

        for word in decoded.split():
            if word.startswith('http:'):
                url = str(word)
                break
        else:
            raise RuntimeError, 'No URL found'
        break

    else:
        raise RuntimeError, 'The message has no text/plain part'

    return (whose, url)

def get_address(arg):
    colon_pos = arg.rfind(':')
    if colon_pos != -1:
        addr = arg[:colon_pos]
        port = arg[colon_pos+1:]
        try:
            port = int(port)
        except ValueError:
            raise RuntimeError, 'Incorrect port number {0}'.format(port)
        return (socket.AF_INET, (addr, port))
    else:
        if not os.path.exists(arg):
            raise RuntimeError, 'Socket file {0} does not exist'.format(arg)
        return (socket.AF_UNIX, arg)

def send_data(af, addr, data):
    s = socket.socket(af, socket.SOCK_STREAM)
    s.connect(addr)
    s.sendall(data)
    s.close()

if __name__ == '__main__':
    try:
        (af, addr) = get_address(sys.argv[1])
        parsed = parse_email(sys.stdin.read())
        message = '{0} location: {1}'.format(parsed[0], parsed[1])
        send_data(af, addr, message)
    except Exception as e:
        sys.stderr.write('ERROR: {0}\n'.format(e))
