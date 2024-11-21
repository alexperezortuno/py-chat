import json
import socket
import threading
from typing import List

from click import command

from pchat.core.cliente import client_socket
from pchat.core.commons import log_lvl, log_str
from pchat.core.logger import get_logger
from pchat.core.utils import messages_income

# Configuración del servidor
HOST = '0.0.0.0'
PORT = 5000

# Logger
logger = get_logger(log_lvl, log_str, __name__)

# Almacena {username: (client_socket, channel, public_key)}
clients = {}
# Almacena {channel_name: [usernames]}
channels = {}


def broadcast(msg: bytes) -> None:
    """Enviar mensaje a todos los usuarios en el mismo canal."""
    data = json.loads(msg.decode('utf-8'))
    cmd = messages_income(data)
    cs, _, _ = clients[data['username']]

    if cmd == 'CREATE_CHANNEL' and data['channel'] not in channels:
        channels[f"{data['channel_name']}_{data['username']}"] = [data['username']]
        cs.send(json.dumps({"type": "CHANNEL_CREATED", "username": data['username']}).encode('utf-8'))
    if cmd == 'JOIN' and data['channel'] in channels:
        channels[data['channel']].append(data['username'])
        cs.send(json.dumps({"type": "CHANNEL_JOINED", "username": data['username']}).encode('utf-8'))
    if cmd == 'MESSAGE' and data['channel'] in channels:
        username = data['username']
        channel = data['channel']
        if channel in channels and username in channels[channel]:
            for username in channels[channel]:
                if username == sender_username:
                    cs.send("message sent".encode())
                cs.send(msg)

def remove_client(username):
    """Eliminar cliente del sistema."""
    if username in clients:
        client_socket, channel, _ = clients[username]
        if channel in channels and username in channels[channel]:
            channels[channel].remove(username)
        logger.info(f"Client disconnected: {username}")
        del clients[username]
        client_socket.close()


def handle_client(client_socket):
    """Manejar la conexión con un cliente."""
    try:
        command = messages_income(json.loads(client_socket.recv(1024).decode('utf-8')))
        logger.debug(f"Message: {command}")
        if command == 'CHANNELS':
            client_socket.send(json.dumps({'type': command, command: list(channels.keys())}).encode())
        if command == 'JOIN':
            userdata = json.loads(client_socket.recv(1024).decode('utf-8'))
            clients[userdata['username']] = (client_socket, [], None)

        # username = userdata['username']
        # channel = userdata['channel']

        # if channel not in channels:
        #     channels[channel] = []
        # channels[channel].append(username)
        # clients[username] = (client_socket, channel, None)  # Public key opcional
        # logger.info(f"Client {username} connected to channel {channel}")

        while True:
            # Recibir mensaje y retransmitirlo
            income = client_socket.recv(4096)
            if income:
                broadcast(income)
            else:
                break
    except Exception as ex:
        logger.error(f"Error handle client: {ex}")
    finally:
        logger.debug("Client disconnected")
        # remove_client(username)


def start_server():
    """Iniciar el servidor."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    logger.info(f"Servidor escuchando en {HOST}:{PORT}")

    while True:
        client_socket, _ = server.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket,))
        thread.start()


if __name__ == "__main__":
    start_server()
