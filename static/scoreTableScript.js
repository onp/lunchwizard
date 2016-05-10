


// collect data and draw graph
d3.json("scoreTableData.json", function(error, data) {
  if (error) throw error;
  
  var players = data["players"]
  var np = players.length //number of players
  var kp = d3.keys(players)
  var ip = {}
  for (var i = 0; i < np; i++){
    ip[kp[i]] = i
  }
  
  var games = data["games"]
  var ng = games.length   //number of games
  var kg = d3.keys(games)
  var ig = {}
  for (var i = 0; i < ng; i++){
    ig[kg[i]] = i
  }
  
  d3.keys(games).map(
    function(game_id){
        games[game_id] = Date(games[game_id])
    }
  )
  
  var scores = data["scores"]
  
  //create an array of scores [game#][player#]
  scoreTable = []
  for (var i = 0; i < ng; i++){
    scoreTable.push([])
  }
  
  for (var i = 0; i < scores.length; i++){
    sc = scores[i]
    scoreTable[ig[sc[0]]][ip[sc[1]]] = sc[2]
  }
  
  console.log(scoreTable)
  
  
  
})
  
  