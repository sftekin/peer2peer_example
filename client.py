from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

from random import randint


class Client(DatagramProtocol):
    def __init__(self, host="localhost", port="8000", capacity=1):
        self.client_add = "127.0.0.1" if host == "localhost" else host
        self.client_port = port
        self.capacity = capacity  # the number of peers that this client can connect

        # server info
        self.server_add = "127.0.0.1"
        self.server_port = 9999

        # peers info
        self.peers_info = {}

        print(f"Client {self.client_add}/{self.client_port} is created.")

    def startProtocol(self):
        server_message = f"ready-{self.capacity}".encode("utf-8")
        self.transport.write(server_message, self.server)

    def datagramReceived(self, datagram: bytes, addr):
        datagram = datagram.decode("utf-8")
        if addr == self.server:
            print("Choose a client from these\n", datagram)
            self.address = input("Write host: "), int(input("Write port: "))
            reactor.callInThread(self.send_message)
        else:
            # perform
            print(addr, ":", datagram)

    def send_message(self):
        while True:
            self.transport.write(input(":::").encode("utf-8"), self.address)

    def parse_server_message(self, datagram):
        # the server will tell you where you can connect
        pass

if __name__ == '__main__':
    r_port = randint(1000, 5000)
    reactor.listenUDP(r_port, Client("localhost", r_port))
    reactor.run()
