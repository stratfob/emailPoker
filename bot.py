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
    

def readMail():
    
    imapper = easyimap.connect('imap.gmail.com', login, password)
    #for mail_id in imapper.listids(limit=100):
    mail_id = imapper.listids()[0]
    mail = imapper.mail(mail_id)
    
    # If new email
    #if not db.isMailRead(mail_id):
        
    db.addReadMail(mail_id)
    
    print("FROM:", mail.from_addr)
    print("TO:", mail.to)
    print("TITLE:", mail.title)
    print("BODY:", mail.body)
    
    if mail.title.upper() == "NEW":
        #make new game
        gameId = game.newGame(mail)
        game.startGame(gameId)
    else:
        #look for game with id in title
        pass
    
    
db.init()    
readMail()
db.closeConn()
