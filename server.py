import os
import socket
import threading
import logging

# Configuración del servidor
HOST = os.getenv('HOST', '0.0.0.0')
PORT = os.getenv('PORT', 5000)

# Logger configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', handlers=[
    logging.FileHandler("server.log"),
    logging.StreamHandler()
])

clients = []

def broadcast(message, sender_socket):
    """Send message to all clients."""
    for client in clients:
        if client != sender_socket:
            client.send(message)

def handle_client(client_socket, client_address):
    """Manage client connection."""
    logging.info(f"Client connected: {client_address}")
    while True:
        try:
            message = client_socket.recv(1024)
            if message:
                logging.info(f"Message receive from {client_address}: {message.decode('utf-8')}")
                broadcast(message, client_socket)
        except Exception as ex:
            logging.info(f"Client disconnect: {client_address}")
            logging.error(f"Error: {ex}")
            clients.remove(client_socket)
            client_socket.close()
            break

def start_server() -> None:
    server: socket.socket | None = None
    try:
        """Starting server"""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((HOST, PORT))
        server.listen()
        logging.info(f"Server listen in {HOST}:{PORT}")

        while True:
            client_socket, client_address = server.accept()
            clients.append(client_socket)
            logging.info(f"Connection accepted {client_address}")

            thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            thread.start()
    except Exception | KeyboardInterrupt as ex:
        if ex == KeyboardInterrupt:
            logging.info("Server stopped")
        else:
            logging.error(f"Error: {ex}")
        if server:
            server.close()
        exit(1)

if __name__ == "__main__":
    start_server()
