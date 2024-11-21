import json
import logging
import socket
import threading
import rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
import os
import flet as ft
from flet_core import ScrollMode, FontWeight
from screeninfo import get_monitors, Monitor

SERVER_HOST: str = 'localhost'  # Cambiar a la IP del servidor
SERVER_PORT: int = 5000
client_socket: socket.socket | None
connection_established: bool = False
global_params: dict = {}

try:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection_established = True
except Exception as ex:
    print(f"Error connecting to server: {ex}")
    exit()

# Generar par de claves RSA
public_key, private_key = rsa.newkeys(512)


def generate_aes_key():
    """Generate key AES."""
    return os.urandom(32)


def encrypt_aes(message, aes_key):
    """Encrypt message using AES."""
    cipher = Cipher(algorithms.AES(aes_key), modes.CFB(aes_key[:16]))
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(128).padder()
    padded_message = padder.update(message.encode()) + padder.finalize()
    return encryptor.update(padded_message) + encryptor.finalize()


def decrypt_aes(encrypted_message, aes_key):
    """Decrypt message using AES."""
    cipher = Cipher(algorithms.AES(aes_key), modes.CFB(aes_key[:16]))
    decryptor = cipher.decryptor()
    unpadder = padding.PKCS7(128).unpadder()
    padded_message = decryptor.update(encrypted_message) + decryptor.finalize()
    return unpadder.update(padded_message) + unpadder.finalize()


def receive_messages(page, message_list):
    """Receive messages from server."""
    while True:
        try:
            encrypted_message = client_socket.recv(4096)
            if encrypted_message:
                # Desencriptar mensaje (aquí suponemos que AES ya se comparte entre clientes)
                message = encrypted_message.decode('utf-8')  # Ajustar según el cifrado
                if message == "message sent":
                    continue
                msg: dict = json.loads(message)
                message_list.controls.append(ft.Text(
                    f"{msg['username']}: {msg['message']}",
                    text_align=ft.TextAlign.RIGHT,
                ))
                page.update()
        except Exception as ex:
            logging.error(f"Error to receive message: {ex}")
            break


def send_message(input_txt: ft.TextField, msg_list: ft.Column, p: ft.Page):
    try:
        ctx = client_socket
        if not ctx:
            return
        userdata = json.loads(global_params['userdata'])
        message = json.dumps({"username": userdata['username'], "channel": userdata['channel'], "message": input_txt.value})
        ctx.send(message.encode('utf-8'))
        msg_list.controls.append(ft.Text(
            f"{userdata['username']}: {userdata['message']}",
            text_align=ft.TextAlign.LEFT,
        ))
        logging.info(f"[CLIENT] Sent message: {message}")
    except Exception as e:
        logging.error(f"[ERROR] Error to send message: {e}")
    finally:
        input_txt.value = ""
        p.update()


def main(page: ft.Page):
    page.title = "Chat Seguro con Canales"
    page.scroll = "auto"

    # Solicitar nombre de usuario y canal
    global_params['userdata'] = json.dumps({"username": "pc2", "channel": "channel_1"})

    message_list = ft.Column(scroll=ScrollMode.AUTO, expand=True)
    input_field = ft.TextField(label="Write a message", expand=True)
    send_button = ft.ElevatedButton("Send",
                                    height=45,
                                    on_click=lambda e: send_message(input_field, message_list, page))

    if connection_established:
        monitor: Monitor = get_monitors()[0]
        screen_height: int = monitor.height
        calculated_height: int = int(screen_height * 0.5)

        page.add(
            ft.Column([
                ft.ResponsiveRow([
                    ft.Container(
                        ft.Text("Messages", size=20, weight=FontWeight.W_200),
                        col={"sm": 12, "md": 12, "xl": 12},
                    ),
                ]),
                ft.Divider(),
                ft.ResponsiveRow([
                    ft.Container(
                        ft.Column([message_list],
                                  scroll=ScrollMode.AUTO,
                                  adaptive=True,
                                  expand=True,
                                  height=calculated_height),
                        col=12
                    ),
                ]),
                ft.Divider(),
                ft.ResponsiveRow([
                    ft.Container(
                        input_field,
                        col=10),
                    ft.Container(
                        send_button,
                        col=2),
                ],
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            ], alignment=ft.MainAxisAlignment.END),
        )
    else:
        page.add(ft.Text("Error to connect with server"))

    client_socket.connect((SERVER_HOST, SERVER_PORT))
    client_socket.send(global_params['userdata'].encode('utf-8'))

    # Hilo para recibir mensajes
    threading.Thread(target=receive_messages, args=(page, message_list), daemon=True).start()

ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=5002)
