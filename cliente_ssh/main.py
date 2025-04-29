# main.py
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from controller import Controlador
from gui import Vista

def main():
    try:
        # Valores predeterminados quemados
        default_host = "200.115.181.211"
        default_port = 9000

        # Puedes cambiar estos valores o cargarlos desde un formulario futuro
        host = default_host
        puerto = default_port
        usuario = "tu_usuario"
        clave = "tu_clave"

        controlador = Controlador(host, puerto, usuario, clave)
        vista = Vista(controlador, default_host, default_port)
        Gtk.main()
    except Exception as e:
        pass

if __name__ == "__main__":
    main()
