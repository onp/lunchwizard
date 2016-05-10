


// collect data and draw graph
d3.json("scoreTableData.json", function(error, data) {
  if (error) throw error;
  
  var players = data["players"]
  var np = length(players) //number of players
  var kp = players.keys()
  var ip = {}
  for (var i = 0; i < length(kp); i++){
    ip[kp[i]] = i
  }
  
  var games = data["games"]
  var ng = length(games)   //number of games
  var kg = games.keys()
  var ig = {}
  for (var i = 0; i < length(kg); i++){
    ig[kg[i]] = i
  }
  
  Object.keys(games).map(
    function(game_id){
        games[game_id] = Date(games[game_id])
    }
  )
  
  var scores = data["scores"]
  
  //create an array of scores [game#][player#]
  scoreTable = []
  for (var i = 0; i < length(kg); i++){
    scoreTable.push([])
  }
  
  for (var i = 0; i < length(scores); i++){
    sc = scores[i]
    scoreTable[ig[sc[0]][ip[sc[1]] = sc[2]
  }
  
  console.log(scoreTable)
  
  
  
}
  
  