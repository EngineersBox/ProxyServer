import socket, os, parser
from threading import Thread
from uuid import uuid4
from pwn import *

'''
TCP Network Proxy
'''

class logging:

    def status(msg):
        print("[" + text.magenta("x") + "] " + msg)

    def error(msg):
        print("[" + text.on_red("Error") + "] " + str(msg))

    def listelem(marker, msg):
        print("(" + text.bold_blue(marker) + ") " + str(msg))

    def listinfo(marker, msg):
        print("(" + text.bold_green(marker) + ") " + str(msg))

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
            logging.status("[Proxy({})] Initialising...".format(self.port))
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

    cmds = {"quit/exit": "Close the proxy",
            "help": "Display this list",
            "setserver": "Open a new connection to a server: \"setserver <interface> <ip> <port>\"",
            "setclient": "Open a new connection to a client: \"setclient <interface> <ip> <port>\"",
            "client": "Apply flags to client: \n-ca: close all\n-ci <id>: close with id\n-ids: Display active client id's",
            "server": "Apply flags to server: \n-c: close server"
    }

    while True:
        try:
            cmd = input("$ ")
            cmd = cmd.split(" ")
            if (cmd[0] == "quit" or cmd[0] == "exit"):
                os._exit(0)
            elif (cmd[0] == "help"):
                print("--Commands--")
                for key, val in cmds.items():
                    log.info("[*] {} :: {}".format(key, val))
                print("--Commands--")
            elif (cmd[0] == "setserver"):
                if (len(cmd) != 4):
                    log.warn("Error: Command format is \"setserver <interface> <ip> <port>\"")
                else:
                    if (not master_server):
                        master_server = Proxy(cmd[1], cmd[2], int(cmd[3]))
                        master_server.start()
                        log.info("[> Started server connection: [ip {}] [port{}]".format(cmd[2], cmd[3]))
                    else:
                        log.warn("Error: Server connection already established, close with \"server -c\"")
            elif (cmd[0] == "setclient"):
                if (len(cmd) != 4):
                    print("Error: Command format is \"setclient <interface> <ip> <port>\"")
                else:
                    client = Proxy(cmd[1], cmd[2], cmd[3])
                    client.start()
                    client_servers.append(client)
                    log.info("[> Started client connection: [ip {}] [port{}]".format(cmd[2], cmd[3]))
            elif (cmd[0] == "client"):
                if (len(cmd) < 2):
                    log.warn("Error: Command format is \"client <flags>\"")
                else:
                    if ("-ca" in cmd):
                        for client in client_servers:
                            client.close()
                            client_servers.remove(clients)
                        log.info("[> Closed all open clients")
                    if ("-ci" in cmd):
                        index = cmd.index("-ci")
                        if (index >= len(cmd) - 1):
                            log.warn("Error: \"-ci\" flag must have an id after it")
                        else:
                            len_pre = len(client_servers)
                            for client in client_servers:
                                if (str(client.getClientUid()) == cmd[index + 1]):
                                    client.close()
                                    client_servers.remove(client)
                            if (len_pre == len(client_servers)):
                                log.warn("Error: No open client with id: {}".format(cmd[index+1]))
                            log.info("[> Closed client with id: {}".format(cmd[index + 1]))
                    if ("-i" in cmd):
                        index = cmd.index("-i")
                        if (index >= len(cmd) - 1):
                            log.warn("Error: \"-ci\" flag must have an id after it")
                        else:
                            for client in client_servers:
                                if (str(client.getClientUid()) == cmd[index + 1]):
                                    log.info("[> Client " + text.bold_yellow(str(client.getClientUid())) + "\nInterface: {}\nServer: {}\nPort: {}".format(client.getInterface(), client.getServer(), client.getPort()))
                    if ("-ids" in cmd):
                        if (len(client_servers) < 1):
                            log.warn("Error: No active clients")
                        else:
                            log.info("[> Active Clients")
                            for i in range(0, len(client_servers)):
                                logging.listelem(str(i), client_servers[i].getClientUid())
            elif (cmd[0] == "server"):
                if (len(cmd) < 2):
                    log.warn("Error: Command format is \"server <flags>\"")
                else:
                    if ("-c" in cmd):
                        master_server.close()
                        log.info("[> Closed active server connection")
            else:
                log.warn("Error: Invalid command, type \"help\" for a list of commands")
        except Exception as e:
            logging.error(e)
