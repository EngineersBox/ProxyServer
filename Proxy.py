import socket, os, parser, cmdline
from threading import Thread
from uuid import uuid4
from pwn import *

'''
TCP Network Proxy
'''

class ProxyToServer(Thread):

    def __init__(self, host, port, uid):
        super(ProxyToServer, self).__init__()
        self.client = None
        self.port = port
        self.host = host
        self.uid = uid
        self.server = socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((host, port))

    def run(self):
        while True:
            data = self.server.recv(4096)
            if data:
                try:
                    reload(parser)
                    parser.parse(data, self.port, "Server")
                except Exception as e:
                    log.warn("Server[{}]".format(self.port), e)
                self.game.sendall(data)

class ClientToProxy(Thread):

    def __init__(self, host, port, uid):
        super(ClientToProxy, self).__init__()
        self.server = None
        self.port = port
        self.host = host
        self.uid = uid
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, int(port)))
        sock.listen(1)
        self.game, addr = sock.accept()

    def run(self):
        while True:
            data = self.client.recv(4096)
            if data:
                try:
                    reload(parser)
                    parser.parse(data, self.port, "Client")
                except Exception as e:
                    log.warn("Client[{}]".format(self.port), e)
                self.server.sendall(data)

class Proxy(Thread):

    def __init__(self, from_host, to_host, port):
        super(Proxy, self).__init__()
        self.from_host = from_host
        self.to_host = to_host
        self.port = port
        self.ctpuid = uuid4()
        self.ptsuid = uuid4()

    def run(self):
        while True:
            cmdline.logging.status("[Proxy({})] Initialising...".format(self.port))
            self.ctp = ClientToProxy(self.from_host, self.port, self.ctpuid)
            self.pts = ProxyToServer(self.to_hist, self.port, self.ptsuid)
            log.success("[Proxy({})] Connection established".format(self.port))
            self.ctp.server = self.pts.server
            self.pts.client = self.ctp.client

            self.ctp.start()
            self.pts.start()

    ## TODO: Fix close() method to actually stop threads and not just return a weird number
    def close(self):
        super()._stop()
        super()._delete()

    def getClientUid(self):
        return self.ctpuid

    def getServerUid(self):
        return self.ptsuid

    def getInterface(self):
        return self.from_host

    def getServer(self):
        return self.to_host

    def getPort(self):
        return self.port

if __name__ == "__main__":
    master_server = Proxy("0.0.0.0", "192.168.178.54", 3333)
    master_server.start()

    client_servers = []
    for port in range(3000, 3006):
        client_server = Proxy("0.0.0.0", "192.168.178.54", port)
        client_server.start()
        client_servers.append(client_server)

    cmdline.cli(master_server, client_servers)
