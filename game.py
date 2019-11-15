import db
import bot
import random
import player
import pydealer as pd
from treys import Card, Evaluator

def newGame(mailBody):    
    
    #TODO: make sure there are no duplicate email addresses
    #TODO: limit number of players to 10
    gameId = db.addGame();

    playerIndex = 0
    for newPlayer in mailBody.split("\r\n"):
        if newPlayer != '':
            playerParts = newPlayer.split(":")
            db.addPlayer(gameId, playerIndex, playerParts[0].lower(), 
                playerParts[1], playerParts[2])
            playerIndex += 1
            
    return gameId

def startGame(gameId):
    numberOfPlayers = db.numberOfPlayersInGame(gameId)
    dealer = random.randint(0, numberOfPlayers - 1)

    # for debugging, remove randomness
    if bot.DEBUG:
        dealer = 0
    
    db.updateGame(gameId, "currentPlayer = " + str(dealer) + ", dealer = " + str(dealer))
    return startHand(gameId)
    
    
def startHand(gameId):
    numberOfPlayers = db.numberOfPlayersInGame(gameId)
    _,_,_,dealer,_,_,_,_ = db.getGame(gameId)
    
    #TODO: make blinds configurable
    # TODO: make blinds increase
    smallBlind = 1
    bigBlind = 2
    
    deck = pd.Deck()
    deck.shuffle()
    # Deal cards and set playes to not be folded
    for i in range(numberOfPlayers):
        _,_,_,_,_,_,_,_,eliminated,_,_,_ = db.getPlayer(gameId, i)
        
        if eliminated == 0: # not eliminated
            hand = deck.deal(2)
            db.updatePlayer(gameId, i, "folded = 0, isChecked = 0, cards = \"" 
                            + str(hand[0]) + ":" + str(hand[1]) + "\", amountPutInPot = 0, amountPutInPotThisRound = 0")
    
    #dealer moves to left
    dealerPos, smallBlindPos, bigBlindPos, UTG = getNextStartingPlayers(gameId)
    
    # TODO: show hand number
    handLog = "<b>Current Hand</b>\r\n--------------------------------------\r\n" 
    handLog += "Dealer: " + db.getPlayer(gameId, dealerPos)[3] + "\r\n"
    
    #UpdateGame
    db.updateGame(gameId, "currentPlayer = " + str(UTG) + 
                  ", dealer = " + str(dealerPos) + 
                  ", board = '', phase = 0, pot = 0, betToMatch = " + str(bigBlind))
    
    handLog += (player.addToPot(gameId, smallBlindPos, smallBlind, "sb") + "\r\n")
    handLog += (player.addToPot(gameId, bigBlindPos, bigBlind, "bb"))

    db.updateGame(gameId, "handLog = \"" + handLog + "\"")
  
    
            
    return UTG


def isHandOver(gameId):
    _,_,currentPlayer,dealer,phase,pot,betToMatch,handLog = db.getGame(gameId)
    numberOfPlayers = db.numberOfPlayersInGame(gameId)
    
    if phase == 4:
        return True
    
    numberChecked = 0
    for i in range(numberOfPlayers):
        _,_,_,_,_,_,isAllIn,folded,eliminated,_,isChecked,_ = db.getPlayer(gameId, i)
        if not bool(folded) and not bool(eliminated):
            numberChecked += 1
            if numberChecked > 1:
                return False
    
    return True

def checkForRoundCompletion(gameId):
    _,_,currentPlayer,dealer,_,pot,betToMatch,handLog = db.getGame(gameId)
    numberOfPlayers = db.numberOfPlayersInGame(gameId)
    
    for i in range(numberOfPlayers):
        _,_,_,_,_,_,isAllIn,folded,eliminated,_,isChecked,_ = db.getPlayer(gameId, i)
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

# Converts card values used by pyDealer package to deuces card 
def pyDealerCardToDeucesCard(cardString):
    newCard = ""
    if cardString.startswith("Ace"):
        newCard += "A"
    elif cardString.startswith("King"):
        newCard += "K"
    elif cardString.startswith("Queen"):
        newCard += "Q"
    elif cardString.startswith("Jack"):
        newCard += "J"
    elif cardString.startswith("10"):
        newCard += "T"
    else: # numerical value under 10
        newCard += cardString[0]
        
    if cardString.endswith("Clubs"):
        newCard += "c"
    elif cardString.endswith("Spades"):
        newCard += "s"
    elif cardString.endswith("Hearts"):
        newCard += "h"
    elif cardString.endswith("Diamonds"):
        newCard += "d"
        
    return Card.new(newCard)

