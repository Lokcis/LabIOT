# ssh_terminal.py
import gi
gi.require_version("Vte", "2.91")
from gi.repository import Vte, GLib

import threading

class SSHTerminal(Vte.Terminal):
    def __init__(self, transport, usuario):
        super().__init__()
        self.spawn_pty(transport, usuario)

    def spawn_pty(self, transport, usuario):
        if not transport:
            return

        try:
            # Obtener el tamaño actual del terminal embebido
            cols, rows = self.get_column_count(), self.get_row_count()
            if cols == 0 or rows == 0:
                cols, rows = 80, 24  # Valores predeterminados si no se puede obtener el tamaño

            channel = transport.open_session()
            channel.get_pty(term="xterm-256color", width=cols, height=rows)
            channel.invoke_shell()
        except Exception as e:
            return

        def _read_from_channel():
            try:
                while True:
                    data = channel.recv(1024)
                    if not data:
                        break
                    GLib.idle_add(self.feed, data)
            except Exception:
                pass
            finally:
                channel.close()

        threading.Thread(target=_read_from_channel, daemon=True).start()

        def _write_to_channel(terminal, data, length):
            try:
                channel.send(data[:length])
            except Exception:
                pass

        self.connect("commit", _write_to_channel)

        # Conectar el evento de cambio de tamaño del terminal embebido
        self.connect("size-allocate", self._on_size_allocate, channel)

    def _on_size_allocate(self, terminal, allocation, channel):
        try:
            # Obtener el tamaño actual del terminal embebido
            cols, rows = terminal.get_column_count(), terminal.get_row_count()
            if cols > 0 and rows > 0:
                # Notificar al servidor remoto el nuevo tamaño del terminal
                channel.resize_pty(width=cols, height=rows)
        except Exception as e:
            pass