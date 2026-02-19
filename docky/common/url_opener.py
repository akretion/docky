# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import atexit
import os
import socket
import subprocess
import sys


def url_opener(socket_name):
    @atexit.register
    def cleanup():
        if os.path.exists(socket_name):
            os.unlink(socket_name)

    # Ensure the socket file is removed on exit and if not
    # remove it before starting the server
    cleanup()

    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.bind(socket_name)
        s.listen()
        while True:
            connection, _ = s.accept()
            url = ""
            while True:
                data = connection.recv(1024)
                if not data:
                    break
                url += data.decode("utf-8")
            try:
                # Use a subprocess instead of directly the webbrowser module
                # in order to silence the output
                subprocess.check_call(
                    [sys.executable, "-m", "webbrowser", url],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except Exception:
                print(f"Failed to open URL: {url}", file=sys.stderr)
