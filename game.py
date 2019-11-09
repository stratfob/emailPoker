import db
import random
import player
import pydealer as pd

def newGame(mailBody):    
    
    #TODO make sure there are no duplicate email addresses
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
    
    
    #TODO: Account for eliminations (use getNextStartingPlayers)
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
    _,_,currentPlayer,dealer,_,pot,betToMatch,handLog = db.getGame(gameId)
    numberOfPlayers = db.numberOfPlayersInGame(gameId)
    
    for i in range(numberOfPlayers):
        _,_,_,_,_,_,isAllIn,folded,eliminated,_,isChecked = db.getPlayer(gameId, i)
        if not bool(folded) and not bool(eliminated) and not bool(isAllIn) and not bool(isChecked):
            return False
    
    return True


def getAllCardsInPlay(gameId):
    numberOfPlayers = db.numberOfPlayersInGame(gameId)
    allCards = []
    board = db.getGame(gameId)[1]
    if not board == "":
        allCards = board.split(":")
    for i in range(numberOfPlayers):
        allCards += db.getPlayer(gameId, i)[5].split(":")
    return allCards
    
def showdown(gameId):
    pass

# Returns active player
def nextRound(gameId):
    _,board,currentPlayer,dealer,phase,pot,betToMatch,handLog = db.getGame(gameId)
    # 0 - preflop
    # 1 - postflop
    # 2 - turn
    # 3 - river
    if phase == 3:
        showdown(gameId)
        #todo: check for game end
        return startHand(gameId)
    else:
        newPhase = phase + 1
        newCurrentPlayer = dealer + 1
        numberOfPlayers = db.numberOfPlayersInGame(gameId)
        db.updateGame(gameId, "phase = " + str(newPhase) + ", currentPlayer = " + str(newCurrentPlayer))
        for i in range(numberOfPlayers):
            db.updatePlayer(gameId, i, "isChecked = 0, amountPutInPot = 0")
            
        deck = pd.Deck()
        deck.get_list(getAllCardsInPlay(gameId)) # remove all cards currently in play
        
        if newPhase == 1:
            newBoard = deck.deal(3)
            db.updateGame(gameId, "board = \"" + str(newBoard[0]) + ":" +
                          str(newBoard[1]) + ":" + str(newBoard[2]) + "\", betToMatch = 0")
        elif newPhase == 2 or newPhase == 3:
            newBoard = deck.deal(1)
            db.updateGame(gameId, "board = \"" + board + ":" + str(newBoard[0]) + ", betToMatch = 0")
            
        return newCurrentPlayer
            


# Returns tuple of next player
def nextPlayer(gameId):
    _,_,currentPlayer,dealer,_,pot,betToMatch,handLog = db.getGame(gameId)
    numberOfPlayers = db.numberOfPlayersInGame(gameId)
    
    for i in range(numberOfPlayers-1):
        playerNumber = (i + currentPlayer + 1) % numberOfPlayers
        _,_,_,_,_,_,isAllIn,folded,eliminated,_,isChecked = db.getPlayer(gameId, playerNumber)
        if not bool(folded) and not bool(eliminated) and not bool(isAllIn) and not bool(isChecked):
            return db.getPlayer(gameId, playerNumber)
        
    return -1 # Error state, should check if round is complete first
    
# Returns tuple of next dealer, sb, bb, and UTG
def getNextStartingPlayers(gameId):
    pass
    
    
    
    