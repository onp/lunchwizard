


// collect data and draw graph
d3.json("scoreTableData.json", function(error, data) {
    if (error) throw error;
  
    var players = data["players"]
    //map each playerID to an ordered value
    var playerMap = {}
    players.map(
        function(v,i){playerMap[v] = i}
    )
  
    var games = data["games"]
    var gameMap = {}
    games.map(
        function(v,i){
            gameMap[v] = i;
            v[1] = new Date(v[1]);
        }
    )

    console.log(games)
    console.log(players)
    
    var scores = data["scores"]
  
  
    //create an array of scores [game#][player#]
    scoreTable = []
    for (var i = 0; i < games.length; i++){
        scoreTable.push([])
    }
  
    for (var i = 0; i < scores.length; i++){
        var sc = scores[i]
        console.log(sc)
        scoreTable[gameMap[sc[0]]][playerMap[sc[1]]] = sc[2]
    }
  
    console.log(scoreTable)
  
  
  
})
  
  