def cardToUnicode(cardString):
    newCard = ""
    if cardString.startswith("Ace"):
        newCard += "A"
    elif cardString.startswith("King"):
        newCard += "K"
    elif cardString.startswith("Queen"):
        newCard += "Q"
    elif cardString.startswith("Jack"):
        newCard += "J"
    elif cardString.startswith("10"):
        newCard += "T"
    else: # numerical value under 10
        newCard += cardString[0]
        
    if cardString.endswith("Clubs"):
        newCard += "♣"
    elif cardString.endswith("Spades"):
        newCard += "♠"
    elif cardString.endswith("Hearts"):
        newCard += "<font color='red'>♥</font>"
    elif cardString.endswith("Diamonds"):
        newCard += "<font color='red'>♦</font>"
        
    return newCard


def getWinners(gameId, players):
    evaluator = Evaluator()
    boardCards = []
    rankings = {}
    
    _,board,_,_,_,_,_,_ = db.getGame(gameId)
    for i in board.split(":"):
        boardCards.append(pyDealerCardToDeucesCard(i))
    
    for i in players:
        cards = i[3]
        rankings[i[0]] = evaluator.evaluate(boardCards, 
                [pyDealerCardToDeucesCard(cards.split(":")[0]), pyDealerCardToDeucesCard(cards.split(":")[1])])
    
    v = list(rankings.values())
    minValue = min(v)
    
    winners = []
    for i in rankings:
        if rankings[i] == minValue:
            winners.append([i, evaluator.class_to_string(evaluator.get_rank_class(minValue))])
    
    return winners

def isGameOver(gameId):
    _,_,currentPlayer,dealer,_,pot,betToMatch,handLog = db.getGame(gameId)
    numberOfPlayers = db.numberOfPlayersInGame(gameId)
    
    numbernotElim = 0
    for i in range(numberOfPlayers):
        _,_,_,_,_,_,isAllIn,folded,eliminated,_,isChecked,_ = db.getPlayer(gameId, i)
        if not bool(eliminated):
            numbernotElim += 1
            if numbernotElim > 1:
                return False
    
    return True

