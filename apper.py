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
    """Homepage."""
    return render_template('index.html')

@app.route("/data.json")
def data():
    """Score data for 2015-8-1 to 2015-11-4."""
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
    
    # adding players to the list
    if request.method == 'POST': 
    
        np  = request.form['p1']
        
        if np is not None:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO players (name,join_date) VALUES (%s,%s);",
                            (np,datetime.date.today()))

    # returning the page with the list of players
    h = open ("templates/players.html")
    content_template = Template(h.read())
    h.close()
    
    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT name FROM players;")
            plist = [p[0] for p in cur.fetchall()] #players are returned as tuples

    return render_template('players.html', plist=plist)
    
@app.route("/scoreEntry",methods=['POST','GET'])
def scoreEntry():
    """Get scores for a new game."""
    
    data = [
        {"players":[{"name":"Sean"},{"name":"Calvin"},{"name":"Omer"},{"name":"Farah"},{"name":"Jamie"]},
        {"players":[{"name":"Oskar"},{"name":"Jeff"},{"name":"Spencer"},{"name":"Burkeley"},{"name":"Dave"}]}
    ]

    return render_template("scoreEntry.html", leagues=data)

    
@app.errorhandler(404)
def page_not_found(error):
    """Serve 404"""
    return render_template('404.html'), 404
    
    