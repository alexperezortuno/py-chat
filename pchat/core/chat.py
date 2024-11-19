#!/usr/src/env python
# -*- coding: utf-8 -*-
import socket
import threading
import rsa
import flet as ft

from flet_core import ScrollMode, FontWeight
from screeninfo import get_monitors, Monitor
from pchat.core.commons import log_lvl, log_str, server_host, server_port, client_host, client_port, public_key, \
    private_key
from pchat.core.logger import get_logger

logger = get_logger(log_lvl, log_str, __name__)

title: str = "Chat Network"


class Chat:
    public_partner = None
    global_params: dict = None
    establish_connection: bool = False

    def client(self) -> socket.socket | None:
        try:
            logger.debug("Chat run")
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            h: int = self.global_params['server_host'] if self.global_params['server_host'] else server_host
            p: int = self.global_params['server_port'] if self.global_params['server_port'] else server_port
            client.connect((h, p))
            self.public_partner = rsa.PublicKey.load_pkcs1(client.recv(1024))
            client.send(public_key.save_pkcs1("PEM"))
            self.establish_connection = True
            self.global_params['client'] = client
            return client
        except Exception as ex:
            logger.error(f"Error to connect with server: {ex}")
            return None

    def host(self, params: dict) -> socket.socket:
        logger.debug("Chat run")
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        h: int = params['server_host'] if params['server_host'] else server_host
        p: int = params['server_port'] if params['server_port'] else server_port
        server.bind((h, p))
        logger.debug("Waiting for connection")
        server.listen(3)
        c, address = server.accept()
        logger.debug(f"Connected to {address}")
        c.send(public_key.save_pkcs1("PEM"))
        self.public_partner = rsa.PublicKey.load_pkcs1(c.recv(1024))
        logger.debug(f"Public partner: {self.public_partner}")

        return c

    def sending_messages(self, ctx, params) -> None:
        while True:
            message = input("")
            name: str = "" if params['name'] == "user" else params['name']
            ctx.send(rsa.encrypt(message.encode(), self.public_partner))
            print(f"{name}: {message}")

    def send_message(self, input_txt: ft.TextField, msg_list: ft.Column, p: ft.Page):
        message = input_txt.value
        try:
            ctx = self.global_params['client']
            if not ctx:
                return
            name: str = "" if self.global_params['name'] == "user" else self.global_params['name']
            ctx.send(rsa.encrypt(message.encode(), self.public_partner))
            msg_list.controls.append(ft.Text(f"Tú: {message}"))
            logger.info(f"[CLIENT] Sent message: {message}")
            input_txt.value = ""
            p.update()
        except Exception as e:
            logger.error(f"[ERROR] Error to send message: {e}")
            p.update()

    def receiving_messages(self, ctx, params) -> None:
        name: str = "" if params['name'] == "user" else params['name']
        while True:
            print(f"{name}: {rsa.decrypt(ctx.recv(1024), private_key).decode()}")

    def run_client(self, params) -> None:
        self.global_params = params
        c = self.client()
        if not c:
            return
        threading.Thread(target=self.sending_messages, args=(c, params)).start()
        threading.Thread(target=self.receiving_messages, args=(c, params)).start()

    def run_host(self, params) -> None:
        h = self.host(params)
        threading.Thread(target=self.sending_messages, args=(h, params)).start()
        threading.Thread(target=self.receiving_messages, args=(h, params)).start()

    def user_interface(self, page: ft.Page) -> None:
        page.title = title
        page.scroll = "auto"
        self.run_client(self.global_params)

        if self.establish_connection:
            monitor: Monitor = get_monitors()[0]
            screen_height: int = monitor.height
            calculated_height: int = int(screen_height * 0.5)
            message_list = ft.Column(scroll=ScrollMode.AUTO, expand=True)

            input_field = ft.TextField(label="Write a message", expand=True)
            send_button = ft.ElevatedButton("Send",
                                            height=45,
                                            on_click=lambda e: self.send_message(input_field, message_list, page))

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
            # threading.Thread(target=receive_messages, args=(page, message_list), daemon=True).start()
        else:
            page.add(ft.Text("Error to connect with server"))

    def run_user_interface(self, params: dict) -> None:
        self.global_params = params
        p: int = params['client_port'] if params['client_port'] else client_port
        ft.app(target=self.user_interface, view=ft.AppView.WEB_BROWSER, port=p)
