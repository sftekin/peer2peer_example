from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
import numpy as np


class Server(DatagramProtocol):
    def __init__(self):
        self.clients2cap = {}
        self.clients2addr = {}
        self.adjacency_mat = None
        self.n_nodes = 0

    def datagramReceived(self, datagram: bytes, addr):
        datagram = datagram.decode("utf-8")
        if "ready" not in datagram:
            capacity = datagram.split("-")[1]
            if addr not in self.clients2addr.keys():
                self.add_node(addr=addr, capacity=capacity)
                print(f"ADD: Client {addr} added with capacity {capacity}")
            else:
                raise Warning("This node already exists")

            # send the neighbouring info

            adds = "\n".join([str(x) for x in self.clients])
            self.transport.write(adds.encode("utf-8"), addr)
            self.clients.append(addr)
        else:
            raise Warning("Server only accept registration requests!")

    def add_node(self, addr, capacity):
        if self.adjacency_mat is None:
            self.adjacency_mat = np.array([[1]])
            self.n_nodes = 1
            self.clients2cap[0] = capacity
            self.clients2addr[0] = addr
        else:
            # update adjacent mat
            temp_mat = np.zeros((self.n_nodes + 1, self.n_nodes + 1))
            temp_mat[:self.n_nodes, :self.n_nodes] = self.adjacency_mat.copy()
            temp_mat[-1, -1] = 1  # set the self adjacent
            random_ngh = np.random.permutation(range(self.n_nodes))[:capacity]
            temp_mat[random_ngh] = 1  # set the neighbours randomly
            self.adjacency_mat = temp_mat

            # update the info
            self.clients2cap[self.n_nodes] = capacity
            self.clients2addr[self.n_nodes] = addr
            self.n_nodes += 1


if __name__ == '__main__':
    reactor.listenUDP(9999, Server())
    reactor.run()
