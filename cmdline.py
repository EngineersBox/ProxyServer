from pwn import *
import Proxy

class logging:

    def status(msg: str) -> None:
        print("[" + text.magenta("x") + "] " + msg)

    def error(msg: str) -> None:
        print("[" + text.on_red("Error") + "] " + str(msg))

    def listelem(marker: str, msg: str) -> None:
        print("(" + text.bold_blue(marker) + ") " + str(msg))

    def listinfo(marker: str, msg: str) -> None:
        print("(" + text.bold_green(marker) + ") " + str(msg))

cmds = {"quit/exit": "Close the proxy",
        "help": "Display this list",
        "setserver": "Open a new connection to a server: \"setserver <interface> <ip> <port>\"",
        "setclient": "Open a new connection to a client: \"setclient <interface> <ip> <port>\"",
        "client": "Apply flags to client: \n-ca: close all\n-ci <id>: close with id\n-ids: Display active client id's\n-if <id> <interface>: set interface for specified client",
        "server": "Apply flags to server: \n-c: close server\n-p <port>: set port for server\n-if <interface>: set interface for server"
}

def cli(master_server, client_servers):
    while True:
        try:
            cmd = input("$ ").decode("utf-8")
            cmd = list(map(lambda s: s.replace("\n", ""), cmd.split(" ")))
            if (cmd[0] == "quit" or cmd[0] == "exit"):
                os._exit(0)
            elif (cmd[0] == "help"):
                print("--Commands--")
                for key, val in cmds.items():
                    log.info("{} :: {}".format(key, val))
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
                            log.warn("Error: \"-ci\" flag must have an id specified")
                        else:
                            len_pre = len(client_servers)
                            for client in client_servers:
                                if (str(client.getClientUid()) == cmd[index + 1]):
                                    client.close()
                                    client_servers.remove(client)
                                    break
                            if (len_pre == len(client_servers)):
                                log.warn("Error: No open client with id: {}".format(cmd[index+1]))
                            log.info("[> Closed client with id: {}".format(cmd[index + 1]))
                    if ("-i" in cmd):
                        index = cmd.index("-i")
                        if (index >= len(cmd) - 1):
                            log.warn("Error: \"-i\" flag must have an id specified")
                        else:
                            for client in client_servers:
                                if (str(client.getClientUid()) == cmd[index + 1]):
                                    log.info("[> Client " + text.bold_yellow(str(client.getClientUid())) + "\nInterface: {}\nServer IP: {}\nPort: {}".format(client.getInterface(), client.getServer(), client.getPort()))
                                    break
                    if ("-ids" in cmd):
                        if (len(client_servers) < 1):
                            log.warn("Error: No active clients")
                        else:
                            log.info("[> Active Clients")
                            for i in range(0, len(client_servers)):
                                logging.listelem(str(i), client_servers[i].getClientUid())
                    if ("-if" in cmd):
                        index = cmd.index("-if")
                        if (len(cmd) - 1 == index):
                            log.warn("Error: flag must have an interface specified")
                        else:
                            changed = False
                            for client in client_servers:
                                if (str(client.getClientUid()) == cmd[index + 1]):
                                    client.from_host = cmd[index + 2]
                                    log.info("[> Set client interface to: '{}'".format(cmd[index + 2]))
                                    changed = True
                                    break
                            if (not changed):
                                log.warn("Error: No client with id: " + cmd[index + 1])
            elif (cmd[0] == "server"):
                if (len(cmd) < 2):
                    log.warn("Error: Command format is \"server <flags>\"")
                else:
                    if ("-c" in cmd):
                        master_server.close()
                        log.info("[> Closed active server connection")
                    if ("-p" in cmd):
                        index = cmd.index("-p")
                        if (len(cmd) - 1 == index):
                            log.warn("Error: flag must have a port specified")
                        else:
                            master_server.port = int(cmd[index + 1])
                            log.info("[> Set server port to: '{}'".format(cmd[index + 1]))
                    if ("-i" in cmd):
                        log.info("[> Server " + text.bold_yellow(str(master_server.getServerUid())) + "\nInterface: {}\nIP: {}\nPort: {}".format(master_server.getInterface(), master_server.getServer(), master_server.getPort()))
                    if ("-if" in cmd):
                        index = cmd.index("-if")
                        if (len(cmd) - 1 == index):
                            log.warn("Error: flag must have an interface specified")
                        else:
                            master_server.from_host = cmd[index + 1]
                            log.info("[> Set server interface to: '{}'".format(cmd[index + 1]))

            else:
                log.warn("Error: Invalid command, type \"help\" for a list of commands")
        except Exception as e:
            print(e.message)
            logging.error(e)
