import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gdk
import threading

from ssh_terminal import SSHTerminal

class Vista(Gtk.Window):
    def __init__(self, controlador, default_host, default_port):
        super().__init__(title="Cliente SSH Upiloto")
        self.set_default_size(800, 500)
        self.controlador = controlador
        self.default_host = default_host
        self.default_port = default_port

        # Crear un HeaderBar personalizado
        self.header_bar = Gtk.HeaderBar()
        self.header_bar.set_title("Cliente SSH")
        self.header_bar.set_subtitle("Conéctate a tu servidor")
        self.header_bar.set_show_close_button(True)
        self.set_titlebar(self.header_bar)

        # Aplicar estilo CSS
        self.apply_custom_css()

        # Caja principal
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(self.box)

        # Caja para el botón de configuración en la parte superior
        self.header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.box.pack_start(self.header_box, False, False, 0)

        # Botón de configuración (ruedita) en la esquina superior derecha
        self.settings_button = Gtk.Button(label="⚙️")
        self.settings_button.set_halign(Gtk.Align.END)  # Alinear a la derecha
        self.settings_button.connect("clicked", self.on_settings_clicked)
        self.header_box.pack_end(self.settings_button, False, False, 0)

        # Formulario de conexión
        self.form_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.box.pack_start(self.form_box, False, False, 0)

        # Campo de entrada para el host (inicialmente oculto)
        self.host_entry = Gtk.Entry()
        self.host_entry.set_placeholder_text("Host")
        self.host_entry.set_visible(False)  # Ocultar inicialmente
        self.form_box.pack_start(self.host_entry, False, False, 0)
    
        # Campo de entrada para el puerto (inicialmente oculto)
        self.port_entry = Gtk.Entry()
        self.port_entry.set_placeholder_text("Puerto")
        self.port_entry.set_visible(False)  # Ocultar inicialmente
        self.form_box.pack_start(self.port_entry, False, False, 0)

        # Campo de entrada para el usuario
        self.user_entry = Gtk.Entry()
        self.user_entry.set_placeholder_text("Usuario")
        self.form_box.pack_start(self.user_entry, False, False, 0)

        # Campo de entrada para la clave
        self.password_entry = Gtk.Entry()
        self.password_entry.set_placeholder_text("Clave")
        self.password_entry.set_visibility(False)  # Ocultar texto
        self.form_box.pack_start(self.password_entry, False, False, 0)

        # Botón de conexión
        self.connect_button = Gtk.Button(label="Conectar")
        self.connect_button.connect("clicked", self.on_connect_clicked)
        self.form_box.pack_start(self.connect_button, False, False, 0)

        # Área para el terminal (se agregará dinámicamente)
        self.terminal_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.box.pack_start(self.terminal_box, True, True, 0)

        self.connect("destroy", self.on_destroy)
        self.show_all()

        # Asegurarse de que los campos de host y puerto estén ocultos
        self.host_entry.set_visible(False)
        self.port_entry.set_visible(False)

    def on_connect_clicked(self, button):
        # Obtener los valores de los campos
        host = self.host_entry.get_text() or self.default_host
        port = self.port_entry.get_text() or str(self.default_port)
        user = self.user_entry.get_text()
        password = self.password_entry.get_text()

        # Validar campos
        if not user or not password:
            self.show_error("Usuario y clave son obligatorios.")
            return

        # Ejecutar la conexión en un hilo separado
        def connect_thread():
            try:
                # Intentar conectar
                self.controlador.modelo.host = host
                self.controlador.modelo.puerto = int(port)
                self.controlador.modelo.usuario = user
                self.controlador.modelo.clave = password

                transport = self.controlador.conectar()

                # Actualizar la interfaz gráfica en el hilo principal
                GLib.idle_add(self.show_terminal, transport, user)

            except ValueError:
                GLib.idle_add(self.show_error, "El puerto debe ser un número válido.")
            except Exception as e:
                GLib.idle_add(self.show_error, f"Error al conectar: {e}")

        threading.Thread(target=connect_thread, daemon=True).start()

    def on_settings_clicked(self, button):
        # Alternar visibilidad de los campos de host y puerto
        is_visible = self.host_entry.get_visible()
        self.host_entry.set_visible(not is_visible)
        self.port_entry.set_visible(not is_visible)
        # No es necesario llamar a show_all aquí, ya que set_visible actualiza la visibilidad directamente.

    def show_terminal(self, transport, user):
        # Limpiar el formulario y mostrar el terminal
        self.form_box.hide()
        self.settings_button.hide()  # Ocultar la rueda de configuración
        terminal = SSHTerminal(transport, user)
        self.terminal_box.pack_start(terminal, True, True, 0)
        self.terminal_box.show_all()

    def show_error(self, message):
        # Mostrar un diálogo de error
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Error")
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

    def on_destroy(self, *args):
        try:
            # Desconectar al cerrar la ventana
            self.controlador.desconectar()
        except Exception as e:
            print(f"Error al desconectar: {e}")
        Gtk.main_quit()

    def apply_custom_css(self):
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"""
            headerbar {
                background: #FF0000; /* Rojo */
            }
        """)
        screen = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(
            screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
        )