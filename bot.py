import yagmail
import easyimap
import db
import game
import credentials

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
    print(receivers, "\r\n", title, "\r\n", body)
    

def playerInfoLog(gameId, playerId):
    _,_,_,_,stack,cards,_,_,_ = db.getPlayer(gameId, playerId)
    string = "\r\nIt is your turn.\r\nYour cards are: " + cards.split(":")[0] + " and " + cards.split(":")[1]
    string += "\r\nYour stack is " + str(stack) + " chips."
    return string

def instructions():
    string = "\r\n\r\nReply to this mail with the body of the mail in one of the following formats:"
    string += "\r\nCall" + "\r\nRaise {integer indicating how many chips to raise to}"
    string += "\r\nFold" + "\r\nAll in" + "\r\nCheck"
    return string
    

def readMail():
    
    imapper = easyimap.connect('imap.gmail.com', login, password)
    #for mail_id in imapper.listids(limit=100):
    mail_id = imapper.listids()[0]
    mail = imapper.mail(mail_id)
    
    # If new email
    #if not db.isMailRead(mail_id):
        
    db.addReadMail(mail_id)
    
    #print("FROM:", mail.from_addr)
    #print("TO:", mail.to)
    #print("TITLE:", mail.title)
    #print("BODY:", mail.body)
    
    if mail.title.upper() == "NEW":
        #make new game
        gameId = game.newGame(mail.body)
        firstPlayer = game.startGame(gameId)
        fakeSendMail(db.getPlayer(gameId, firstPlayer)[2], gameId, 
                     db.getGame(gameId)[7] + playerInfoLog(gameId,firstPlayer)
                     + instructions())
    else:
        #look for game with id in title
        pass
    

def main():
    db.init()    
    readMail()
    db.closeConn()
    
    
if __name__ == '__main__':
    main()
