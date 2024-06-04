import argparse
import asyncio
import os
import platform
import re
import socket
import random

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

def ErrorData(data):
    data_list = list(data)
    number = random.randint(0, len(data_list) - 1)
    if data_list[number] == '0':
        data_list[number] = '1'
    elif data_list[number] == '1':
        data_list[number] = '0'
    return ''.join(data_list)

def calculate_parity_bits(data):
    """Calculate parity bits for Hamming code."""
    n = len(data)
    r = 1
    while (2**r) < (n + r + 1):
        r += 1
    return r

def hamming_code(data):
    """Generate Hamming code with parity bits."""
    n = len(data)
    r = calculate_parity_bits(data)
    data = list(data)
    j = 0
    k = 1
    m = len(data)

    # Insert parity bits into their positions
    while k <= m + r:
        if k == 2**j:
            data.insert(k-1, '0')
            j += 1
        k += 1

    # Calculate parity bits
    for i in range(r):
        val = 0
        for j in range(1, len(data) + 1):
            if j & (2**i) == (2**i):
                val = val ^ int(data[j-1])
        data[2**i - 1] = str(val)

    return ''.join(data)

def check_hamming_code(data):
    """Check and correct Hamming code errors."""
    n = len(data)
    r = calculate_parity_bits(data)
    data = list(data)
    error_pos = 0

    # Calculate parity bits and identify error position
    for i in range(r):
        val = 0
        for j in range(1, n + 1):
            if j & (2**i) == (2**i):
                val = val ^ int(data[j-1])
        error_pos += val * (2**i)

    if error_pos:
        data[error_pos-1] = '1' if data[error_pos-1] == '0' else '0'

    return ''.join(data), error_pos


def decode_hamming_code(data):
    """Decode Hamming code by removing parity bits."""
    n = len(data)
    r = calculate_parity_bits(data)
    corrected_data = list(data)
    j = 0
    decoded_data = []

    for i in range(1, n + 1):
        if i != 2 ** j:
            decoded_data.append(corrected_data[i - 1])
        else:
            j += 1

    return ''.join(decoded_data)


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
        self.client = None 
        #Se declara un cliente al momento de iniciliazar InitialScreen
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
                msg = msg.replace(' ', '`')
                data = (''.join(format(ord(x), 'b') for x in msg))
                key = "1001"

                ans = encodeData(data, key)
                hamming_encoded = hamming_code(ans)

                msg = msg.replace('`', ' ')
                if self.client:
                    if noise > 0:
                        number = random.randint(1, 5)
                        if number <= noise:
                            errorAns = ErrorData(hamming_encoded)
                            self.client.send(errorAns.encode('utf-8'))
                            chatContainer.mount(
                                Container(
                                    Label(f"{msg}\n{ans}\nw/Error: {errorAns}", classes="my-msg"),
                                    classes="my-msg-cont"
                                )
                            )
                        else:
                            self.client.send(hamming_encoded.encode('utf-8'))
                            chatContainer.mount(
                                Container(
                                    Label(msg, classes="my-msg"),
                                    classes="my-msg-cont"
                                )
                            )
                    else:
                        self.client.send(hamming_encoded.encode('utf-8'))
                        chatContainer.mount(
                            Container(
                                Label(msg, classes="my-msg"),
                                classes="my-msg-cont"
                            )
                        )
                else:
                    self.app.push_screen(DebugScreen(f"Error al enviar el mensaje"))





            except Exception as e:
                # close the connection
                if self.client:
                    self.client.close()
                self.app.push_screen(DebugScreen(f"Error al enviar el mensaje\n{e}"))

    async def awaiting_connection(self):
        """Asynchronously listens for incoming connections and updates the UI."""
        try:
            s.bind((urName, port))
            s.listen()
        except Exception as e:
            self.app.push_screen(DebugScreen(f"Error al crear conexion\n{e}"))
            return

        while True:  # Main loop
            try:
                client, addr = await asyncio.to_thread(s.accept)
                self.client = client
                self.app.push_screen(DebugScreen(f"Established connection with:\n{addr}"))
                asyncio.create_task(self.handle_client(client))
            except Exception as e:
                self.app.push_screen(DebugScreen(f"Error al enviar el mensaje\n{e}"))

    async def handle_client(self, client):
        """Handle communication with a connected client."""
        try:
            while True:
                msg = await asyncio.to_thread(client.recv, 2048)
                if msg:
                    decoded_msg = msg.decode('utf-8')
                    cipher = decode_hamming_code(decoded_msg)
                    crc_valid = crc_check(cipher, '1001')
                    if not crc_valid:
                        corrected_msg, error_pos = check_hamming_code(decoded_msg)
                        data_part = corrected_msg[:-3]
                        ans = decode_hamming_code(data_part)
                        bad_str = binToStr(decoded_msg)
                        str1 = binToStr(ans)
                        str1 = str1.replace('`', ' ')
                        self.app.call_later(self.update_chat, f"Message w/Error: {bad_str}\nCorrected Message: {str1}\nBin w/Error: {data_part}\nCorrected Bin: {ans}\nError at bit: {error_pos}\nCRC Valid: {crc_valid}")
                    else:
                       ans = decode_hamming_code(decoded_msg)
                       str1 = binToStr(ans)
                       str1 = str1.replace('`', ' ')
                       self.app.call_later(self.update_chat, f"Decoded Message: {str1}\nDecoded Bin: {decoded_msg}\nCRC Valid: {crc_valid}")




                else:
                    break
        except Exception as e:
            self.app.push_screen(DebugScreen(f"Error al recibir el mensaje\n{e}"))


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
    BINDINGS = [("q", "quit", "Exit"), ("d", "toggle_dark", "Toggle Dark Mode")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield ScrollableContainer(InitialScreen(), id="initial-container")

    def on_mount(self):
        self.title = "Chat Application"
        self.sub_title = "IP: " + urName + " " + "PORT: " + str(port) + " " + "NOISE: " + str(noise)

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark

    def action_quit(self) -> None:
        s.close()
        quit()


if __name__ == "__main__":
    #Argument parsing
    entry = argparse.ArgumentParser("Server side of the crc app")
    entry.add_argument("--port", "-p", type=int, default=1337, help="Change the port of the server. Default is 1337")
    entry.add_argument("--noise", "-n", type=int, default=0, help="Add noise to data transmission. Default is 0")

    #Parse the arguments
    args = entry.parse_args()
    noise = args.noise
    if noise < 0:
        noise = 0
    if noise > 5:
        noise = 5

    #Socket setup
    urName = getIpAddress()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = args.port


    #ServerApp Init
    app = ServerApp()
    app.run()
