from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import Header, Footer, Input, Button, Label,Static
from textual.containers import Container


class PantallaInicial(Static):
    """Widget de espera de Conexion"""
    def compose(self) -> ComposeResult:
            yield Label("INGRESE LOS DATOS :")
            yield Input(id="ip",placeholder="IP",type="text")
            yield Input(id="port",placeholder="PORT", type="number",max_length=4)
            yield Input(id="text",placeholder="TEXT", type="text")
            yield Button(id="send-btn",label="ENVIAR")

class serverApp(App):
    """Manejo de la aplicacion"""
    CSS_PATH = "../style/client.tcss"
    BINDINGS = [("q", "quit", "Salir de la aplicación"), ("d", "toggle_dark", "Activar o desactivar el modo oscuro")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield ScrollableContainer(PantallaInicial())


    def action_toggle_dark(self) -> None:
        self.dark = not self.dark

    def action_quit(self) -> None:
        quit()


if __name__ == "__main__":
    app = serverApp()
    app.run()
