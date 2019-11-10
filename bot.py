import yagmail
import easyimap
import db
import game
import credentials
import player
import uuid

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
    _,_,_,name,stack,cards,_,_,_,amountPutInPot,_,amountPutInPotThisRound = db.getPlayer(gameId, playerId)
    _,board,_,_,_,pot,betToMatch,handLog = db.getGame(gameId)
    string = "\r\n\r\nIt is your turn " + name + ".\r\nYour cards are: " + cards.split(":")[0] + " and " + cards.split(":")[1]
    if board != "":
        string += "\r\nThe board is : "
        for card in board.split(":"):
            string += str(card) + ", "
        string = string[:-2] # get rid of trailing comma
    string += "\r\nThe pot is " + str(pot) + " chips."
    string += "\r\nYour stack is " + str(stack) + " chips."
    if not amountPutInPotThisRound == 0:
        string += "You have already put in " + str(amountPutInPotThisRound) + " chips into the pot."
    if betToMatch - amountPutInPotThisRound != 0:
        string += "\r\nTo call you'll need to put in " + str(betToMatch - amountPutInPotThisRound) + " chips."
    return string

def instructions():
    string = "\r\n\r\nReply to this mail with the body of the mail in one of the following formats:"
    string += "\r\nCall (this option is also check where applicable)"
    string += "\r\nRaise {integer indicating how many chips to raise to} (this option is also bet where applicable)" 
    string += "\r\nFold" + "\r\nAll in"
    return string
    

def readMail(mailId, fakeMail):
    
    # uncomment below three lines for real mail
   # imapper = easyimap.connect('imap.gmail.com', login, password)
   # mail_id = imapper.listids()[0]
   # mail = imapper.mail(mail_id)
    
   # This is the fake mail stuff
    mail_id = mailId
    mail = fakeMail
   
   
    # If new email
    if not db.isMailRead(mail_id):
        db.addReadMail(mail_id)
        #TODO: make the if staement encompass all of readMail()
    
    
    if mail.title.upper() == "NEW":
        #make new game
        gameId = game.newGame(mail.body)
        firstPlayer = game.startGame(gameId)
        
        #Send first mail
        fakeSendMail(db.getPlayer(gameId, firstPlayer)[2], gameId, 
                     db.getGame(gameId)[7] + playerInfoLog(gameId,firstPlayer)
                     + instructions())
        
        return gameId
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
                player.fold(gameId, playerTuple)
            elif mail.body.upper().startswith("ALL IN"):
                pass
            elif mail.body.upper().startswith("CHECK"):
                pass
            else:
                fakeSendMail(playerEmail, gameId, "Invalid command. " + instructions())
            

    
            nextPlayerTuple = game.nextPlayer(gameId)
            
            
            if game.checkForRoundCompletion(gameId):
                # Starts next round and returns active player
                nextPlayerTuple = db.getPlayer(gameId, game.nextRound(gameId))
                
            if game.isHandOver(gameId):
                game.showdown(gameId)
                
                # Send mail to all players
                for i in range(db.numberOfPlayersInGame(gameId)):
                    fakeSendMail(db.getPlayer(gameId, i)[2], gameId, 
                                 db.getGame(gameId)[7])
                
                nextPlayerTuple = db.getPlayer(gameId, game.startHand(gameId))
                
            db.updateGame(gameId, "currentPlayer = " + str(nextPlayerTuple[1]))
             
            
            print("------------------------------------------------------------")
            fakeSendMail(nextPlayerTuple[2], gameId, db.getGame(gameId)[7] +
                         playerInfoLog(gameId, nextPlayerTuple[1]) + instructions())
            
        else:
            pass # Not current player
            # TODO respond to incorrect player
            
class Mail:
    def __init__(self, title, body, from_addr):
        self.title = title
        self.body = body 
        self.from_addr = from_addr #100
       

def main():
    db.init()   
    
    gameId = readMail("test1", Mail("New", "ben.e.stratford@gmail.com:Ben1:100\r\nbenstratford586@gmail.com:Ben2:100", "<ben.e.stratford@gmail.com>"))
    firstPlayer = db.getGame(gameId)[2]
    
    for i in range(4):
        if firstPlayer == 0:
            ID = str(uuid.uuid4()).replace('-','')
            readMail(ID, Mail("Re: " + gameId, "Call", "<ben.e.stratford@gmail.com>"))
            readMail(ID, Mail("Re: " + gameId, "Call", "<benstratford586@gmail.com>"))
        else:
            ID = str(uuid.uuid4()).replace('-','')
            readMail(ID, Mail("Re: " + gameId, "Call", "<benstratford586@gmail.com>"))
            readMail(ID, Mail("Re: " + gameId, "Call", "<ben.e.stratford@gmail.com>"))
           

    db.closeConn()
    
    
if __name__ == '__main__':
    main()
