import os
import time
import numpy as np
from threading import Thread
from multiprocessing import Process
from twisted.internet import reactor
from client import Client
from server import Server
from document import Document
from twisted.internet.protocol import DatagramProtocol

os.environ["FOUND"] = "0"


def client_run(client, port):
    reactor.listenUDP(port, client)
    reactor.run()


def run():
    num_clients = 5
    num_queries = 5
    file_count = 20

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
    ports = np.random.choice(range(4000, 5000), num_clients, replace=False)
    capacities = [2, 3, 3, 2, 3]

    # create clients
    clients = []
    all_names = []
    for s_ind, port, cap in zip(shard_indices, ports, capacities):
        fact_names, fact_info = doc_creator.shard_document(start_idx=s_ind[0],
                                                           end_idx=s_ind[1])
        all_names += fact_names
        client = Client(fact_names=fact_names,
                        fact_info=fact_info,
                        port=port,
                        capacity=cap)
        clients.append((client, port))

    # create server
    server = Server()

    # activate server
    p = Process(target=client_run, args=(server, 9999))
    p.start()

    # activate clients
    processes = []
    for client, port in clients:
        p = Process(target=client_run, args=(client, port))
        p.start()
        processes.append(p)
        time.sleep(1)

    time.sleep(3)
    print("possible_names", all_names)
    print("calling query arg")
    eg_port = clients[0][1]
    sample_words = all_names[:num_queries]
    counter = 0
    q_time_list = []
    start_time = time.time()
    for word in sample_words:
        qs_time = time.time()
        server.search_fact(fact_name=word, port=eg_port)
        with open("flag.txt", "r") as f:
            flag = f.readline()
        while flag == "0":
            pass
        qe_time = time.time()
        counter += 1

        with open("flag.txt", "w") as f:
            f.write("0")

        q_time_list.append(qe_time - qs_time)
    elapsed_time = time.time() - start_time

    print(f"Throughput: {counter / elapsed_time:.5f}, Latency: {np.mean(q_time_list):.5f}")

    for p in processes:
        p.join()


if __name__ == '__main__':
    run()
