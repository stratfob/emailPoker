import db
import random
import player

def newGame(mail):    
    gameId = db.addGame();

    playerIndex = 0
    for newPlayer in mail.body.split("\r\n"):
        if newPlayer != '':
            playerParts = newPlayer.split(":")
            print(db.addPlayer(gameId, playerIndex, playerParts[0], 
                         playerParts[1], playerParts[2]))
            playerIndex += 1
            
    return gameId

def startGame(gameId):
    numberOfPlayers = db.numberOfPlayersInGame(gameId)
    dealer = random.randint(0, numberOfPlayers - 1)
    
    db.updateGame(gameId, "currentPlayer = " + str(dealer) + ", dealer = " + str(dealer))
    startHand(gameId)
    
    
def startHand(gameId):
    numberOfPlayers = db.numberOfPlayersInGame(gameId)
    _,_,_,dealer,_,_ = db.getGame(gameId)
    
    #dealer moves to left
    dealerPos = (dealer + 1) % numberOfPlayers
    smallBlind = (dealerPos + 1) % numberOfPlayers
    bigBlind = (dealerPos + 2) % numberOfPlayers
    UTG = (dealerPos + 3) % numberOfPlayers
    
    #Todo: make blinds configurable
    print(player.addToPot(gameId, smallBlind, 1, "sb"))
    print(player.addToPot(gameId, bigBlind, 2, "bb"))
    
    #UpdateGame
    db.updateGame(gameId, "currentPlayer = " + str(UTG) + ", dealer = " + str(dealerPos))