def showdown(gameId):
    _,_,currentPlayer,dealer,_,pot,betToMatch,handLog = db.getGame(gameId)
    numberOfPlayers = db.numberOfPlayersInGame(gameId)
    
    board = db.getGame(gameId)[1]
    string = ""
    if board != "":
        string += "\r\n\r\nThe board was : "
        for card in board.split(":"):
            string += cardToUnicode(str(card)) + ", "
        string = string[:-2] # get rid of trailing comma
    db.updateGame(gameId, "handLog = \"" + db.getGame(gameId)[7] + string + "\"")
    
    isStillIn = []
    
    for i in range(numberOfPlayers):
        _,_,_,_,stack,cards,isAllIn,folded,eliminated,amountPutInPot,isChecked,_ = db.getPlayer(gameId, i)
        if not bool(folded) and not bool(eliminated):
            isStillIn.append([i,amountPutInPot,stack, cards])
       
    thisPot = pot
    
    
    while len(isStillIn) > 1:
        minimumAIP = min(i[1] for i in isStillIn)
        thisPot = minimumAIP * len(isStillIn)
        for i in isStillIn:
            i[1] -= minimumAIP
        
        winners = getWinners(gameId, isStillIn)
        
        for i in winners:
            handLog = db.getGame(gameId)[7]
            playerTuple = db.getPlayer(gameId, i[0])
            
            logStatement = playerTuple[3] + " shows " + cardToUnicode(playerTuple[5].split(":")[0]) + ", " +  cardToUnicode(playerTuple[5].split(":")[1])
            logStatement += " (" + i[1] + ")"
            logStatement += "\r\n" + player.takeFromPot(gameId, i[0], thisPot//len(winners))
            db.updateGame(gameId, "handLog = \"" + handLog + "\r\n" + logStatement + "\"")
        
        newIsStillIn = []
        
        for i in isStillIn:
            if i[1] != 0:
                newIsStillIn.append(i)
                
        isStillIn = newIsStillIn
        pot -= thisPot
        thisPot = 0
        
        
    if len(isStillIn) == 1:
        handLog = db.getGame(gameId)[7]
        logStatement = player.takeFromPot(gameId, isStillIn[0][0], isStillIn[0][1] + (pot-isStillIn[0][1]))
        db.updateGame(gameId, "handLog = \"" + handLog + "\r\n" + logStatement + "\"")
    
    for i in range(numberOfPlayers):
        _,_,_,_,stack,cards,isAllIn,folded,eliminated,amountPutInPot,isChecked,_ = db.getPlayer(gameId, i)
        if stack <= 0:
            db.updatePlayer(gameId, i, "eliminated = 1")
        db.updatePlayer(gameId, i, "isAllIn = 0")
        
def allAreAllIn(gameId):
    _,_,currentPlayer,dealer,_,pot,betToMatch,handLog = db.getGame(gameId)
    numberOfPlayers = db.numberOfPlayersInGame(gameId)
    
    if nextPlayer(gameId) == -1:
        return True
    
    for i in range(numberOfPlayers):
        _,_,_,_,_,_,isAllIn,folded,eliminated,_,isChecked,_ = db.getPlayer(gameId, i)
        if not bool(eliminated) and not bool(folded) and not bool(isAllIn):
            return False
    
    return True
    
# Returns active player
def nextRound(gameId):
    _,board,currentPlayer,dealer,phase,pot,betToMatch,handLog = db.getGame(gameId)
    # 0 - preflop
    # 1 - postflop
    # 2 - turn
    # 3 - river

    newPhase = phase + 1
    numberOfPlayers = db.numberOfPlayersInGame(gameId)
    db.updateGame(gameId, "currentPlayer = " + str(dealer))
    
    for i in range(numberOfPlayers):
        db.updatePlayer(gameId, i, "isChecked = 0, amountPutInPotThisRound = 0")
        
    db.updateGame(gameId, "phase = " + str(newPhase))
    
    if not allAreAllIn(gameId):
        newCurrentPlayer = nextPlayer(gameId)[1]
        db.updateGame(gameId, "currentPlayer = " + str(newCurrentPlayer))
        
    else:
        newCurrentPlayer = dealer
        db.updateGame(gameId, "currentPlayer = " + str(newCurrentPlayer))
            
    deck = pd.Deck()
    deck.get_list(getAllCardsInPlay(gameId)) # remove all cards currently in play
    deck.shuffle()
    
    if newPhase == 1:
        newBoard = deck.deal(3)
        
        handLog = handLog + "\r\nFlop : " + cardToUnicode(str(newBoard[0])) + ", " \
            + cardToUnicode(str(newBoard[1])) + ", " + cardToUnicode(str(newBoard[2]))
        db.updateGame(gameId, "board = \"" + str(newBoard[0]) + ":" +
                      str(newBoard[1]) + ":" + str(newBoard[2]) + 
                      "\", betToMatch = 0, handLog = \"" + handLog + "\"")
    elif newPhase == 2 or newPhase == 3:
        newBoard = deck.deal(1)
        if newPhase == 2:
            handLog = handLog + "\r\nTurn : " + cardToUnicode(str(newBoard[0]))
        else:
            handLog = handLog + "\r\nRiver : " + cardToUnicode(str(newBoard[0]))
        db.updateGame(gameId, "board = \"" + board + ":" + str(newBoard[0]) +
                      "\", betToMatch = 0, handLog = \"" + handLog + "\"")
        
    
    return newCurrentPlayer
    
        
            


# Returns tuple of next player
def nextPlayer(gameId):
    _,_,currentPlayer,dealer,_,pot,betToMatch,handLog = db.getGame(gameId)
    numberOfPlayers = db.numberOfPlayersInGame(gameId)
    
    for i in range(numberOfPlayers-1):
        playerNumber = (i + currentPlayer + 1) % numberOfPlayers
        _,_,_,_,_,_,isAllIn,folded,eliminated,_,isChecked,_ = db.getPlayer(gameId, playerNumber)
        if not bool(folded) and not bool(eliminated) and not bool(isAllIn) and not bool(isChecked):
            return db.getPlayer(gameId, playerNumber)
        
    return -1 # Error state, should check if round is complete first
    
# Returns tuple of next dealer, sb, bb, and UTG
def getNextStartingPlayers(gameId):
    _,_,_,dealer,_,_,_,_ = db.getGame(gameId)
    
    db.updateGame(gameId, "currentPlayer = " + str(dealer))
    # Dealer moves to left
    dealerPos = nextPlayer(gameId)[1]
    db.updateGame(gameId, "currentPlayer = " + str(dealerPos))
    smallBlindPos = nextPlayer(gameId)[1]
    db.updateGame(gameId, "currentPlayer = " + str(smallBlindPos))
    bigBlindPos = nextPlayer(gameId)[1]
    db.updateGame(gameId, "currentPlayer = " + str(bigBlindPos))
    UTG = nextPlayer(gameId)[1]
    db.updateGame(gameId, "currentPlayer = " + str(UTG))
    return (dealerPos, smallBlindPos, bigBlindPos, UTG)
    
    
    