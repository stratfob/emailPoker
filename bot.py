import yagmail
import easyimap
import db
import game
import credentials
import player
import uuid

# Change below for console mails (debug) 
DEBUG = True

login = credentials.log
password = credentials.passw

def sendMail(receivers, title, body):
    if DEBUG:
        fakeSendMail(receivers, title, body)
    else:
        yag = yagmail.SMTP(login)
        yag.send(
            to=receivers,
            subject=title,
            contents=body,
        )
    
def fakeSendMail(receivers, title, body):
    print(receivers + "\r\n" + title + "\r\n" + body)
    

def playerInfoLog(gameId, playerId):
    _,board,_,_,_,pot,betToMatch,handLog = db.getGame(gameId)
    string = "\r\n\r\nPlayers:"
    for i in range(db.numberOfPlayersInGame(gameId)):
        _,_,address,name,stack,_,isAllIn,folded,eliminated,_,isChecked,_ = db.getPlayer(gameId, i)
        string += "\r\n" + name + " - " + str(stack) + " chips"
        
    _,_,_,name,stack,cards,_,_,_,amountPutInPot,_,amountPutInPotThisRound = db.getPlayer(gameId, playerId)
    string += "\r\n\r\nIt is your turn " + name + ".\r\nYour cards are: " + game.cardToUnicode(cards.split(":")[0]) + " and " + game.cardToUnicode(cards.split(":")[1])
    if board != "":
        string += "\r\nThe board is : "
        for card in board.split(":"):
            string += game.cardToUnicode(str(card)) + ", "
        string = string[:-2] # get rid of trailing comma
    string += "\r\nThe pot is " + str(pot) + " chips."
    string += "\r\nYour stack is " + str(stack) + " chips."
    if not amountPutInPotThisRound == 0:
        string += "You have already put in " + str(amountPutInPotThisRound) + " chips into the pot."
    if betToMatch - amountPutInPotThisRound != 0:
        string += "\r\nTo call you'll need to put in " + str(betToMatch - amountPutInPotThisRound) + " chips."
    return string

def instructions():
    string = "\r\n\r\nReply to this mail with the body of the mail as one of the following responses:"
    string += "\r\nCall (this option is also check where applicable)"
    string += "\r\nRaise {integer indicating how many chips to raise to} (this option is also bet where applicable)" 
    string += "\r\nFold" + "\r\nAll in"
    return string
    
