from wsgiref.simple_server import make_server
from apper import appli

httpd = make_server('', 8001, appli)
print("Serving HTTP on port 8000...")

# Respond to requests until process is killed
httpd.serve_forever()