# Simple Chat Application Report

## 1. Introduction

This project implements a multi-client chat application using TCP socket programming.

The goal is to understand client-server communication and concurrency.

## 2. Architecture

The system follows a client-server architecture.

Server manages connections and broadcasts messages.

Clients send and receive messages.

## 3. Concurrency

Concurrency is implemented using Python threads.

Each client connection runs in a separate thread.

## 4. Communication Protocol

JOIN username
MSG message
QUIT

## 5. Testing

Tested with:

- Multiple clients
- Simultaneous messages
- Client disconnect
- Long messages

## 6. Challenges

- Handling disconnected clients
- Synchronizing shared client list
- Managing multiple threads

## 7. Conclusion

The system successfully supports multi-client chat using TCP sockets.