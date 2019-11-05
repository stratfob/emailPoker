import db

def addToPot(gameId, player, chips, action):
    _,_,_,_,_,pot = db.getGame(gameId)
    playerTuple = db.getPlayer(gameId, player)
    _,_,address,name,stack,_,_ = playerTuple
    logStatement = ""
    chipsPutIn = chips
    
    if stack < chips:
        logStatement += "Player " + name + " is all in! "
        chipsPutIn = chips
        db.updatePlayer(gameId, player, "isAllIn = 1")
    logStatement = "Player " + name + " "
    if action == "sb": # small blind
        logStatement += "posted the small blind of " + str(chipsPutIn) + " chips."
    elif action == "bb": # big blind
        logStatement += "posted the big blind of " + str(chipsPutIn) + " chips."
   
    #TODO add more actions
    
    #update player stack
    db.updatePlayer(gameId, player, "stack = " + str(stack - chipsPutIn))
    
    #update pot
    db.updateGame(gameId, "pot = " + str(pot + chipsPutIn))
    return logStatement
    
    

def fold(player):
    pass

def call(player):
    pass

def raiseTo(player, chips):
    pass