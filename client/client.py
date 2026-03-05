import socket
import threading
import sys

HOST = "127.0.0.1"
PORT = 5000


def receive_messages(sock):
    while True:
        try:
            message = sock.recv(1024).decode()
            if not message:
                break
            print(message)
        except:
            break


def send_messages(sock):
    while True:
        message = input()

        if message == "/quit":
            sock.send("/quit".encode())
            sock.close()
            sys.exit()

        sock.send(message.encode())


def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    username_prompt = client.recv(1024).decode()
    username = input(username_prompt)

    client.send(username.encode())

    receive_thread = threading.Thread(
        target=receive_messages, args=(client,))
    receive_thread.start()

    send_thread = threading.Thread(
        target=send_messages, args=(client,))
    send_thread.start()


if __name__ == "__main__":
    start_client()