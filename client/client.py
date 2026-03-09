import socket
import threading
import sys

HOST = "127.0.0.1"
PORT = 5000


def receive_messages(sock):

    while True:

        try:
            message = sock.recv(1024)

            if not message:
                break

            print(message.decode())

        except:
            break

def send_messages(sock):
    while True:
        try:
            message = input().strip()

            if not message:
                continue

            if message == "/quit":

                sock.send("QUIT".encode())
                sock.close()
                sys.exit()

            elif message == "/users":

                sock.send("USERS".encode())

            else:

                sock.send(f"MSG {message}".encode())

        except:
            break


def start_client():

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client.connect((HOST, PORT))

    prompt = client.recv(1024).decode()

    if prompt == "USERNAME":

        username = input("Enter username: ")

        client.send(username.encode())

    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.daemon = True
    receive_thread.start()

    send_thread = threading.Thread(target=send_messages, args=(client,))
    send_thread.daemon = True
    send_thread.start()

    receive_thread.join()
    send_thread.join()

if __name__ == "__main__":
    start_client()