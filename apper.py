import os
import urllib.parse
from string import Template
from dbConnect import dbConnect
import datetime
from flask import Flask,jsonify,request,render_template

from openpyxl import load_workbook


app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

@app.route("/")
def index():

    h = open ("index.html","rb")
    content = h.read()
    h.close()
    
    return content

@app.route("/data.json")
def data():
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

    return jsonify(data)
    
@app.route("/excel",methods=['POST','GET'])
def excelUpload():
    """Handle excel data file uploads"""
    
    conn = dbConnect()
    
    plist = 'nothing posted'
    
    if request.method == 'POST':
        wb = load_workbook(request.files['excelUpload'])
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
    
    return render_template('excel.html',p1=plist)

@app.route("/players",methods=['POST','GET'])
def players():
    """Serve the players page"""
    
    conn = dbConnect()
    
    if request.method == 'POST':
    
        np  = request.form['p1']
        
        if np is not None:
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

    return render_template('players.html', plist=plist)
             

def serverApp(environ, start_response):
    """WSGI application to switch between different applications
    based on the request URI"""

    if environ['PATH_INFO'] == '/score':
        return score_app(environ, start_response)

    else:
        return show_404_app(environ, start_response)

       
    
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