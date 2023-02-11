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
                print(f"Server | ADD: client {addr} added with capacity {capacity}")
                # send the neighbouring info
                neigh_str = self.get_neigh_str()
                self.transport.write(neigh_str.encode("utf-8"), addr)
            else:
                raise Warning("Server | This node already exists")
        else:
            raise Warning("Server | only accept registration requests!")

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
            temp_mat[random_ngh] = 1  # set the neighbours
            self.adjacency_mat = temp_mat

            # update the info
            self.clients2cap[self.n_nodes] = capacity
            self.clients2addr[self.n_nodes] = addr
            self.n_nodes += 1

    def get_neigh_str(self):
        n_row = np.where(self.adjacency_mat[-1])[0]
        neigh_idx = n_row[:-1]
        neigh_str = "?".join(["-".join(self.clients2addr[j]) for j in neigh_idx])
        return neigh_str


if __name__ == '__main__':
    reactor.listenUDP(9999, Server())
    reactor.run()
