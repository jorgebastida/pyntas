#!/usr/bin/env python
import re
import sys
import socket
import array
import threading
import redis as redislib
import simplejson
from random import randrange

import settings


class ClientThread(threading.Thread):

    def __init__(self, channel, details):
        self.channel = channel
        self.details = details
        threading.Thread.__init__(self)

    def run(self):
        print 'Received connection:', self.details[0]
        self.channel.settimeout(10)
        self.channel.send('$Direction Download 75|')
        outfile = open(self.details[0] + '.tmp', 'wb')
        print 'file opened to write'
        buff = ""
        while True:
            try:
                while True:
                    t = self.channel.recv(1)
                    buff += t
            except socket.timeout:
                pass
            except socket.error:
                break
        print 'got from connect ' + t
        outfile.write(t)
        self.channel.close()
        print 'Closed connection:', self.details[0]


class ChatBot(object):
    HOST = 'dc.ekparty.org'
    PORT = 411

    sharesize = '15012000000'
    debugflag = 1
    commanddebug = 1
    loggedon = 0
    havenicklist = 0

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tmpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __init__(self, redis, nick):
        self.nick = nick
        self.redis = redis

    def readsock(self, sock):
        buff = ""
        sock.settimeout(0.13)
        while True:
            try:
                while True:
                    t = sock.recv(1)
                    if t != '|':
                        buff += t
                    else:
                        return buff
            except socket.timeout:
                pass
            except socket.error:
                return
        return buff

    def parsecommand(self, gotstring):

        if (gotstring != ''):
            print gotstring
            data = gotstring.split()

            if data[0] == '$Lock':
                self.s.send('$Key %s|' % self.lock2key2(data[1]))
                self.s.send('$ValidateNick %s|' % self.nick)
            elif data[0] == '$UserIP':
                if (self.debugflag):
                    print '\nGot $UserIP'
            elif data[0] == '$Hello':
                self.s.send('$Version 1,0091|')
                self.s.send('$MyINFO $ALL %s simple python bot$ $100$bot@bot.com$%s$|' % (self.nick, self.sharesize))
            elif data[0] == '$HubTopic':
                    return 'Logged'
            if data[0]:
                return data[0]
        return

    def lock2key2(self, lock):
        "Generates response to $Lock challenge from Direct Connect Servers"
        lock = array.array('B', lock)
        ll = len(lock)
        key = list('0' * ll)
        for n in xrange(1, ll):
            key[n] = lock[n] ^ lock[n - 1]
        key[0] = lock[0] ^ lock[-1] ^ lock[-2] ^ 5
        for n in xrange(ll):
            key[n] = ((key[n] << 4) | (key[n] >> 4)) & 255
        result = ""
        for c in key:
            if c in (0, 5, 36, 96, 124, 126):
                result += "/%%DCN%.3i%%/" % c
            else:
                result += chr(c)
        return result

    def logintohub(self):
        print 'connecting....'
        self.s.connect((self.HOST, self.PORT))
        self.s.send('Hello, world|')

        while 1:
            data = self.readsock(self.s)
            t = self.parsecommand(data)
            if t == 'Logged':
                break
        return

    def mainloop(self):
        while 1:
            data = self.readsock(self.s)

            if (data != ''):
                command, message = data.split(' ', 1)
                if command.startswith('<') and command.endswith('>'):
                    print command, message
                    m = re.match(r'.*(\w{2}([\s-])?\d{1,3}).*', message.upper())
                    if m:

                        site = m.groups()[0].replace(' ', '-')
                        if '-' not in site:
                            site = '-'.join([site[:2], site[2:]])

                        user = command[1:-1]
                        if 'compro' in message.lower():
                            color = '#B94A48'
                        elif 'vendo' in message.lower():
                            color = '#468847'
                        elif 'necesito' in message.lower() or 'busco' in message.lower():
                            color = '#F89406'
                        else:
                            color = "#%s" % "".join([hex(randrange(0, 255))[2:] for i in range(3)])

                        try:
                            data = {'user': user, 'message': message.encode('utf-8'), 'site': site, 'color':color}
                            data = simplejson.dumps(data)
                        except:
                            continue

                        self.redis.publish(settings.CHAT_KEY, data)

                elif command == '$Hello' and command == self.nick:
                        self.loggedon = 1

        return

if __name__ == '__main__':
    redis = redislib.StrictRedis(host=settings.REDIS_HOST,
                                 port=settings.REDIS_PORT,
                                 db=settings.REDIS_DB)

    if len(sys.argv) < 2:
        print "You must provide a bot name:  python dcbot USERNAME"
        sys.exit(1)

    t = ChatBot(nick=sys.argv[1], redis=redis)
    t.logintohub()
    t.mainloop()
