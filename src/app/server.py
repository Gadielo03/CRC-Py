from textual import on
from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer, Container
from textual.widgets import Header, Footer, LoadingIndicator, Button, Label, Static
from textual.screen import ModalScreen
import os
import platform
import socket
import argparse
import re
import asyncio


"""Functions for the classes"""


def getOS() -> str:
    """Gets the OS of the host"""
    osName = platform.system()
    return osName


def getWindowsIp() -> str:
    """Gets the IP address of the host in Windows"""
    ipv4_pattern = re.compile(r"IPv4.*: (\d+\.\d+\.\d+\.\d+)")
    output = os.popen('ipconfig').read()
    match = ipv4_pattern.search(output)
    if match:
        return match.group(1)
    else:
        return "127.0.0.1"


def getIpAddress() -> str:
    """Gets the IP address of the host"""
    # Check what OS is Server running
    whoAreWe = getOS()
    ipv4 = ""
    if whoAreWe == "Linux":
        ipv4 = os.popen('ip addr').read().split("inet ")[2].split("/")[0]
        pass
    elif whoAreWe == "Windows":
        ipv4 = getWindowsIp()
        pass
    elif whoAreWe == "Darwin":
        ipv4 = os.popen('ifconfig | grep "inet "').read().split("inet ")[2].split(" ")[0]
        pass

    return ipv4


class ErrorScreen(ModalScreen):
    def compose(self) -> ComposeResult:
        yield Container(
            Label("Error al Conectar"),
            Button(id="close-btn", label="Cerrar"),
            id="error-container"
        )

    @on(Button.Pressed)
    def on_button_click(self, event: Button.Pressed):
        if event.button.id == "close-btn":
            self.app.pop_screen()


class MessagesScreen(ModalScreen):
    BINDINGS = [("q", "quit", "Salir de la aplicación"), ("d", "toggle_dark", "Activar o desactivar el modo oscuro")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield ScrollableContainer(
            Label("Mensajes Recibidos 🤩"),
            id="msg-Container"
        )
        yield Footer()

    def action_toggle_dark(self) -> None:
        self.app.dark = not self.app.dark

    def action_quit(self) -> None:
        quit()


class InitialScreen(Static):
    """Initial Screen for connections"""
    server_task = None

    def compose(self) -> ComposeResult:
        urName = getIpAddress()
        label = Label("ESPERANDO UNA CONEXIÓN", classes="info", id="estadoConexion")
        indicator = LoadingIndicator(id="indicadorEspera")

        yield Container(
            label,
            Label("IP: " + urName, classes="info", id="hostIp"),
            Label("PUERTO: " + str(port), classes="info", id="hostPort"),
            indicator,
            id="contenedorInicial",
        )

    async def awaiting_connection(self):
        """Asynchronously listens for incoming connections and updates the UI."""
        s.listen(5)

        while True:  # Main loop
            try:
                client, addr = await asyncio.to_thread(s.accept)
                await self.app.push_screen(MessagesScreen())
                client.send("Connection established".encode())

                # Handle connection in a separate coroutine
                await asyncio.create_task(self.handle_connection(client))

            except:
                await self.app.push_screen(ErrorScreen())

    async def handle_connection(self, client: socket.socket):
        """Coroutine to manage individual connections."""
        try:
            pass
        finally:
            client.close()

    def on_mount(self):
        self.server_task = asyncio.create_task(self.awaiting_connection())

    def action_quit(self) -> None:
        self.server_task.cancel()  # Cancel the server task
        try:
            s.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass  # Ignore errors if the socket is already closed
        finally:
            s.close()
        self.app.exit()


class ServerApp(App):
    """Manejo de la aplicacion"""
    CSS_PATH = "../style/server.tcss"
    BINDINGS = [("q", "quit", "Salir de la aplicación"), ("d", "toggle_dark", "Activar o desactivar el modo oscuro")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Container(InitialScreen())

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark

    def action_quit(self) -> None:
        quit()


if __name__ == "__main__":
    #Argument parsing
    entry = argparse.ArgumentParser("Server side of the crc app")
    entry.add_argument("--port", "-p", type=int, default=1337, help="Change the port of the server. Default is 1337")

    #Parse the arguments
    args = entry.parse_args()

    #Socket setup
    s = socket.socket()
    port = args.port
    s.bind((getIpAddress(), port))
    #ServerApp Init
    app = ServerApp()
    app.run()
