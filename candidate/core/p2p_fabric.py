"""
Peer-to-Peer (P2P) Fabric for True Decentralization
Addresses TODOs 57-67

This module provides a simplified implementation of a P2P node, which enables
direct, high-throughput communication between collaborating agents, bypassing
the central event broker for data-intensive tasks.
"""

import socket
import threading


class P2PNode:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.peers = set()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)
        self.lock = threading.Lock()

        listener_thread = threading.Thread(target=self._listen)
        listener_thread.daemon = True
        listener_thread.start()

    def _listen(self):
        while True:
            conn, addr = self.sock.accept()
            with self.lock:
                self.peers.add(addr)
            print(f"P2PNode: Accepted connection from {addr}")
            handler_thread = threading.Thread(
                target=self._handle_connection, args=(conn, addr)
            )
            handler_thread.daemon = True
            handler_thread.start()

    def _handle_connection(self, conn, addr):
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    break
                print(f"P2PNode: Received data from {addr}: {data.decode()}")
            except ConnectionResetError:
                break
        with self.lock:
            self.peers.remove(addr)
        conn.close()
        print(f"P2PNode: Connection from {addr} closed.")

    def connect(self, peer_host, peer_port):
        peer_addr = (peer_host, peer_port)
        with self.lock:
            if peer_addr in self.peers:
                return
            self.peers.add(peer_addr)

        try:
            peer_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_sock.connect(peer_addr)
            print(f"P2PNode: Connected to {peer_addr}")
            # In a real implementation, you would keep this socket open for
            # communication
        except ConnectionRefusedError:
            with self.lock:
                self.peers.remove(peer_addr)
            print(f"P2PNode: Connection to {peer_addr} refused.")

    def broadcast(self, message):
        with self.lock:
            for peer_addr in self.peers:
                try:
                    peer_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    peer_sock.connect(peer_addr)
                    peer_sock.sendall(message.encode())
                    peer_sock.close()
                except Exception as e:
                    print(f"P2PNode: Failed to send message to {peer_addr}: {e}")


if __name__ == "__main__":
    node1 = P2PNode("localhost", 8001)
    node2 = P2PNode("localhost", 8002)

    node1.connect("localhost", 8002)

    import time

    time.sleep(1)  # Allow time for connection to be established

    node1.broadcast("Hello from node 1!")
    node2.broadcast("Hello from node 2!")

    time.sleep(1)
