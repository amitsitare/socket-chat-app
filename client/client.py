# import socket for network communication
import socket

# import threading to receive messages while typing
import threading

# import sys to exit program
import sys

# server address
HOST = "127.0.0.1"

# server port
PORT = 5000

def receive_messages(sock):
    
    # Continuously receive messages from server
    while True:
        try:
            message = sock.recv(1024).decode()
            if not message:
                break
            print(message)
        except:
            break

def send_messages(sock):

    # Send messages typed by user
    while True:
        message = input()

        # exit chat
        if message == "/quit":
            sock.send("/quit".encode())
            sock.close()
            sys.exit()

        # send message to server
        sock.send(message.encode())

def start_client():

    # create TCP socket
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect to server
    client.connect((HOST, PORT))

    # receive username prompt
    username_prompt = client.recv(1024).decode()

    # ask user
    username = input(username_prompt)

    # send username
    client.send(username.encode())

    # thread to receive messages
    receive_thread = threading.Thread(
        target=receive_messages,
        args=(client,)
    )
    receive_thread.start()

    # thread to send messages
    send_thread = threading.Thread(
        target=send_messages,
        args=(client,)
    )
    send_thread.start()

if __name__ == "__main__":
    start_client()