from http.server import *


def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler):
    """Serve simple static content."""
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

run()
