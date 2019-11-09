import yagmail
import easyimap
import db
import game
import credentials
import player

login = credentials.log
password = credentials.passw

def sendMail(receivers, title, body):
    yag = yagmail.SMTP(login)
    yag.send(
        to=receivers,
        subject=title,
        contents=body,
    )
    
def fakeSendMail(receivers, title, body):
    print(receivers + "\r\n" + title + "\r\n" + body)
    

def playerInfoLog(gameId, playerId):
    _,_,_,name,stack,cards,_,_,_,amountPutInPot,_ = db.getPlayer(gameId, playerId)
    #TODO: return board and bet to match to player
    _,board,_,_,_,pot,betToMatch,handLog = db.getGame(gameId)
    string = "\r\nIt is your turn " + name + ".\r\nYour cards are: " + cards.split(":")[0] + " and " + cards.split(":")[1]
    string += "\r\nYour stack is " + str(stack) + " chips."
    if not amountPutInPot == 0:
        string += "You have already put in " + str(amountPutInPot) + " chips into the pot."
    return string

def instructions():
    string = "\r\n\r\nReply to this mail with the body of the mail in one of the following formats:"
    string += "\r\nCall (this option is also check where applicable)"
    string += "\r\nRaise {integer indicating how many chips to raise to} (this option is also bet where applicable)" 
    string += "\r\nFold" + "\r\nAll in"
    return string
    

def readMail():
    
    imapper = easyimap.connect('imap.gmail.com', login, password)
    #for mail_id in imapper.listids(limit=100):
    mail_id = imapper.listids()[0]
    mail = imapper.mail(mail_id)
    
    # If new email
    if not db.isMailRead(mail_id):
        db.addReadMail(mail_id)
        #TODO: make the if staement encompass all of readMail()
    
    print("FROM:", mail.from_addr)
    print("TO:", mail.to)
    print("TITLE:", mail.title)
    print("BODY:", mail.body)
    
    if mail.title.upper() == "NEW":
        #make new game
        gameId = game.newGame(mail.body)
        firstPlayer = game.startGame(gameId)
        
        #Send first mail
        fakeSendMail(db.getPlayer(gameId, firstPlayer)[2], gameId, 
                     db.getGame(gameId)[7] + playerInfoLog(gameId,firstPlayer)
                     + instructions())
        
    #look for game with id in title
    elif not len(db.getGame(mail.title[4:])) == 0:
        
        gameId = mail.title[4:]
        playerEmail = mail.from_addr[mail.from_addr.find('<')+1:mail.from_addr.rfind('>')]       
        playerTuple = db.getPlayerByEmail(gameId, playerEmail)
        gameTuple = db.getGame(gameId)
        
        
        #if current player
        if playerTuple[1] == gameTuple[2]: # current player
            
            if mail.body.upper().startswith("CALL"):
                player.call(gameId, playerTuple)           
            elif mail.body.upper().startswith("RAISE"):
                pass
            elif mail.body.upper().startswith("FOLD"):
                pass
            elif mail.body.upper().startswith("ALL IN"):
                pass
            elif mail.body.upper().startswith("CHECK"):
                pass
            else:
                fakeSendMail(playerEmail, gameId, "Invalid command. " + instructions())
            
            
            print(game.getAllCardsInPlay(gameId))
            
            nextPlayerTuple = game.nextPlayer(gameId)
            if game.checkForRoundCompletion(gameId):
                # Starts next round and returns active player
                nextPlayerTuple = db.getPlayer(gameId, game.nextRound(gameId))
                
            db.updateGame(gameId, "currentPlayer = " + str(nextPlayerTuple[1]))
               
            fakeSendMail(nextPlayerTuple[2], gameId, db.getGame(gameId)[7] +
                         playerInfoLog(gameId, nextPlayerTuple[1]) + instructions())
            
        else:
            print(game.getAllCardsInPlay(gameId))
            pass # Not current player
            # TODO respond to incorrect player
            
        

def main():
    db.init()    
    readMail()
    db.closeConn()
    
    
if __name__ == '__main__':
    main()
