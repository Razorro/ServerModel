import time
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from coroutine_server import Server


class Thread_Server(Server):
    def __init__(self, ip, port, maxConn=100):
        super().__init__(ip, port, maxConn)
        self.workThreadPool = ThreadPoolExecutor(max_workers=3)

    def messageProcess(self, sock, packet):
        self.workThreadPool.submit(partial(self._delayedProcess, sock, packet))

    def _delayedProcess(self, sock, packet, delay=3):
        time.sleep(delay)
        print('after %s seconds delay, processing...' % delay)
        print('receive data detail: %r, data len: %s' % (packet, len(packet)))
        print('Done!')

        # Put into write notification list, simply treat packet as the result
        result = packet
        self.wlist.add(sock)
        self.writeChannel[sock].send(result)


if __name__ == '__main__':
    s = Thread_Server('localhost', 10011)
    s.start()