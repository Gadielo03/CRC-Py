import argparse
import asyncio
import os
import platform
import re
import socket

from textual import events, on
from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer
from textual.containers import Container
from textual.screen import ModalScreen
from textual.widgets import Button, Footer, Header, Input, Label, Static

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

class DebugScreen(ModalScreen):
    def __init__(self, status: str):
        self.status = status
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Container(
            Label(self.status),
            Button(id="close-btn", label="Cerrar"),
            id="error-container"
        )

    @on(Button.Pressed)
    def on_button_click(self, event: Button.Pressed):
        if event.button.id == "close-btn":
            self.app.pop_screen()

class InitialScreen(Static):
    """Widget de espera de Conexion"""
    def __init__(self):
        super().__init__()
        self.client = None #Se declara un cliente al momento de iniciliazar InitialScreen
        #Despues se copia el client generado por la conexion
        #Y esta copia del client se puede utilizar en todos los metodos de InitialScreen
        #Usando self.client :3

    def compose(self) -> ComposeResult:

        yield ScrollableContainer(
            ScrollableContainer(id="chat-container"),
            id="MessagesContainer"
        )

        yield Container(
            Input(id="msg-input", placeholder="Mensaje"),
            Button(id="send-btn", label="Enviar"),
            id="input-container"
        )

    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "send-btn":
            inputMsg = self.query_one("#msg-input")
            chatContainer = self.query_one('#chat-container')

            try:
                msg = inputMsg.value

                data = (''.join(format(ord(x), 'b') for x in msg))
                # print("Entered data in binary format :", data)
                key = "1001"

                ans = encodeData(data, key)
                st = ans.encode('utf-8')
                #print("Encoded data to be sent to server in binary format :", ans)
                #s.sendto(ans.encode(), (ip, port))
                if self.client:
                    # self.client.sendto(st, (urName, port))
                    self.client.send(st)
                    self.app.call_later(self.update_chat, f"Message sent!")
                else:
                    self.app.call_later(self.update_chat, f"Message not send")



                chatContainer.mount(
                    Container(
                        Label(msg, classes="my-msg"), 
                        classes="my-msg-cont"
                    )
                )

            except Exception as e:
                # close the connection
                if self.client:
                    self.client.close()
                # self.app.push_screen(ErrorScreen())
                # self.app.push_screen(DebugScreen(f"Error al enviar el mensaje\n{e}"))
                self.app.call_later(self.update_chat,f"Error al recibir el mensaje\n{e}")

    async def awaiting_connection(self):
        """Asynchronously listens for incoming connections and updates the UI."""
        try:
            s.bind((urName, port))
            s.listen()
            self.app.call_later(self.update_chat, "Bind correcto!")
        except Exception as e:
            self.app.call_later(self.update_chat, f"Error al escuchar conexiones: {e}")
            return

        while True:  # Main loop
            try:
                client, addr = await asyncio.to_thread(s.accept)
                self.client = client
                self.app.call_later(self.update_chat, f"connection from {addr}")
                asyncio.create_task(self.handle_client(client))
            except Exception as e:
                self.app.call_later(self.update_chat,f"Error al recibir el mensaje\n{e}")
                # self.app.push_screen(DebugScreen(f"Error al recibir el mensaje\n{e}"))

    async def handle_client(self, client):
        """Handle communication with a connected client."""
        try:
            while True:
                msg = await asyncio.to_thread(client.recv, 2048)
                if msg:
                    decoded_msg = msg.decode('utf-8')
                    self.app.call_later(self.update_chat, decoded_msg)
                else:
                    break
        except Exception as e:
            self.app.call_later(self.update_chat, f"Receive error: {e}")
        #finally:
            #client.close()
            #self.app.call_later(self.update_chat, "Client disconnected")


    async def update_chat(self, msg):
        chatContainer = self.query_one("#chat-container")
        chatContainer.mount(
            Container(
                Label(msg, classes="rec-msg"),
                classes="rec-msg-cont"
            )
        )

    async def handle_connection(self, client: socket.socket):
        """Coroutine to manage individual connections."""
        try:
            pass
        finally:
            client.close()

    def on_mount(self) -> None:
        self.chat_task = asyncio.create_task(self.awaiting_connection())


class ServerApp(App):
    """Manejo de la aplicacion"""
    CSS_PATH = "../style/chat.tcss"
    BINDINGS = [("q", "quit", "Salir de la aplicación"), ("d", "toggle_dark", "Activar o desactivar el modo oscuro")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield ScrollableContainer(InitialScreen(), id="initial-container")

    def on_mount(self):
        self.title = "Chat Application"
        self.sub_title = "IP: " + urName + " " + "PUERTO: " + str(port)

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark

    def action_quit(self) -> None:
        s.close()
        quit()


if __name__ == "__main__":
    #Argument parsing
    entry = argparse.ArgumentParser("Server side of the crc app")
    entry.add_argument("--port", "-p", type=int, default=1337, help="Change the port of the server. Default is 1337")

    #Parse the arguments
    args = entry.parse_args()

    #Socket setup
    urName = getIpAddress()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = args.port


    #ServerApp Init
    app = ServerApp()
    app.run()