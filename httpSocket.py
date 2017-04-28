
class HttpServerSocket:

    def __init__(self, client_sock, address):
        self.addr = address
        self.socket = client_sock


class HttpClientSocket:
    pass