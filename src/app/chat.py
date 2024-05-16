import argparse

from textual import on
from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import Header, Footer, Input, Button, Label, Static
from textual.screen import ModalScreen
from textual.containers import Container
import os
import platform
import re
# Import socket module
import socket
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

def getOS() -> str:
    """Gets the OS of the host"""
    osName = platform.system()
    return osName

def xor(a, b):
    # initialize result
    result = []

    # Traverse all bits, if bits are
    # same, then XOR is 0, else 1
    for i in range(1, len(b)):
        if a[i] == b[i]:
            result.append('0')
        else:
            result.append('1')

    return ''.join(result)


# Performs Modulo-2 division
def mod2div(dividend, divisor):
    # Number of bits to be XORed at a time.
    pick = len(divisor)

    # Slicing the dividend to appropriate
    # length for particular step
    tmp = dividend[0: pick]

    while pick < len(dividend):

        if tmp[0] == '1':

            # replace the dividend by the result
            # of XOR and pull 1 bit down
            tmp = xor(divisor, tmp) + dividend[pick]

        else:  # If leftmost bit is '0'

            # If the leftmost bit of the dividend (or the
            # part used in each step) is 0, the step cannot
            # use the regular divisor; we need to use an
            # all-0s divisor.
            tmp = xor('0' * pick, tmp) + dividend[pick]

        # increment pick to move further
        pick += 1

    # For the last n bits, we have to carry it out
    # normally as increased value of pick will cause
    # Index Out of Bounds.
    if tmp[0] == '1':
        tmp = xor(divisor, tmp)
    else:
        tmp = xor('0' * pick, tmp)

    checkword = tmp
    return checkword


# Function used at the sender side to encode
# data by appending remainder of modular division
# at the end of data.
def encodeData(data, key):
    l_key = len(key)

    # Appends n-1 zeroes at end of data
    appended_data = data + '0' * (l_key - 1)
    remainder = mod2div(appended_data, key)

    # Append remainder in the original data
    codeword = data + remainder
    return codeword

class ConnectScreen(ModalScreen):
    def compose(self) -> ComposeResult:
        yield ScrollableContainer(
            Label("Agregar Amigo :)"),
            Input(placeholder="IP",id="input-ip"),
            Input(placeholder="PUERTO",id="input-port"),
            Container(
            Button(id="connect-btn", label="Conectar"),
            Button(id="close-btn", label="Cerrar"),id="connect-btns-container"),
            id="connect-container"
        )

    @on(Button.Pressed)
    def on_button_click(self, event: Button.Pressed):
        if event.button.id == "close-btn":
            self.app.pop_screen()
        elif( event.button.id == "connect-btn"):
            ipinput = self.query_one('#input-ip')
            portinput = self.query_one('#input-port')
            try :
                ip = str(ipinput.value)
                port = int(portinput.value)

                # Create a socket object
                s = socket.socket()
                # connect to the server
                s.connect((ip, port))
            except:
                s.close()
                self.app.push_screen(ErrorScreen())


class ErrorScreen(ModalScreen):
    def compose(self) -> ComposeResult:
        yield Container(
            Label("Error"),
            Button(id="close-btn", label="Cerrar"),
            id="error-container"
        )

    @on(Button.Pressed)
    def on_button_click(self, event: Button.Pressed):
        if event.button.id == "close-btn":
            self.app.pop_screen()


class InitialScreen(Static):
    """Widget de espera de Conexion"""

    def compose(self) -> ComposeResult:

        label = Label("ESPERANDO UNA CONEXIÓN", classes="info", id="estadoConexion")

        yield ScrollableContainer(
            Container(
            Container(id="chat-container"),
            id="MessagesContainer")
        )
        yield Container(
            Input(id="msg-input",placeholder="Mensaje"),
            Button(id="send-btn",label="Enviar"),
            id="input-container"
        )

    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed):
        global s
        if event.button.id == "send-btn":
            #ipinput = self.query_one("#ip", Input)
            #portinput = self.query_one("#port", Input)

            try:
                ip = str(ipinput.value)
                port = int(portinput.value)

                # Create a socket object
                s = socket.socket()
                # connect to the server
                s.connect((ip, port))



            except:
                # close the connection
                s.close()
                self.app.push_screen(ErrorScreen())
            else:
                self.app.push_screen(MessagesScreen())


class ChatApp(App):
    """Manejo de la aplicacion"""
    CSS_PATH = "../style/chat.tcss"
    BINDINGS = [("q", "quit", "Salir de la aplicación"), ("d", "toggle_dark", "Activar o desactivar el modo oscuro"), ("a", "connect_screen", "Agregar amigos")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield ScrollableContainer(InitialScreen(), id="initial-container")

    def on_mount(self) -> None:
        self.title = "Chat Application"
        self.sub_title = "IP: " + urName + " " + "PUERTO: " + str(port)

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark

    def action_quit(self) -> None:
        quit()

    def action_connect_screen(self) -> None:
        self.push_screen(ConnectScreen())

if __name__ == "__main__":
    entry = argparse.ArgumentParser("Server side of the crc app")
    entry.add_argument("--port", "-p", type=int, default=1337, help="Change the port of the server. Default is 1337")

    # Parse the arguments
    args = entry.parse_args()

    urName = getIpAddress()
    port = args.port

    app = ChatApp()
    app.run()
