import socket
import select
import struct
import re

class MCRconException (Exception):
    def __new__(cls, *args, **kwArgs):
        return super(MCRconException, cls).__new__(*args, **kwArgs)

class MCRcon:
    def __init__(self, host, port, password):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.password = password
        self.connect()
        
    def connect(self):
        self.s.connect((self.host, self.port))
        self.send_real(3, self.password)
    
    def close(self):
        self.s.close()
    
    def send(self, command, retries=3):
        if retries <= 0:
            raise Exception("Couldn't transmit message, couldn't reconnect")
        try:
            return self.send_real(2, command)
        except MCRconException:
            self.send(command, retries-1)
    
    def send_real(self, out_type, out_data):
        #Send the data
        buff = struct.pack('<iii', 
            10+len(out_data),
            0,
            out_type) + out_data + "\x00\x00"
        self.s.send(buff)
        
        #Receive a response
        in_data = ''
        ready = True
        while ready:
            #Receive an item
            tmp_len, tmp_req_id, tmp_type = struct.unpack('<iii', self.s.recv(12))
            tmp_data = self.s.recv(tmp_len-8) #-8 because we've already read the 2nd and 3rd integer fields

            #Error checking
            if tmp_data[-2:] != '\x00\x00':
                raise MCRconException('protocol failure', 'non-null pad bytes')
            tmp_data = tmp_data[:-2]
            
            #if tmp_type != out_type:
            #    raise Exception('protocol failure', 'type mis-match', tmp_type, out_type)
           
            if tmp_req_id == -1:
                raise MCRconException('auth failure')
           
            m = re.match('^Error executing: %s \((.*)\)$' % re.escape(out_data), tmp_data)
            if m:
                raise MCRconException('command failure', m.group(1))
            
            #Append
            in_data += tmp_data

            #Check if more data ready...
            ready = select.select([self.s], [], [], 0)[0]
        
        return in_data
