import os

STATIC_URL_PREFIX = '/static/'
STATIC_FILE_DIR = 'static/' 

MIME_TABLE = {'.txt': 'text/plain',
              '.html': 'text/html',
              '.css': 'text/css',
              '.js': 'application/javascript',
             }  
             
def content_type(path):
    """Return a guess at the mime type for this path
    based on the file extension"""
    
    name, ext = os.path.splitext(path)
    
    if ext in MIME_TABLE:
        return MIME_TABLE[ext]
    else:
        return "application/octet-stream"

def appli(environ, start_response):
    """WSGI application to switch between different applications
    based on the request URI"""

    if environ['PATH_INFO'].startswith(STATIC_URL_PREFIX):
        return static_app(environ, start_response)
    elif environ['PATH_INFO'] == "":
        return home_app(environ, start_response)
    else:
        return show_404_app(environ, start_response)
        
def home_app(environ, start_response):
    """Serve the homepage"""
    
    headers = [('content-type', 'text/html')]
    h = open ("home.html","rb")
    content = h.read()
    h.close()
    
    start_response('200 OK', headers)
    return [content]
    
        
def static_app(environ, start_response):
    """Serve static files from the directory named
    in STATIC_FILES"""
    
    path = environ['PATH_INFO']
    # we want to remove '/static' from the start
    path = path.replace(STATIC_URL_PREFIX, STATIC_FILE_DIR)
    
    # normalise any .. elements in path    
    path = os.path.normpath(path)

    # only serve the file if it is within STATIC_FILE_DIR and
    # if it exists
    if path.startswith(STATIC_FILE_DIR) and os.path.exists(path):
        h = open(path, 'rb')
        content = h.read()
        h.close()
         
        headers = [('content-type', content_type(path))]
        start_response('200 OK', headers)
        return [content]
    
def show_404_app(environ, start_response):
    """Serve 404"""
    
    data = b"404\n\n File not found."
    data += b"\n" + environ['PATH_INFO'].encode("utf8")
    data += "\n" + environ['SCRIPT_NAME'].encode("utf8")
    
    start_response("200 OK", [
        ("Content-Type", "text/plain"),
        ("Content-Length", str(len(data)))
    ])
    return [data]