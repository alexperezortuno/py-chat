import json
import socket
import threading
from typing import Any

from pchat.core.commons import log_lvl, log_str
from pchat.core.logger import get_logger
from pchat.core.utils import messages_income

# Configuración del servidor
HOST = '0.0.0.0'
PORT = 5000

# Logger
logger: Any = get_logger(log_lvl, log_str, __name__)
tag: str = "[SERVER]"

# Almacena {username: (client_socket, channel, public_key)}
clients = {}
# Almacena {channel_name: [usernames]}
channels = {}


def broadcast(msg: bytes, client_socket: Any) -> None:
    """Enviar mensaje a todos los usuarios en el mismo canal."""
    data: Any = json.loads(msg.decode('utf-8'))
    cmd = messages_income(data)
    logger.debug(f"{tag} Broadcast: {cmd}")
    if cmd == 'CHANNELS':
        username = data['username']
        if username in clients:
            c: list = list(channels.keys())
            clients[username][0].send(json.dumps({'type': "CHANNELS", "list": c}).encode('utf-8'))
    if cmd == 'CREATE_CHANNEL':
        username = data['username']
        channel = data['channel_name']
        if channel not in channels:
            channels[channel] = [username]
            clients[username][0].send(json.dumps({"type": "CHANNEL_CREATED"}).encode('utf-8'))
        else:
            client_socket.send(json.dumps({"type": "CHANNEL_ERROR"}).encode('utf-8'))

def remove_client(username):
    """Eliminar cliente del sistema."""
    if username in clients:
        client_socket, channel, _ = clients[username]
        if channel in channels and username in channels[channel]:
            channels[channel].remove(username)
        logger.info(f"Client disconnected: {username}")
        del clients[username]
        client_socket.close()

def manage_messages(client_socket):
    """Recibir mensaje de un cliente."""
    try:
        data: Any = json.loads(client_socket.recv(1024).decode('utf-8'))
        command = messages_income(data)
        logger.debug(f"{tag} Message: {command}")
        if command == 'JOIN':
            userdata = data
            username = userdata['username']
            clients[username] = (client_socket, [], None)
            client_socket.send(json.dumps({"type": "JOIN_SUCCESS", "username": username}).encode('utf-8'))
    except Exception as ex:
        logger.error(f"{tag} Error manage message: {ex}")

def handle_client(client_socket):
    """Manejar la conexión con un cliente."""
    try:
        manage_messages(client_socket)
        while True:
            # Recibir mensaje y retransmitirlo
            income = client_socket.recv(4096)
            if income:
                broadcast(income, client_socket)
            else:
                break
    except Exception as ex:
        logger.error(f"{tag} Error handle client: {ex}")
    finally:
        logger.debug(f"{tag} Client disconnected")
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
