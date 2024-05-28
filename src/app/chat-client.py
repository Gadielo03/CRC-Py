import argparse
import asyncio

from textual import on, events
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


def binToStr(decoded_msg) -> str:
    """Converts binary to string, considering remaining bits and spaces."""
    # Remove the last 3 CRC bits
    # decoded_msg = decoded_msg[:-3]
    #
    # # Ensure the length is a multiple of 7
    # while len(decoded_msg) % 7 != 0:
    #     decoded_msg = '0' + decoded_msg

    binc = [decoded_msg[i:i + 7] for i in range(0, len(decoded_msg), 7)]
    nums = [int(chunk, 2) for chunk in binc]
    return ''.join(chr(num) for num in nums)


def calculate_parity_bits(data):
    data = [int(bit) for bit in data]
    n = len(data)
    r = 0
    while (2 ** r < n + r + 1):
        r += 1

    hamming_code = list(data)

    # Initialize parity bits to 0
    for i in range(r):
        hamming_code.insert((2 ** i) - 1, 0)

    # Calculate parity bits
    for i in range(r):
        parity_index = (2 ** i) - 1
        parity_sum = 0
        for j in range(parity_index, len(hamming_code), (2 * (parity_index + 1))):
            parity_sum += sum(hamming_code[j:j + parity_index + 1])
        hamming_code[parity_index] = parity_sum % 2

    return ''.join(map(str, hamming_code))


def detect_and_correct(hamming_code):
    hamming_code = [int(bit) for bit in hamming_code]
    r = 0
    while (2 ** r < len(hamming_code)):
        r += 1

    error_pos = 0
    for i in range(r):
        parity_index = (2 ** i) - 1
        parity_sum = 0
        for j in range(parity_index, len(hamming_code), (2 * (parity_index + 1))):
            parity_sum += sum(hamming_code[j:j + parity_index + 1])
        if parity_sum % 2 != 0:
            error_pos += 2 ** i

    if error_pos != 0:
        hamming_code[error_pos - 1] ^= 1  # Correct the error

    return ''.join(map(str, hamming_code))

def xor(a, b):
    result = []
    for i in range(1, len(b)):
        if a[i] == b[i]:
            result.append('0')
        else:
            result.append('1')
    return ''.join(result)

def mod2div(dividend, divisor):
    pick = len(divisor)
    tmp = dividend[0: pick]
    while pick < len(dividend):
        if tmp[0] == '1':
            tmp = xor(divisor, tmp) + dividend[pick]
        else:
            tmp = xor('0' * pick, tmp) + dividend[pick]
        pick += 1
    if tmp[0] == '1':
        tmp = xor(divisor, tmp)
    else:
        tmp = xor('0' * pick, tmp)
    checkword = tmp
    return checkword

def encodeData(data, key):
    l_key = len(key)
    appended_data = data + '0' * (l_key - 1)
    remainder = mod2div(appended_data, key)
    codeword = data + remainder
    return codeword

def crc_check(input_bits, key):
    l_key = len(key)
    appended_data = input_bits + '0' * (l_key - 1)
    remainder = mod2div(appended_data, key)
    return '1' not in remainder

class ConnectScreen(ModalScreen):
    def compose(self) -> ComposeResult:
        yield ScrollableContainer(
            Label("Agregar Amigo :)"),
            Input(placeholder="IP", id="input-ip"),
            Input(placeholder="PUERTO", id="input-port", type="number"),
            Container(
                Button(id="connect-btn", label="Conectar"),
                Button(id="close-btn", label="Cerrar"), id="connect-btns-container"),
            id="connect-container"
        )

    @on(Button.Pressed)
    def on_button_click(self, event: Button.Pressed):
        if event.button.id == "close-btn":
            self.app.pop_screen()
        elif event.button.id == "connect-btn":
            ipinput = self.query_one("#input-ip", Input)
            portinput = self.query_one("#input-port", Input)

            try:
                ip = str(ipinput.value)
                port = int(portinput.value)

                # connect to the server
                s.connect((ip, port))
                self.app.pop_screen()
            #s.bind((getIpAddress(), port))
            except Exception as e:
                s.close()
                self.app.push_screen(DebugScreen("Error al enviar el mensaje, Error: " + str(e)))


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
                msg = msg.replace(' ', '`')

                data = (''.join(format(ord(x), 'b') for x in msg))
                #print("Entered data in binary format :", data)
                key = "1001"

                #ans = encodeData(data, key)
                #print("Encoded data to be sent to server in binary format :", ans)
                #s.sendto(ans.encode(), (ip, port))
                ans = encodeData(data, key)
                # print("Encoded data to be sent to server in binary format :", ans)
                # s.sendto(ans.encode(), (ip, port))
                s.send(ans.encode('utf-8'))
                # self.mount(ans.encode())

                msg = msg.replace('`', ' ')
                chatContainer.mount(
                    Container(
                        Label(msg, classes="my-msg"), classes="my-msg-cont")
                )

            except:
                # close the connection
                s.close()
                self.app.push_screen(DebugScreen("Error al enviar el mensaje"))

    async def awaiting_messages(self):
        """Asynchronously listens for incoming Server Messages"""
        while True:  # Main loop
            try:
                    msg = await asyncio.to_thread(s.recv, 2048)
                    if msg:
                        decoded_msg = msg.decode('utf-8')
                        str1 = binToStr(decoded_msg)
                        str1 = str1.replace('`', ' ')
                        self.app.call_later(self.update_chat, str1 + "\n" + decoded_msg)
                    else:
                        break

            except Exception as e:
                self.app.call_later(self.update_chat, f"Error al recibir el mensaje\n{e}")
                await asyncio.sleep(5)
                # self.app.push_screen(DebugScreen(f"Error al recibir el mensaje\n{e}"))

    async def update_chat(self, msg):
        chatContainer = self.query_one("#chat-container")
        chatContainer.mount(
            Container(
                Label(msg, classes="rec-msg"),
                classes="rec-msg-cont"
            )
        )

    def on_mount(self) -> None:
        self.chat_task = asyncio.create_task(self.awaiting_messages())


class ChatApp(App):
    """Manejo de la aplicacion"""
    CSS_PATH = "../style/chat.tcss"
    BINDINGS = [("q", "quit", "Salir de la aplicación"), ("d", "toggle_dark", "Activar o desactivar el modo oscuro"),
                ("a", "connect_screen", "Agregar amigos")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield ScrollableContainer(InitialScreen(), id="initial-container")

    def on_mount(self) -> None:
        self.title = "Chat Client Application"

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark

    def action_quit(self) -> None:
        quit()

    def action_connect_screen(self) -> None:
        self.push_screen(ConnectScreen())


if __name__ == "__main__":
#Argument parsing
    entry = argparse.ArgumentParser("Client side of the crc app")
    entry.add_argument("--port", "-p", type=int, default=0000, help="Change the port of the client. Default is 1111")

    #Parse the arguments
    args = entry.parse_args()

    #Socket setup
    ip = getIpAddress()
    port = args.port

    # Create a socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    app = ChatApp()
    app.run()
