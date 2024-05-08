from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer, Container
from textual.widgets import Header, Footer, LoadingIndicator, Label, Static
import os
import socket
import threading as thrd


class PantallaInicial(Static):
    """Widget de espera de Conexion"""

    def getIpAddress(self) -> str:
        #TODO: Implement this method but for Windows
        """Gets the IP address of the host"""
        ipv4 = os.popen('ip addr').read().split("inet ")[2].split("/")[0]
        return ipv4

    def awaitingConnection(self):
        s = socket.socket()
        port = 1337
        s.bind((self.getIpAddress(), port))
        s.listen(5)
        c, addr = s.accept()
        if addr:
            print("Conexión establecida con: ", addr)
            c.close()
            #TODO: Implement this method

    def compose(self) -> ComposeResult:
        urName = self.getIpAddress()
        yield Container(
            Label("ESPERANDO UNA CONEXIÓN", classes="info", id="estadoConexion"),
            Label("IP: " + urName, classes="info", id="hostIp"),
            Label("PUERTO: 1337", classes="info", id="hostPort"),
            LoadingIndicator(id="indicadorEspera"),
            id="contenedorInicial",
        )
        thrd.Thread(target=self.awaitingConnection).start()


class serverApp(App):
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
        quit()



if __name__ == "__main__":
    app = serverApp()
    app.run()
