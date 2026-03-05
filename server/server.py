import socket
import threading
from datetime import datetime

HOST = "127.0.0.1"
PORT = 5000

clients = {}
lock = threading.Lock()


def broadcast(message, sender=None):
    """Send message to all clients except sender"""
    with lock:
        for client_socket in list(clients.keys()):
            if client_socket != sender:
                try:
                    client_socket.send(message.encode())
                except:
                    client_socket.close()
                    remove_client(client_socket)


def remove_client(client_socket):
    """Remove client from dictionary"""
    with lock:
        if client_socket in clients:
            username = clients[client_socket]
            del clients[client_socket]
            broadcast(f"SERVER: {username} left the chat.")


def handle_client(client_socket, addr):
    try:
        client_socket.send("Enter username: ".encode())
        username = client_socket.recv(1024).decode().strip()

        with lock:
            clients[client_socket] = username

        print(f"{username} connected from {addr}")
        broadcast(f"SERVER: {username} joined the chat.")

        while True:
            message = client_socket.recv(1024).decode()

            if not message:
                break

            if message.strip() == "/quit":
                break

            timestamp = datetime.now().strftime("%H:%M:%S")
            full_message = f"[{timestamp}] {username}: {message}"

            print(full_message)
            broadcast(full_message, client_socket)

    except:
        pass
    finally:
        remove_client(client_socket)
        client_socket.close()


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(10)

    print(f"Server started on {HOST}:{PORT}")
    print("Waiting for connections...\n")

    while True:
        client_socket, addr = server.accept()

        thread = threading.Thread(
            target=handle_client, args=(client_socket, addr))
        thread.start()


if __name__ == "__main__":
    start_server()