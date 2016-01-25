import os
import urllib.parse

try:
    import psycopg2
except ImportError:
    pass

STATIC_URL_PREFIX = '/static/'
STATIC_FILE_DIR = 'static/' 

MIME_TABLE = {'.txt': 'text/plain',
              '.html': 'text/html',
              '.css': 'text/css',
              '.png': 'image/png',
              '.js': 'application/javascript',
             }

def dbConnect():
    urllib.parse.uses_netloc.append("postgres")
    url = urllib.parse.urlparse(os.environ["DATABASE_URL"])


    conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
    
    return conn
             
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
    elif environ['PATH_INFO'] == '/':
        return home_app(environ, start_response)
    elif environ['PATH_INFO'] == '/favicon.ico':
        return favicon_app(environ, start_response)
    else:
        return show_404_app(environ, start_response)
        
def home_app(environ, start_response):
    """Serve the homepage"""
    
    if environ['REQUEST_METHOD'] == 'POST':
        # the environment variable CONTENT_LENGTH may be empty or missing
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except (ValueError):
            request_body_size = 0

        # When the method is POST the variable will be sent
        # in the HTTP request body which is passed by the WSGI server
        # in the file like wsgi.input environment variable.
        request_body = environ['wsgi.input'].read(request_body_size)
        d = urllib.parse.parse_qs(request_body)
        
        t1 = d.get(b"t1",[b"no text recvd"])[0]
        d1 = d.get(b"d1",[b"no date recvd"])[0]
        
        content = b"Post received.<br>"
        content += t1
        content += b"<br>"
        #content += str(d1).encode("utf8")
        content += d1
        
    
    else:
        h = open ("home.html","rb")
        content = h.read()
        h.close()
    
    headers = [('content-type', 'text/html')]
    start_response('200 OK', headers)
    return [content]
    
def favicon_app(environ, start_response):
    """Serve the favicon"""
    
    headers = [('content-type', 'image/x-icon')]
    h = open ("static/favicon.ico","rb")
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
    print(path)
    
    # normalise any .. elements in path    
    path = os.path.normpath(path)
    
    print(path)

    # only serve the file if it is within STATIC_FILE_DIR and
    # if it exists
    
    #following line doesn't work on windows (uses \)
    #if path.startswith(STATIC_FILE_DIR) and os.path.exists(path):
    if os.path.exists(path): #this is potentially insecure
        h = open(path, 'rb')
        content = h.read()
        h.close()
         
        headers = [('content-type', content_type(path))]
        start_response('200 OK', headers)
        return [content]
    
    else:
        return show_404_app(environ, start_response)
    
def show_404_app(environ, start_response):
    """Serve 404"""
    
    data = b"404\n\n File not found."
    data += b"\n path: " + environ['PATH_INFO'].encode('utf8')
    data += b"\n script: " + environ['SCRIPT_NAME'].encode('utf8')
    
    start_response("200 OK", [
        ("Content-Type", "text/plain"),
        ("Content-Length", str(len(data)))
    ])
    return [data]