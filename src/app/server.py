from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer, Container
from textual.widgets import Header, Footer, LoadingIndicator, Label, Static
import os
import platform
import socket
import argparse
import re
import threading as thrd

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
    # TODO: Implement this method but for Windows
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


def awaitingConnection():
    s.listen(5)
    c, addr = s.accept()
    if addr:
        print("Conexión establecida con: ", addr)
        c.close()
        #TODO: Implement this method


class PantallaInicial(Static):
    """Initial Screen for connections"""

    def compose(self) -> ComposeResult:
        urName = getIpAddress()
        yield Container(
            Label("ESPERANDO UNA CONEXIÓN", classes="info", id="estadoConexion"),
            Label("IP: " + urName, classes="info", id="hostIp"),
            Label("PUERTO: " + str(port), classes="info", id="hostPort"),
            LoadingIndicator(id="indicadorEspera"),
            id="contenedorInicial",
        )
        thrd.Thread(target=awaitingConnection).start()


class ServerApp(App):
    """Manejo de la aplicacion"""
    CSS_PATH = "../style/server.tcss"
    BINDINGS = [("q", "quit", "Salir de la aplicación"), ("d", "toggle_dark", "Activar o desactivar el modo oscuro")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Container(PantallaInicial())

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark

    def action_quit(self) -> None:
        thrd.Thread(target=s.close()).start()
        quit()


if __name__ == "__main__":
    #Argument parsing
    entry = argparse.ArgumentParser("Server side of the crc app")
    entry.add_argument("--port", type=int, default=1337, help="Change the port of the server. Default is 1337")

    #Parse the arguments
    args = entry.parse_args()

    #Socket setup
    s = socket.socket()
    port = args.port
    s.bind((getIpAddress(), port))
    #ServerApp Init
    app = ServerApp()
    app.run()
