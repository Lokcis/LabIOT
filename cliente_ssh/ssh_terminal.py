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
            channel = transport.open_session()
            channel.get_pty(term='xterm-256color', width=80, height=24)
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
