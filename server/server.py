# import socket library to create network connections
import socket

# import threading so server can handle multiple clients
import threading

# import datetime to add message timestamps
from datetime import datetime

# server IP address
HOST = "127.0.0.1"

# port number where server will listen
PORT = 5000

# dictionary to store connected clients
# format: {socket : username}
clients = {}

# lock to prevent multiple threads modifying clients dictionary simultaneously
lock = threading.Lock()

# list to store chat history
chat_history = []

def broadcast(message, sender=None):

    # Send message to all connected clients except the sender
    with lock:
        for client_socket in list(clients.keys()):
            if client_socket != sender:
                try:
                    # send message to client
                    client_socket.send(message.encode())

                except:
                    # if sending fails remove client
                    client_socket.close()
                    remove_client(client_socket)

def remove_client(client_socket):
    # Remove disconnected client
    with lock:
        if client_socket in clients:
            username = clients[client_socket]

            # remove user from dictionary
            del clients[client_socket]

            # notify others
            broadcast(f"SERVER: {username} left the chat.")


def handle_client(client_socket, addr):
    
    # Handle communication with one client
    try:

        # ask username
        client_socket.send("Enter username: ".encode())

        # receive username
        username = client_socket.recv(1024).decode().strip()

        # add client to dictionary
        with lock:
            clients[client_socket] = username

        print(f"{username} connected from {addr}")

        # notify others
        broadcast(f"SERVER: {username} joined the chat.")

        # send chat history
        for msg in chat_history:
            client_socket.send((msg + "\n").encode())

        while True:

            # receive message
            message = client_socket.recv(1024).decode().strip()

            # if connection lost
            if not message:
                break

            # exit command
            if message == "/quit":
                break

            # show user list
            if message == "/users":

                user_list = ", ".join(clients.values())

                client_socket.send(
                    f"Connected users: {user_list}".encode()
                )

                continue

            # ignore empty messages
            if message == "":
                continue

            # timestamp
            timestamp = datetime.now().strftime("%H:%M:%S")

            # format message
            full_message = f"[{timestamp}] {username}: {message}"

            # save to history
            chat_history.append(full_message)

            print(full_message)

            # broadcast message
            broadcast(full_message, client_socket)

    except Exception as e:
        print("Error:", e)

    finally:

        remove_client(client_socket)

        client_socket.close()


def start_server():

    # create TCP socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # allow reuse of address
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # bind server to host and port
    server.bind((HOST, PORT))

    # allow 10 clients
    server.listen(10)

    print(f"Server started on {HOST}:{PORT}")
    print("Waiting for connections...\n")

    while True:

        # accept client connection
        client_socket, addr = server.accept()

        # create thread for client
        thread = threading.Thread(
            target=handle_client,
            args=(client_socket, addr)
        )

        # start thread
        thread.start()

# run server
if __name__ == "__main__":
    start_server()