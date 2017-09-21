#!/usr/bin/env python

import socket
import sys
import numbers
import json

LEN_SIZE = 10
TYPE_SIZE = 1
STMT_MSG = 0
EXPR_MSG = 1

class ConnectionBuffer(object):
    def __init__(self, conn):
        self.conn = conn
        self.buff = bytes()

    def get(self, size):
        while len(self.buff) < size:
            data = self.conn.recv(1024)
            if len(data) == 0:
                raise EOFError('Connection closed')
            self.buff += data

        result = self.buff[:size]
        self.buff = self.buff[size:]
        return result

def utf8(bs):
    if sys.version_info >= (3,0):
        return str(bs, 'UTF8')
    else:
        return unicode(bs, 'UTF8')

def to_logo(x):
    if isinstance(x, numbers.Number):
        return str(x)
    elif isinstance(x, str):
        return json.dumps(x)
    elif hasattr(x, '__len__'):
        return '[' + ' '.join([to_logo(y) for y in x]) + ']'
    else:
        return json.dumps(repr(x))

def to_bytes(s):
    if sys.version_info >= (3,0):
        return bytes(s, 'UTF8')
    else:
        return bytes(s)

def logo_responder(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('localhost', port))
        sock.listen(0)
        conn, addr = sock.accept()
        buff = bytes()
        with conn:
            buff = ConnectionBuffer(conn)
            globs = {}
            locs = {}
            while True:
                length = int(buff.get(LEN_SIZE))
                msg_type = int(buff.get(TYPE_SIZE))
                code = utf8(buff.get(length))
                if msg_type == STMT_MSG:
                    exec(code, globs, locs)
                else:
                    result = to_bytes(to_logo(eval(code, globs, locs)))
                    prefix = to_bytes(str(len(result)).zfill(LEN_SIZE))
                    conn.sendall(prefix + result)


def conn_iter(conn):
    buff = bytes()


if __name__ == '__main__':
    logo_responder(int(sys.argv[1]))

