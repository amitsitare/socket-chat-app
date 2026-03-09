import socket
import threading
from datetime import datetime
import os
import sys

# Fix emoji printing in Windows
sys.stdout.reconfigure(encoding='utf-8')

HOST = "127.0.0.1"
PORT = 5000
MAX_CLIENTS = 10

clients = {}
lock = threading.Lock()

HISTORY_FILE = "chat_history.txt"
LOG_FILE = "server.log"

def log_event(message):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(message + "\n")

def save_history(message):
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(message + "\n")

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return f.readlines()

def broadcast(message):
    disconnected = []
    with lock:
        sockets = list(clients.keys())
    for client in sockets:
        try:
            client.send((message + "\n").encode("utf-8"))
        except:
            disconnected.append(client)
    for client in disconnected:
        remove_client(client)

def remove_client(client_socket):
    with lock:
        if client_socket not in clients:
            return
        username = clients[client_socket]
        del clients[client_socket]

    msg = f"SERVER: {username} left the chat"
    print(msg)
    log_event(msg)
    broadcast(msg)
    try:
        client_socket.close()
    except:
        pass

def handle_client(client_socket, addr):
    try:
        client_socket.send("USERNAME".encode())
        username = client_socket.recv(1024).decode().strip()
        with lock:
            if len(clients) >= MAX_CLIENTS:
                client_socket.send("Server full".encode())
                client_socket.close()
                return

            if username in clients.values():
                client_socket.send("Username already taken".encode())
                client_socket.close()
                return
            clients[client_socket] = username

        join_msg = f"SERVER: {username} joined the chat"
        print(join_msg)
        log_event(join_msg)
        broadcast(join_msg)
        history = load_history()
        for msg in history[-20:]:
            client_socket.send(msg.encode("utf-8"))

        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            data = data.decode().strip()

            if data.startswith("MSG"):
                message = data[4:]
                timestamp = datetime.now().strftime("%H:%M:%S")
                message = message.replace(":)", "😊").replace(":(", "😢").replace(":D", "😃")
                formatted = f"[{timestamp}] {username}: {message}"
                print(formatted)
                save_history(formatted)
                log_event(formatted)
                broadcast(formatted)

            elif data == "USERS":
                with lock:
                    user_list = ", ".join(clients.values())
                client_socket.send(f"Connected users: {user_list}".encode())

            elif data == "QUIT":
                break
    except Exception as e:
        print("Client error:", e)
    finally:
        remove_client(client_socket)

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(10)

    print(f"Server running on {HOST}:{PORT}")
    while True:
        client_socket, addr = server.accept()
        thread = threading.Thread(
            target=handle_client,
            args=(client_socket, addr),
            daemon=True
        )
        thread.start()

if __name__ == "__main__":
    start_server()