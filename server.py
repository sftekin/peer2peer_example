from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
import numpy as np


class Server(DatagramProtocol):
    def __init__(self):
        self.clients2cap = {}
        self.clients2addr = {}
        self.graph = {}
        self.n_nodes = 0

    def datagramReceived(self, datagram: bytes, addr):
        datagram = datagram.decode("utf-8")
        if "ready" in datagram:
            capacity = int(datagram.split("-")[1])
            addr_str = f"{addr[0]}-{addr[1]}"
            if addr_str not in self.clients2addr.keys():
                node_id = self.add_node(addr=addr_str, capacity=capacity)
                print(f"Server | ADD: client {addr} added with capacity {capacity}")
                # send the neighbouring info
                neigh_str = self.get_neigh_str(node_id=node_id)
                self.transport.write(neigh_str.encode("utf-8"), addr)
            else:
                raise Warning("Server | This node already exists")
        else:
            raise Warning("Server | only accept registration requests!")

    def add_node(self, addr, capacity):
        if self.n_nodes == 0:
            self.graph[0] = []
            self.n_nodes = 1
            self.clients2cap[0] = capacity
            self.clients2addr[0] = addr
            return 0
        else:
            # update graph
            node_id = self.n_nodes
            nodes = list(self.graph.keys())
            random_ngh = np.random.permutation(nodes)[:capacity]
            self.graph[node_id] = random_ngh.tolist()
            for ngh in random_ngh:
                self.graph[ngh].append(node_id)

            # update the info
            self.clients2cap[node_id] = capacity
            self.clients2addr[node_id] = addr
            self.n_nodes += 1
            print(self.graph)
            return node_id

    def get_neigh_str(self, node_id):
        if self.n_nodes < 2:
            return ""
        else:
            neigh_idx = self.graph[node_id]
            neigh_str = "?".join([self.clients2addr[j] for j in neigh_idx])
            return neigh_str


if __name__ == '__main__':
    reactor.listenUDP(9999, Server())
    reactor.run()
