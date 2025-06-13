# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import http.server
import socketserver
import threading
import urllib.parse
import webbrowser


class ForwardUrlHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Parse the query string
        query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        url = query.get("url", [""])[0]
        code = 200
        if url:
            status = webbrowser.open(url)
            response = "OK" if status else "Failed"
        else:
            response = "No URL parameter given"
            code = 500

        self.send_response(code)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(response.encode())
        return


def run_server():
    """Run a simple HTTP server to handle URL forwarding"""

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", 0), ForwardUrlHandler) as httpd:
        port = httpd.server_address[1]
        print("serving at port", port)
        httpd.serve_forever()
        print("out of the loop")


def spawn_url_forwarder():
    """Spawn a url forwarder in the host"""

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
