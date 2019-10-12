from codecs import encode

def parse(data, port, origin):
    if (port == 3333):
        return
    if (origin == "server"):
        return
    print("[{}({}}] {}".format(origin, port, encode(data, "hex").decode("utf-8")))