def readMail(imapper, mailId = None, fakeMail = None):   
    
    if DEBUG:
        mail_id = mailId
        mail = fakeMail
    else:
        mail_id = imapper.listids()[0]
        mail = imapper.mail(mail_id)
    
    # If new email
    if not db.isMailRead(mail_id):
        db.addReadMail(mail_id)
    
        if mail.title.upper() == "NEW":
            #make new game
            gameId = game.newGame(mail.body)
            firstPlayer = game.startGame(gameId)
            
            print("First player = " + str(firstPlayer))
            
            #Send first mail
            sendMail(db.getPlayer(gameId, firstPlayer)[2], gameId, 
                         db.getGame(gameId)[7] + playerInfoLog(gameId,firstPlayer)
                         + instructions())
            
            return gameId
        #look for game with id in title
        elif not len(db.getGame(mail.title[4:])) == 0:
            
            gameId = mail.title[4:]
            playerEmail = mail.from_addr[mail.from_addr.find('<')+1:mail.from_addr.rfind('>')].lower()       
            playerTuple = db.getPlayerByEmail(gameId, playerEmail)
            gameTuple = db.getGame(gameId)
            
            successfulRaise = True
            
            #if current player
            if playerTuple[1] == gameTuple[2]: # current player
                
                if mail.body.upper().startswith("CALL"):
                    player.call(gameId, playerTuple)           
                elif mail.body.upper().startswith("RAISE"):
                    if len(mail.body.split(" "))<2:
                        successfulRaise = False
                    else:
                        if mail.body.split(" ")[1].strip().find('\r') == -1:
                            chipsToRaiseTo = int(mail.body.split(" ")[1].strip())
                        else: 
                            chipsToRaiseTo = int(mail.body.split(" ")[1].strip()[:mail.body.split(" ")[1].strip().find('\r')])
                        successfulRaise = player.raiseTo(gameId, playerTuple, chipsToRaiseTo)
                                                    
                elif mail.body.upper().startswith("FOLD"):
                    player.fold(gameId, playerTuple)
                elif mail.body.upper().startswith("ALL IN"):
                    successfulRaise = player.allIn(gameId, playerTuple)
                else:
                    successfulRaise = False
                
                if successfulRaise:
        
                    if not game.allAreAllIn(gameId):
                        nextPlayerTuple = game.nextPlayer(gameId)
                    
                    if game.checkForRoundCompletion(gameId):
                        # Starts next round and returns active player
                        nextPlayerTuple = db.getPlayer(gameId, game.nextRound(gameId))
                        
                    if game.isHandOver(gameId):
                        game.showdown(gameId)
                        
                        # Send mail to all players
                        for i in range(db.numberOfPlayersInGame(gameId)):
                            sendMail(db.getPlayer(gameId, i)[2], gameId, 
                                         db.getGame(gameId)[7])
                        
                        if not game.isGameOver(gameId):   
                            nextPlayerTuple = db.getPlayer(gameId, game.startHand(gameId))
                        
                    if not game.isGameOver(gameId):
                        if not game.allAreAllIn(gameId):
                            db.updateGame(gameId, "currentPlayer = " + str(nextPlayerTuple[1]))
                            sendMail(nextPlayerTuple[2], gameId, db.getGame(gameId)[7] +
                                         playerInfoLog(gameId, nextPlayerTuple[1]) + instructions())
                        else:
                            _,_,currentPlayer,dealer,_,pot,betToMatch,handLog = db.getGame(gameId)
                            numberOfPlayers = db.numberOfPlayersInGame(gameId)
                            for i in range(numberOfPlayers):
                                if not bool(db.getPlayer(gameId, i)[8]): # not eliminated
                                    sendMail(db.getPlayer(gameId, i)[2], gameId, db.getGame(gameId)[7] +
                                         "\r\nDealer, please call to continue.")
                            
                    else:
                        _,_,currentPlayer,dealer,_,pot,betToMatch,handLog = db.getGame(gameId)
                        numberOfPlayers = db.numberOfPlayersInGame(gameId)
                        
                        for i in range(numberOfPlayers):
                            _,_,_,_,_,_,isAllIn,folded,eliminated,_,isChecked,_ = db.getPlayer(gameId, i)
                            if not bool(eliminated):
                                winner = i
                                break
                        
                        for i in range(numberOfPlayers):
                            sendMail(db.getPlayer(gameId, i)[2], gameId, 
                                         "The winner was " + db.getPlayer(gameId, winner)[3]
                                         + "! Thanks for playing :)")
                            
                        db.deleteGame(gameId)
                    
                # unsuccessful raise    
                else:
                    sendMail(playerEmail, gameId, "Invalid input. Please try again.\r\n"+ instructions())
                


class Mail:
    def __init__(self, title, body, from_addr):
        self.title = title
        self.body = body 
        self.from_addr = from_addr
       

def main():
    db.init()   
    imapper = easyimap.connect('imap.gmail.com', login, password)
    
    if DEBUG:
        gameId = readMail(imapper, str(uuid.uuid4()).replace('-',''), Mail("New", "ben1mail:Ben1:100\r\nben2mail:Ben2:100\r\nben3mail:Ben3:100\r\nben4mail:Ben4:100", "<ben.e.stratford@gmail.com>"))
        readMail(imapper, str(uuid.uuid4()).replace('-',''), Mail("Re: " + gameId, "All in", "<ben1mail>"))
        readMail(imapper, str(uuid.uuid4()).replace('-',''), Mail("Re: " + gameId, "Fold", "<ben2mail>"))
        readMail(imapper, str(uuid.uuid4()).replace('-',''), Mail("Re: " + gameId, "Fold", "<ben3mail>"))
        readMail(imapper, str(uuid.uuid4()).replace('-',''), Mail("Re: " + gameId, "Fold", "<ben4mail>"))
        readMail(imapper, str(uuid.uuid4()).replace('-',''), Mail("Re: " + gameId, "Call", "<ben1mail>"))
        readMail(imapper, str(uuid.uuid4()).replace('-',''), Mail("Re: " + gameId, "Call", "<ben2mail>"))
        readMail(imapper, str(uuid.uuid4()).replace('-',''), Mail("Re: " + gameId, "Call", "<ben3mail>"))
        readMail(imapper, str(uuid.uuid4()).replace('-',''), Mail("Re: " + gameId, "Call", "<ben4mail>"))
 

    else:
        while True:
            try:
                readMail(imapper)
            except Exception as e:
                #TODO: add email details
                sendMail(credentials.ownerEmail, "Crash", str(e))

    
    db.closeConn()
    
    
if __name__ == '__main__':
    main()
