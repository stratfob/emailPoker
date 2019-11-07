import db
import random
import player
import pydealer as pd

def newGame(mailBody):    
    gameId = db.addGame();

    playerIndex = 0
    for newPlayer in mailBody.split("\r\n"):
        if newPlayer != '':
            playerParts = newPlayer.split(":")
            db.addPlayer(gameId, playerIndex, playerParts[0], 
                         playerParts[1], playerParts[2])
            playerIndex += 1
            
    return gameId

def startGame(gameId):
    numberOfPlayers = db.numberOfPlayersInGame(gameId)
    dealer = random.randint(0, numberOfPlayers - 1)
    
    db.updateGame(gameId, "currentPlayer = " + str(dealer) + ", dealer = " + str(dealer))
    return startHand(gameId)
    
    
def startHand(gameId):
    numberOfPlayers = db.numberOfPlayersInGame(gameId)
    _,_,_,dealer,_,_,_,_ = db.getGame(gameId)
    
    smallBlind = 1
    bigBlind = 2
    
    
    #TODO: Account for eliminations
    #dealer moves to left
    dealerPos = (dealer + 1) % numberOfPlayers
    smallBlindPos = (dealerPos + 1) % numberOfPlayers
    bigBlindPos = (dealerPos + 2) % numberOfPlayers
    UTG = (dealerPos + 3) % numberOfPlayers
    
    for i in range(numberOfPlayers):
        db.updatePlayer(gameId, i, "amountPutInPot = 0")
    
    
    handLog = "New Hand\r\n--------------------------------------\r\n" 
    handLog += "Dealer: " + db.getPlayer(gameId, dealerPos)[3] + "\r\n"
    
    #UpdateGame
    db.updateGame(gameId, "currentPlayer = " + str(UTG) + 
                  ", dealer = " + str(dealerPos) + 
                  ", board = '', phase = 0, pot = 0, betToMatch = " + str(bigBlind))
    
    handLog += (player.addToPot(gameId, smallBlindPos, smallBlind, "sb") + "\r\n")
    handLog += (player.addToPot(gameId, bigBlindPos, bigBlind, "bb") + "\r\n")

    db.updateGame(gameId, "handLog = \"" + handLog + "\"")
  
    deck = pd.Deck()
    deck.shuffle()
    # Deal cards and set playes to not be folded
    for i in range(numberOfPlayers):
        _,_,_,_,_,_,_,_,eliminated,_,_ = db.getPlayer(gameId, i)
        
        if eliminated == 0: # not eliminated
            hand = deck.deal(2)
            db.updatePlayer(gameId, i, "folded = 0, isChecked = 0, cards = \"" 
                            + str(hand[0]) + ":" + str(hand[1]) + "\"")
            
    return UTG

def checkForRoundCompletion(gameId):
    pass
    
def nextPlayer(gameId):
    pass
    
    