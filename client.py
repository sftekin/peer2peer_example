import random
import time
from random import randint

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor


class Client(DatagramProtocol):
    def __init__(self, fact_names, fact_info, host="localhost", port=8000, capacity=1):
        # faculty info
        self.fact_names = fact_names
        self.fact_info = fact_info
        # client info
        self.client_ip = "127.0.0.1" if host == "localhost" else host
        self.client_port = port
        self.capacity = capacity  # the number of peers that this client can connect
        self.client_address = (self.client_ip, self.client_port)
        self.client_name = f"{self.client_ip}/{self.client_port}"
        # server info
        self.server_addr = ("127.0.0.1", 9999)
        # peers info
        self.peers_addr = {}  # stores key: Establish flag
        self.peer2names = {}
        print(f"Client {self.client_name} | is created.")

        self.cache = []

    def startProtocol(self):
        server_message = f"ready-{self.capacity}".encode("utf-8")
        self.transport.write(server_message, self.server_addr)

    def datagramReceived(self, datagram: bytes, addr):
        datagram = datagram.decode("utf-8")
        if self.server_addr == addr:
            # perform server job
            new_peer = self.parse_server_message(datagram)
            if new_peer:
                for p_addr in self.peers_addr:
                    self.send_ping(addr=p_addr)
                    reactor.callInThread(self.send_information, p_addr)
        else:
            header, message = datagram.split("/")
            if header == "ping":
                self.peers_addr[addr] = True
                print(f"Client {self.client_name} | PING received from {addr}")
                self.send_pong(addr=addr)
            elif header == "pong":
                self.peers_addr[addr] = True
                print(f"Client {self.client_name} | PONG received from {addr}")
            elif header == "get_names":
                package = ",".join(self.fact_names)
                send_message = f"send_names/{package}".encode("utf-8")
                print(f"Client {self.client_name} | get_names received from {addr}")
                self.transport.write(send_message, addr)
            elif header == "send_names":
                print(f"Client {self.client_name} | send_names received from {addr}")
                self.peer2names[addr] = message
            elif header == "keyword":
                fac_name = message.strip()
                if fac_name in self.cache:
                    return
                self.cache.append(fac_name)
                if fac_name in self.fact_names:
                    idx = self.fact_names.index(fac_name)
                    print(f"Client {self.client_name} | {fac_name} is found, here its more info: \n")
                    print(self.fact_info[idx])
                    self.transport.write("word_found".encode("utf-8"), self.server_addr)
                else:
                    self.search_peers(keyword=fac_name)

    def send_ping(self, addr):
        self.transport.write("ping/".encode("utf-8"), addr)

    def send_pong(self, addr):
        self.transport.write("pong/".encode("utf-8"), addr)

    def send_information(self, addr):
        counter = 0
        while not self.peers_addr[addr]:
            if counter > 10:
                break
            time.sleep(1)
            counter += 1

        if not self.peers_addr[addr]:
            print(f"Client {self.client_name} | ASK info from {addr} is timed out")
            return
        else:
            # ask for information from your peer
            self.transport.write("get_names/".encode("utf-8"), addr)

    def search_peers(self, keyword):
        found_addr = False
        for peer_addr, peer_names in self.peer2names.items():
            if keyword in peer_names:
                found_addr = True
                self.transport.write(f"keyword/{keyword}".encode("utf-8"), peer_addr)
        if not found_addr:
            neigh_list = list(self.peers_addr.keys())
            peer_addr = neigh_list[randint(0, len(neigh_list) - 1)]
            self.transport.write(f"keyword/{keyword}".encode("utf-8"), peer_addr)

    def parse_server_message(self, datagram):
        if datagram:
            # the server will tell you where you can connect
            for addr in datagram.split("?"):
                ip, port = addr.split("-")
                new_addr = (ip, int(port))
                self.peers_addr[new_addr] = False
                print(f"Client {self.client_name} | ADD {new_addr}")
            new_peer = True
        else:
            print(f"Client {self.client_name} | This is the first node")
            new_peer = False
        return new_peer


if __name__ == '__main__':
    r_port = randint(1000, 5000)
    client = Client("localhost", r_port)
    reactor.listenUDP(r_port, client)
    reactor.run()
