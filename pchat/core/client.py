import os
import socket
from typing import Any

import rsa
import json
import threading
import flet as ft

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from flet_core import ScrollMode, FontWeight
from screeninfo import Monitor, get_monitors
from pchat.core.commons import log_lvl, log_str
from pchat.core.logger import get_logger
from pchat.core.utils import messages_income, generate_random_string

logger = get_logger(log_lvl, log_str, __name__)
route_channel: str = "/channels"

SERVER_HOST: str = 'localhost'  # Cambiar a la IP del servidor
SERVER_PORT: int = 5000
client_socket: socket.socket | None
connection_established: bool = False
global_params: dict = {}
message_list = ft.Column(scroll=ScrollMode.AUTO, expand=True)
channel_list = ft.Column(scroll=ScrollMode.AUTO, expand=True)
temp_user: str = generate_random_string(25)

try:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))
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


def receive_messages():
    """Receive messages from server."""
    while True:
        try:
            encrypted_message: Any = client_socket.recv(4096).decode('utf-8')
            msg: dict = json.loads(encrypted_message)
            command: str = messages_income(msg)
            logger.debug(f"Message: {command}")
        except Exception as ex:
            logger.error(f"Error to receive message: {ex}")
            break


def send_message(input_txt: ft.TextField, msg_list: ft.Column, p: ft.Page):
    try:
        ctx = client_socket
        if not ctx:
            return
        userdata = json.loads(global_params['userdata'])
        message = json.dumps(
            {"username": userdata['username'], "channel": userdata['channel'], "message": input_txt.value})
        ctx.send(message.encode('utf-8'))
        msg_list.controls.append(ft.Text(
            f"{userdata['username']}: {userdata['message']}",
            text_align=ft.TextAlign.LEFT,
        ))
        logger.info(f"[CLIENT] Sent message: {message}")
    except Exception as e:
        logger.error(f"[ERROR] Error to send message: {e}")
    finally:
        input_txt.value = ""
        p.update()


def main(page: ft.Page):
    page.title = "Routes Example"

    monitor: Monitor = get_monitors()[0]
    screen_width: int = monitor.width
    screen_height: int = monitor.height
    calculated_width: int = int(screen_width * 0.5)
    calculated_height: int = int(screen_height * 0.5)

    channel_create_name = ft.TextField(label="Channel name", expand=True)
    create_channel_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Create channel"),
        content=ft.Column([
            channel_create_name,
            ft.ElevatedButton("Create", on_click=lambda x: create_channel_action(channel_create_name)),
        ]),
        open=True,
    )

    def join_user(user_name: ft.TextField):
        logger.debug(f"User name: {user_name}")
        if connection_established:
            if user_name.value == "":
                page.open(alert_user_empty)

            global_params['username'] = user_name.value
            client_socket.send(json.dumps({'type': 'JOIN', 'username': global_params['username']}).encode('utf-8'))
            page.go(route_channel)

    def handle_dialog_close(e):
        logger.debug("Dialog closed")
        page.close(alert_user_empty)
        page.update()

    alert_user_empty: ft.AlertDialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Error"),
        content=ft.Text("This is an alert message"),
        actions=[
            ft.TextButton("OK", on_click=handle_dialog_close),
        ],
    )

    def create_channel_action(create_channel_modal: ft.TextField) -> None:
        logger.debug(f"Create channel action {create_channel_modal}")
        if connection_established:
            if 'channel' not in global_params:
                global_params['channel'] = []

            new_channel: dict = {
                'type': 'CREATE_CHANNEL',
                'channel_name': create_channel_modal.value,
                'username': global_params['username']
            }

            global_params['channel'].append(new_channel)
            client_socket.send(json.dumps(new_channel).encode('utf-8'))
            page.close(create_channel_dialog)

    def create_channel(e):
        logger.debug("Create channel")
        if connection_established:
            page.open(create_channel_dialog)

    def route_change(route: str):
        input_field = ft.TextField(label="Please type your user name",
                                   expand=True,
                                   text_align=ft.TextAlign.CENTER)

        if page.views:
            page.views.clear()

        page.views.append(
            ft.View(
                "/",
                [
                    ft.AppBar(title=ft.Text("Chat"), bgcolor=ft.colors.SURFACE_VARIANT),
                    ft.Row(
                        [
                            ft.Column(
                                width=calculated_width,
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                adaptive=True,
                                spacing=5,
                                controls=[
                                    ft.Container(
                                        input_field,
                                        adaptive=True,
                                        alignment=ft.alignment.center,
                                    ),
                                    ft.Container(
                                        ft.ElevatedButton("Save", on_click=lambda e: join_user(input_field)),
                                        adaptive=True,
                                        alignment=ft.alignment.center
                                    )],
                            ),
                        ],
                        expand=True,
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
            )
        )
        if page.route == route_channel:
            if connection_established:
                client_socket.send(json.dumps({'type': 'CHANNELS', 'username': global_params['username']}).encode('utf-8'))
                content_channels = ft.Column([
                    ft.ResponsiveRow([
                        ft.Container(
                            channel_list,
                            col=12
                        ),
                    ]),
                    ft.ResponsiveRow([
                        ft.Container(
                            ft.ElevatedButton("CREATE CHANNEL", on_click=create_channel),
                            col=12
                        ),
                    ]),
                ])
            else:
                content_channels = ft.Text("Error to connect with server")

            page.views.append(
                ft.View(
                    route_channel,
                    [
                        ft.AppBar(title=ft.Text("Channels"),
                                  bgcolor=ft.colors.SURFACE_VARIANT,
                                  automatically_imply_leading=False),
                        content_channels,
                    ],
                )
            )
        if page.route == "/chat":
            write_field = ft.TextField(label="Write a message", expand=True)
            send_button = ft.ElevatedButton("Send",
                                            height=45,
                                            on_click=lambda e: send_message(write_field, message_list, page))
            if connection_established:
                monitor: Monitor = get_monitors()[0]
                screen_height: int = monitor.height
                calculated_height: int = int(screen_height * 0.5)

                content_chat = ft.Column([
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
                            write_field,
                            col=10),
                        ft.Container(
                            send_button,
                            col=2),
                    ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    )
                ], alignment=ft.MainAxisAlignment.END)
            else:
                content_chat = ft.Text("Error to connect with server")

            page.views.append(
                ft.View(
                    "/chat",
                    [
                        ft.AppBar(title=ft.Text("Chat"),
                                  bgcolor=ft.colors.SURFACE_VARIANT,
                                  automatically_imply_leading=False),
                        content_chat,
                    ]
                )
            )
        page.update()

        # Hilo para recibir mensajes
        threading.Thread(target=receive_messages, args=(), daemon=True).start()

    def view_pop(view: ft.View):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)


ft.app(main, view=ft.AppView.WEB_BROWSER)
