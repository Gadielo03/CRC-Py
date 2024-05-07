from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import Header, Footer, LoadingIndicator, Button, Label,Static


class PantallaInicial(Static):
    """Widget de espera de Conexion"""
    def compose(self) -> ComposeResult:
        yield Label("Esperando una conexión", id="estadoConexion")
        yield LoadingIndicator()

class serverApp(App):
    """Manejo de la aplicacion"""
    CSS_PATH = "../style/server.tcss"
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
