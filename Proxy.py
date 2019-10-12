import socket, os, parser
from threading import Thread

'''
TCP Network Proxy
'''

class ProxyToServer(Thread):

    def __init__(self, host, port):
        super(ProxyToServer, self).__init__()
        self.client = None
        self.port = port
        self.host = host
        self.server = socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((host, port))

    def run(self):
        while True:
            data = self.server.recv(4096)
            if data:
                try:
                    reload(parser)
                    parser.parse(data, self.port, "server")
                except Exception as e:
                    print("server[{}]".format(self.port), e)
                self.game.sendall(data)

class ClientToProxy(Thread):

    def __init__(self, host, port):
        super(ClientToProxy, self).__init__()
        self.server = None
        self.port = port
        self.host = host
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.listen(1)
        self.game, addr = sock.accept()

    def run(self):
        while True:
            data = self.client.recv(4096)
            if data:
                try:
                    reload(parser)
                    parser.parse(data, self.port, "client")
                except Exception as e:
                    print("client[{}]".format(self.port), e)
                self.server.sendall(data)

class Proxy(Thread):

    def __init__(self, from_host, to_host, port):
        super(Proxy, self).__init__()
        self.from_host = from_host
        self.to_host = to_host
        self.port = port

    def run(self):
        while True:
            print("[proxy({})] setting up".format(self.port))
            self.ctp = ClientToProxy(self.from_host, self.port)
            self.pts = ProxyToServer(self.to_hist, self.port)
            print("[proxy({})] connection established".format(self.port))
            self.ctp.server = self.pts.server
            self.pts.client = self.ctp.client

            self.ctp.start()
            self.pts.start()

if __name__ == "__main__":
    master_server = Proxy("0.0.0.0", "192.168.178.54", 3333)
    master_server.start()

    game_servers = []
    for port in range(3000, 3006):
        _game_server = Proxy("0.0.0.0", "192.168.178.54", port)
        _game_server.start()
        game_servers.append(_game_server)

    cmds = {"quit/exit": "Close the proxy", "help": "Display this list"}

    while True:
        try:
            cmd = input("$ ")
            if (cmd[:4] == "quit" or cmd[:4] == "exit"):
                os._exit(0)
            elif (cmd[:4] == "help"):
                print("--Commands--")
                for key, val in cmds.items():
                    print("[*] {} :: {}".format(key, val))
                print("--Commands--")
            else:
                print("Error: Invalid command, type \"help\" for a list of commands")
        except Exception as e:
            print(e)
