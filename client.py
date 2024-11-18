import socket
import threading
import logging
import flet as ft
from flet_core import ScrollMode, FontWeight
from screeninfo import get_monitors

SERVER_HOST: str = '192.169.0.163'  # Cambiar a la IP del servidor
SERVER_PORT: int = 5000
establish_connection: bool = False
title: str = "Chat Network"
monitor = get_monitors()[0]
screen_height = monitor.height
calculated_height = int(screen_height * 0.5)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', handlers=[
    logging.FileHandler("client.log"),
    logging.StreamHandler()
])

# Cliente socket
try:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))
    establish_connection = True
except Exception as ex:
    print(f"Connection error server: {ex}")
    exit(1)


def receive_messages(page, message_list):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            message_list.controls.append(ft.Text(message))
            if message != "":
                logging.info(f"[INFO] Message received: {message}")
            page.update()
        except Exception as e:
            logging.error(f"[ERROR] Error to receive message: {e}")
            page.update()
            break


def main(page: ft.Page):
    page.title = title
    page.scroll = "auto"

    if establish_connection:
        message_list = ft.Column(scroll=ScrollMode.AUTO, expand=True)

        input_field = ft.TextField(label="Write a message", expand=True)
        send_button = ft.ElevatedButton("Send",
                                        height=45,
                                        on_click=lambda e: send_message(input_field, message_list, page))

        def send_message(input_txt: ft.TextField, msg_list: ft.Column, p: ft.Page):
            message = input_txt.value
            try:
                client_socket.send(message.encode('utf-8'))
                msg_list.controls.append(ft.Text(f"Tú: {message}"))
                logging.info(f"[CLIENT] Sent message: {message}")
                input_txt.value = ""
                p.update()
            except Exception as e:
                logging.error(f"[ERROR] Error to send message: {e}")
                p.update()

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
        threading.Thread(target=receive_messages, args=(page, message_list), daemon=True).start()
    else:
        page.add(ft.Text("Error to connect with server"))


try:
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=5001)
except KeyboardInterrupt:
    if establish_connection:
        client_socket.close()
    exit(0)
