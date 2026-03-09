import socket
import threading
from datetime import datetime
import os
import sys

# Fix emoji printing issue in Windows terminal
sys.stdout.reconfigure(encoding='utf-8')

# Server IP and port number
HOST = "127.0.0.1"
PORT = 5000

# Maximum number of clients allowed
MAX_CLIENTS = 10

# Dictionary to store connected clients
# format: {socket : username}
clients = {}

# Lock is used so multiple threads do not modify the dictionary at the same time
lock = threading.Lock()

# File names for storing chat history and server logs
HISTORY_FILE = "chat_history.txt"
LOG_FILE = "server.log"


# Function to store server events in log file
def log_event(message):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(message + "\n")


# Function to save chat messages in history file
def save_history(message):
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(message + "\n")


# Function to load previous chat messages when a new user joins
def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []

    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return f.readlines()


# Function to send a message to all connected clients
def broadcast(message):

    disconnected = []

    # Copy list of client sockets safely
    with lock:
        sockets = list(clients.keys())

    # Send message to each client
    for client in sockets:
        try:
            client.send((message + "\n").encode("utf-8"))
        except:
            # If sending fails, mark client as disconnected
            disconnected.append(client)

    # Remove disconnected clients
    for client in disconnected:
        remove_client(client)


# Function to remove a client when they disconnect
def remove_client(client_socket):

    with lock:
        if client_socket not in clients:
            return

        username = clients[client_socket]

        # Remove user from dictionary
        del clients[client_socket]

    msg = f"SERVER: {username} left the chat"

    print(msg)

    # Save event in log file
    log_event(msg)

    # Notify other users
    broadcast(msg)

    # Close socket connection
    try:
        client_socket.close()
    except:
        pass


# Function that handles communication with one client
def handle_client(client_socket, addr):

    try:

        # Ask client for username
        client_socket.send("USERNAME".encode())

        username = client_socket.recv(1024).decode().strip()

        with lock:

            # Check if server already has maximum clients
            if len(clients) >= MAX_CLIENTS:
                client_socket.send("Server full".encode())
                client_socket.close()
                return

            # Prevent duplicate usernames
            if username in clients.values():
                client_socket.send("Username already taken".encode())
                client_socket.close()
                return

            # Add user to client list
            clients[client_socket] = username

        join_msg = f"SERVER: {username} joined the chat"

        print(join_msg)

        # Save join event
        log_event(join_msg)

        # Inform other users
        broadcast(join_msg)

        # Send previous chat history to the new user
        history = load_history()

        for msg in history[-20:]:
            client_socket.send(msg.encode("utf-8"))

        # Continuous loop to receive messages
        while True:

            data = client_socket.recv(1024)

            if not data:
                break

            data = data.decode().strip()

            # Message command
            if data.startswith("MSG"):

                message = data[4:]

                # Add timestamp
                timestamp = datetime.now().strftime("%H:%M:%S")

                # Replace simple emoji text with actual emoji
                message = message.replace(":)", "😊").replace(":(", "😢").replace(":D", "😃")

                formatted = f"[{timestamp}] {username}: {message}"

                print(formatted)

                # Save message to history and log
                save_history(formatted)
                log_event(formatted)

                # Send message to all clients
                broadcast(formatted)

            # Command to show connected users
            elif data == "USERS":

                with lock:
                    user_list = ", ".join(clients.values())

                client_socket.send(f"Connected users: {user_list}".encode())

            # Quit command
            elif data == "QUIT":
                break

    except Exception as e:
        # Print error if client crashes
        print("Client error:", e)

    finally:
        # Remove client safely
        remove_client(client_socket)


# Function to start the server
def start_server():

    # Create TCP socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Allow quick restart of server
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind server to IP and port
    server.bind((HOST, PORT))

    # Listen for up to 10 clients
    server.listen(10)

    print(f"Server running on {HOST}:{PORT}")

    # Accept connections continuously
    while True:

        client_socket, addr = server.accept()

        # Create thread for each client
        thread = threading.Thread(
            target=handle_client,
            args=(client_socket, addr),
            daemon=True
        )

        thread.start()


# Start the server program
if __name__ == "__main__":
    start_server()