import db

def addToPot(gameId, player, chips, action):
    _,_,_,_,_,pot,_,_ = db.getGame(gameId)
    playerTuple = db.getPlayer(gameId, player)
    _,_,address,name,stack,_,_,_,_,amountPutInPot,_ = playerTuple
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
    elif action == "call":
        logStatement += "calls " + str(chipsPutIn) + " chips."
    elif action == "raise":
        logStatement += "raises to " + str(chipsPutIn) + " chips."
    
    #update player stack
    db.updatePlayer(gameId, player, "stack = " + str(stack - chipsPutIn) 
        + ", amountPutInPot = " + str(amountPutInPot + chipsPutIn))
    
    #update pot
    db.updateGame(gameId, "pot = " + str(pot + chipsPutIn))
    return logStatement
    
    

def fold(player):
    pass

def call(gameId, playerTuple):
    _,_,_,_,_,pot,betToMatch,handLog = db.getGame(gameId)
    _,playerId,address,name,stack,_,_,_,_,amountPutInPot,_ = playerTuple
    
    chipsToPutIn = betToMatch - amountPutInPot
    
    logStatement = handLog + addToPot(gameId, playerId, chipsToPutIn, "call")
    
    #update player stack
    db.updatePlayer(gameId, playerId, "isChecked = 1")
    db.updateGame(gameId, "handLog = \"\r\n" + logStatement + "\"")
    

def raiseTo(player, chips):
    pass