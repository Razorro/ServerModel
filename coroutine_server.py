import socket
import select
import copy
from functools import wraps
from collections import deque
from struct import pack


def coroutine(func):
    """ Decorator: primes `func` by advancing to first `yield` """
    @wraps(func)
    def primer(*args, **kwargs):
        gen = func(*args, **kwargs)
        next(gen)
        return gen
    return primer


class Server:
    def __init__(self, ip, port, maxConn=100):
        self.ip = ip
        self.port = port
        self.sock = None
        self.readChannel = {}                           # read channel
        self.writeChannel = {}                          # write channel
        self.pendingPacket = {}                         # pending to deal
        self.wlist = set()                              # wait to write
        self.maxConn = maxConn

    @staticmethod
    def packetTrimmer(byteBuf):
        """ Default method to trim a packet out of buffer """
        while True:
            datas = yield
            byteBuf += datas
            if len(byteBuf) >= 2:
                break

        packetSize = byteBuf[1] * 256 + byteBuf[0]
        while True:
            if len(byteBuf) >= packetSize+2:
                break
            datas = yield
            byteBuf += datas

        packetData = byteBuf[2:packetSize+2]
        return packetData, byteBuf[2+packetSize:]

    def distributePacket(self):
        """ package processing, customize it as whatever you want """
        for sock, msgQueue in self.pendingPacket.items():
            if len(msgQueue) == 0:
                continue

            packet = msgQueue.popleft()
            self.messageProcess(sock, packet)

    def messageProcess(self, sock, packet):
        """ Do nothing, just echo to client """
        self.wlist.add(sock)                        # turn on watching on write socket
        self.writeChannel[sock].send(packet)

    def start(self):
        print('start server at %s:%s' % (self.ip, self.port))
        try:
            self.sock = socket.socket()
            self.sock.bind((self.ip, self.port))
            self.sock.listen(self.maxConn)
        except Exception as e:
            print('initialize server error: %s' % e)
            return
        else:
            while True:
                rlist = [self.sock] + list(self.readChannel.keys())
                wlist = copy.copy(list(self.wlist))
                self.distributePacket()
                readSet, writeSet, exceptSet = select.select(rlist, wlist, [])

                for readFd in readSet:
                    if readFd == self.sock:
                        self.createConnection()
                    else:
                        self.readHandler(readFd)

                for writeFd in writeSet:
                    self.writeHandler(writeFd)

                for exceptFd in exceptSet:
                    print('got an exception notification about fd %s' % exceptFd)

    def createConnection(self):
        conn, addr = self.sock.accept()
        conn.setblocking(False)
        print("establish connection from %s" % (conn.getpeername(),))
        self.genereateChannel(conn)

    def readHandler(self, sock):
        """
        For best match with hardware and network realities, the value of bufsize should be
        a relatively small power of 2, for example, 4096.
        """
        nbytes = sock.recv(4096)
        if len(nbytes) == 0:
            self.closeConnection(sock)
        else:
            print('get data from sock%s --> %s' % (sock.getpeername(), nbytes.decode()))
            self.readChannel[sock].send(nbytes)

    def writeHandler(self, sock):
        self.writeChannel[sock].send(b'')

    def closeConnection(self, sock):
        print('conn from %s closed' % (sock.getsockname(),))
        del self.writeChannel[sock]
        del self.readChannel[sock]
        if sock in self.pendingPacket: del self.pendingPacket[sock]
        sock.close()

    def genereateChannel(self, sock):
        """ Create channel for socket """
        self.readChannel[sock] = self.getReadChannel(sock)
        self.writeChannel[sock] = self.getWriteChannel(sock)

    @coroutine
    def getReadChannel(self, sock):
        readBuf = bytearray()
        while True:
            datas = yield from self.packetTrimmer(readBuf)
            packet = datas[0]
            readBuf = datas[1]
            print('trim message from sock%s --> %s' % (sock.getpeername(), packet.decode()))
            self.pendingPacket.setdefault(sock, deque()).append(packet)

    @coroutine
    def getWriteChannel(self, sock):
        writeBuf = bytearray()
        while True:
            data = yield
            if len(data):
                writeBuf = writeBuf + pack('=H', len(data)) + data
            nwritten = sock.send(writeBuf)
            writeBuf = writeBuf[nwritten:]

            if len(writeBuf) == 0:
                print('cancel write listening')
                self.wlist.remove(sock)                 # turn off watching on write socket


if __name__ == "__main__":
    s = Server('localhost', 10010)
    s.start()