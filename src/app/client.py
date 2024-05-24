from textual import on
from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import Header, Footer, Input, Button, Label, Static
from textual.screen import ModalScreen
from textual.containers import Container
# Import socket module
import socket

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

class MessagesScreen(ModalScreen):

    BINDINGS = [("q", "quit", "Salir de la aplicación"), ("d", "toggle_dark", "Activar o desactivar el modo oscuro")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield ScrollableContainer(
            Label("Mensajeria :)"),
            Input(id="msg-input",placeholder="Mensaje"),
            Container(
            Button(id="snd-msg-btn",label="Enviar"),
                    Label("  "),
                    Button(id="ext-btn",label="Salir"),
                    id="msg-btn-Container"),
            id="msg-Container"
        )
        yield Footer()

    def action_toggle_dark(self) -> None:
        self.app.dark = not self.app.dark

    def action_quit(self) -> None:
        quit()

    @on(Button.Pressed)
    def SendMessage(self,event: Button.Pressed):
        if event.button.id == "snd-msg-btn":
            messageinput = self.query_one('#msg-input',Input)
            message = messageinput.value
            data = (''.join(format(ord(x), 'b') for x in message))
            # print("Entered data in binary format :", data) todo
            key = "1001"
            ans = encodeData(data, key)
            # print("Encoded data to be sent to server in binary format :", ans)
            # s.sendto(ans.encode(), (ip, port))
            s.send(ans.encode('utf-8'))
            #self.mount(ans.encode())
            #self.app.push_screen(ErrorScreen())
        elif event.button.id == "ext-btn":
            s.close()
            self.app.pop_screen()

class ErrorScreen(ModalScreen):
    def compose(self) -> ComposeResult:
        yield Container(
            Label("Error"),
            Button(id="close-btn",label="Cerrar"),
            id="error-container"
        )

    @on(Button.Pressed)
    def on_button_click(self,event: Button.Pressed):
        if event.button.id == "close-btn":
            self.app.pop_screen()


class InitialScreen(Static):
    """Widget de espera de Conexion"""

    def compose(self) -> ComposeResult:
        yield ScrollableContainer(
            Label("INGRESE LOS DATOS :"),
            Input(id="ip", placeholder="IP", type="text"),
            Input(id="port", placeholder="PORT", type="number", max_length=5),
            Button(id="send-btn", label="Conectar"),
            Label(id="output"),
        )


    @on(Button.Pressed)
    def on_button_Pressed(self, event: Button.Pressed):
        global s
        if event.button.id == "send-btn":
            ipinput = self.query_one("#ip", Input)
            portinput = self.query_one("#port", Input)

            try:
                ip = str(ipinput.value)
                port = int(portinput.value)

                # Create a socket object
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # connect to the server
                s.connect((ip, port))
                


            except:
                # close the connection
                s.close()
                self.app.push_screen(ErrorScreen())
            else:
                self.app.push_screen(MessagesScreen())


class ClientApp(App):
    """Manejo de la aplicacion"""
    CSS_PATH = "../style/client.tcss"
    BINDINGS = [("q", "quit", "Salir de la aplicación"), ("d", "toggle_dark", "Activar o desactivar el modo oscuro")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield ScrollableContainer(InitialScreen(), id="initial-container")

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark

    def action_quit(self) -> None:
        quit()


if __name__ == "__main__":
    ip = ""
    port = 0000
    s = ''
    app = ClientApp()
    app.run()
