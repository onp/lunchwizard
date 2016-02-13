import os
import urllib.parse
from string import Template
from dbConnect import dbConnect
import datetime
import cgi
import json

from openpyxl import load_workbook

STATIC_URL_PREFIX = '/static/'
STATIC_FILE_DIR = 'static/' 

MIME_TABLE = {'.txt': 'text/plain',
              '.html': 'text/html',
              '.css': 'text/css',
              '.png': 'image/png',
              '.js': 'application/javascript',
             }

class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime) or isinstance(o, datetime.date):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)
             
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
    elif environ['PATH_INFO'] == '/players':
        return players_app(environ, start_response)
    elif environ['PATH_INFO'] == '/excel':
        return excelUpload_app(environ, start_response)
    elif environ['PATH_INFO'] == '/score':
        return score_app(environ, start_response)
    elif environ['PATH_INFO'] == '/data.json':
        return data_app(environ, start_response)
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
        h = open ("index.html","rb")
        content = h.read()
        h.close()
    
    headers = [('content-type', 'text/html')]
    start_response('200 OK', headers)
    return [content]
    
def players_app(environ, start_response):
    """Serve the players page"""
    
    conn = dbConnect()
    
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
        
        np = d.get(b"p1")
        
        if np is not None:
            np = np[0].decode()
            with conn:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO players (name,join_date) VALUES (%s,%s);",
                            (np,datetime.date.today()))
                        
        
    
    h = open ("templates/players.html")
    content_template = Template(h.read())
    h.close()
    
    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT name FROM players;")
            plist = cur.fetchall()
    
    
    content = content_template.substitute(p1=str(plist))
    
    content = content.encode("utf8")
    
    headers = [('content-type', 'text/html')]
    start_response('200 OK', headers)
    
    conn.close()
    
    return [content]
    
def excelUpload_app(environ, start_response):
    """Handle excel data file uploads"""
    
    conn = dbConnect()
    
    plist = 'nothing posted'
    
    if environ['REQUEST_METHOD'] == 'POST':
        formdata = cgi.FieldStorage(environ=environ, fp=environ['wsgi.input'])
        
        if 'excelUpload' in formdata and formdata['excelUpload'].filename != "":
            wb = load_workbook(formdata['excelUpload'].file)
            ws = wb["raw"]
            playerIDs = []
            with conn:
                with conn.cursor() as cur:
                    for nameCell in ws.rows[0][1:]:
                        name = nameCell.value
                        cur.execute("SELECT player_id FROM players WHERE name = %s",(name,))
                        playerID = cur.fetchone()
                        if playerID is not None:
                            playerIDs.append(playerID[0])
                        else:
                            cur.execute("INSERT INTO players (name,join_date) VALUES (%s,%s) RETURNING player_id;",
                            (name,datetime.date.today()))
                            playerID = cur.fetchone()
                            playerIDs.append(playerID[0])
            
            with conn:
                with conn.cursor() as cur:
                    for game in ws.rows[1:]:
                        cur.execute("INSERT INTO games (date) VALUES (%s) RETURNING game_id",(game[0].value,))
                        gameID = cur.fetchone()[0]
                        scoreData = []
                        for col,pID in enumerate(playerIDs,1):
                            points = game[col].value
                            if points is not None:
                                scoreData.append((pID,gameID,points))
                        cur.executemany("INSERT INTO scores (player_ID,game_ID,points) VALUES (%s,%s,%s)",scoreData)
                        
            plist = 'data loaded.'
            
    h = open ("templates/excel.html")
    content_template = Template(h.read())
    h.close()
    
    content = content_template.substitute(p1=str(plist))
    
    content = content.encode("utf8")
    
    headers = [('content-type', 'text/html')]
    start_response('200 OK', headers)
    
    conn.close()
    
    return [content]
    
def score_app(environ, start_response):
    conn = dbConnect()
    
   # h = open ("templates/score.html")
   # content_template = Template(h.read())
   # h.close()
   # 
   # date1 = datetime.date(2015,8,1)
   # date2 = datetime.date(2015,11,4)
   # 
   # plist = "failed"
   # 
   # glist = "failed"
   # 
   # slist = "failed"
   # 
   # with conn:
   #     with conn.cursor() as cur:
   #         #get players that were active in the time period
   #         cur.execute("""SELECT DISTINCT player_id
   #         FROM scores INNER JOIN games
   #         ON (scores.game_id = games.game_id)
   #         WHERE games.date > %s
   #         AND games.date < %s """,
   #         (date1,date2))
   #         
   #         plist = [x[0] for x in cur.fetchall()]
   #         
   #     with conn.cursor() as cur:
   #         #get games that happened in the time period
   #         cur.execute("""SELECT game_id
   #         FROM games
   #         WHERE games.date > %s
   #         AND games.date < %s """,
   #         (date1,date2))
   #         
   #         glist = [x[0] for x in cur.fetchall()]
   #         
   #     with conn.cursor() as cur:
   #         #get scores for active players
   #         cur.execute("""SELECT players.name, scores.points
   #         FROM players LEFT OUTER JOIN scores
   #         ON (players.player_id = scores.player_id)
   #         WHERE game_id = %s """,
   #         (glist[0],))
   #         
   #         #pgList view setup
   #         """CREATE VIEW pgList AS
   #         SELECT * FROM games CROSS JOIN players
   #         """
   #         
   #         #score for every player in every game, even if they didn't play
   #         """SELECT pgList.name, scores.points, scores.game_id 
   #         FROM pgList LEFT OUTER JOIN scores
   #         ON (pgList.player_id = scores.player_id
   #         AND pgList.game_id = scores.game_id)
   #         """
   #         
   #         slist = cur.fetchall()
   # 
   # content = content_template.substitute(_players=str(plist),_games=str(glist),_scores=str(slist))
   # 
   # content = content.encode("utf8")
    
    h = open ("templates/score.html","rb")
    content = h.read()
    h.close()
    
    headers = [('content-type', 'text/html')]
    start_response('200 OK', headers)
    
    conn.close()
    
    return [content]
    
def data_app(environ,start_response):
    conn = dbConnect()
    
    date1 = datetime.date(2015,8,1)
    date2 = datetime.date(2015,11,4)
    
    plist = None
    data = None
    
    
    with conn:
        with conn.cursor() as cur:
            #get players that were active in the time period
            cur.execute("""SELECT DISTINCT player_id
            FROM datedScores
            WHERE date > %s
            AND date < %s """,
            (date1,date2))
            
            plist = [x[0] for x in cur.fetchall()]
        
        with conn.cursor() as cur:
            #get scores for active players
            data = {}
            for p in plist:
                cur.execute("""SELECT date, points
                FROM datedScores
                WHERE player_id = %s """,
                (p,))
                data[p] = cur.fetchall()
    
    jsonData = json.dumps(data,cls=DateTimeEncoder)

    content = jsonData.encode("utf8")
    
    headers = [('content-type', 'application/json')]
    start_response('200 OK', headers)

    conn.close()

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