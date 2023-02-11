import os
import time
import numpy as np
from threading import Thread
from multiprocessing import Process
from twisted.internet import reactor

from client import Client
from server import Server
from document import Document


def client_run(client, port):
    reactor.listenUDP(port, client)
    reactor.run()

def run():
    num_clients = 5
    num_queries = 10
    file_count = 5

    file_path = os.path.join("files", "crawled_data.json")
    doc_creator = Document(file_path=file_path)

    # create client info
    shard_indices = []
    while len(shard_indices) != num_clients:
        start_idx = np.random.randint(0, doc_creator.n_files)
        end_idx = start_idx + file_count
        if end_idx >= doc_creator.n_files:
            continue
        else:
            shard_indices.append((start_idx, end_idx))
    ports = np.random.randint(1000, 5000, num_clients)
    capacities = np.random.randint(2, num_clients, num_clients)

    # create clients
    clients = []
    for s_ind, port, cap in zip(shard_indices, ports, capacities):
        fact_names, fact_info = doc_creator.shard_document(start_idx=s_ind[0],
                                                           end_idx=s_ind[1])
        client = Client(fact_names=fact_names,
                        fact_info=fact_info,
                        port=port,
                        capacity=cap)
        clients.append((client, port))

    # activate clients
    processes = []
    for client, port in clients:
        p = Process(target=client_run, args=(client, port))
        p.start()
        processes.append(p)
        time.sleep(1)

    for p in processes:
        p.join()



if __name__ == '__main__':
    run()
