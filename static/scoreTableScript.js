


// collect data and draw graph
d3.json("scoreTableData.json", function(error, data) {
    if (error) throw error;
  
    var players = data["players"]
    //map each playerID to an ordered value
    var playerMap = {}
    players.map(
        function(v,i){
            playerMap[v[0]] = i
        }
    )
  
    var games = data["games"]
    var gameMap = {}
    games.map(
        function(v,i){
            gameMap[v[0]] = i;
            v[1] = new Date(v[1]);
        }
    )
    
    var scores = data["scores"]
  
    //create an array of scores [game#][player#]
    scoreArray = []
    for (var i = 0; i < games.length; i++){
        scoreArray.push([])
    }
  
    for (var i = 0; i < scores.length; i++){
        var sc = scores[i]
        scoreArray[gameMap[sc[0]]][playerMap[sc[1]]] = sc[2]
    }
    

    var scoreTable = document.createElement('table');
    var row = document.createElement('tr');
    row.appendChild(document.createElement('th'));
    for (var i = 0; i < players.length; i++){
        var cell = document.createElement('th');
        cell.textContent = players[i][1]
        cell.classList.add("playerName")
        row.appendChild(cell)
    }
    scoreTable.appendChild(row);
    for (var i = 0; i < games.length; i++) {
        var row = document.createElement('tr');
        var cell = document.createElement('th');
        cell.textContent = games[i][1].toDateString()
        cell.classList.add("gameDate")
        row.appendChild(cell);
        for (var j = 0; j < players.length; j++) {
            var cell = document.createElement('td');
            cell.textContent = scoreArray[i][j];
            row.appendChild(cell);
        }
        scoreTable.appendChild(row);
    }

    document.getElementById("content").appendChild(scoreTable)

  
  
  
})
  
  