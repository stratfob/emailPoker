import sqlite3
import uuid

conn = sqlite3.connect('poker.db')
c = conn.cursor()


# Tables
def createGameTable():
    try:
        c.execute('''CREATE TABLE game
              (ID integer, board text, currentPlayer integer, dealer integer,
              phase integer, pot integer, betToMatch integer, handLog text,
              handNo integer, smallBlind integer, blindIncrement integer)''')
        conn.commit()
        return "Created game table successfully"
    except:
        return "Table Exists"
    
def createPlayerTable():
    try:
        c.execute('''CREATE TABLE player
              (gameID integer, ID integer, address text, name text, 
              stack integer, cards text, isAllIn integer, folded integer, 
              eliminated integer, amountPutInPot integer, isChecked integer, amountPutInPotThisRound integer)''')
        conn.commit()
        return "Created player table successfully"
    except:
        return "Table Exists"
    
def createReadMailTable():
    try:
        c.execute('''CREATE TABLE readMail
              (mailId text)''')
        conn.commit()
        return "Created read mail table successfully"
    except:
        return "Table Exists"
    
# Inserts 
def addPlayer(gameId, playerId, address, name, stack):
    try:
        c.execute("""INSERT INTO player(gameId, ID, address, name, 
                                        stack, cards, isAllIn, folded,
                                        eliminated, amountPutInPot, isChecked, amountPutInPotThisRound)
              VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""", 
              (gameId, playerId, address, name, stack, "", 0, 0, 0, 0, 0, 0))
        conn.commit()
        return "Player " + name + " added successfully"
    except Exception as e:
        return e
    
def addGame():
    unique = False
    while not unique:
        ID = str(uuid.uuid4()).replace('-','')
        c.execute("SELECT * FROM game WHERE ID = ?", (ID,))
        rows = c.fetchall()
        if len(rows)==0:
            c.execute("""INSERT INTO game(ID, board, currentPlayer, 
                                          dealer, phase, pot, betToMatch, 
                                          handLog, handNo, smallBlind, blindIncrement)
                  VALUES(?,?,?,?,?,?,?,?,?,?,?)""", (ID, "", 0, 0, 0, 0, 0,"",0, 0, 0))
            conn.commit()
            unique = True
            return ID
        
def addReadMail(mailId):
    try:
        c.execute("""INSERT INTO readMail(mailId)
            VALUES(?)""", (mailId,))
        conn.commit()
        return "Mail " + mailId + " added successfully"
    except Exception as e:
        return e
        
# Selects     
def isMailRead(mailId):
    c.execute("SELECT * FROM readMail WHERE mailId = ?", (mailId,))
    rows = c.fetchall()
    return not len(rows)==0

def numberOfPlayersInGame(gameId):
    c.execute("SELECT count(*) FROM player WHERE gameID = ?", (gameId,))
    rows = c.fetchall()
    return int(rows[0][0])

def getGame(gameId):
    try:
        c.execute("SELECT * FROM game WHERE ID = ?", (gameId,))
        return c.fetchall()[0]
    except:
        return []
    

def getPlayer(gameID, playerId):
    c.execute("SELECT * FROM player WHERE ID = ? AND gameID = ?", (playerId, gameID))
    return c.fetchall()[0]

def getPlayerByEmail(gameId, playerEmail):
    c.execute("SELECT * FROM player WHERE address = ? AND gameID = ?", (playerEmail, gameId))
    return c.fetchall()[0]

#Updates
def updateGame(ID, updatesString):
    try:
        c.execute("UPDATE game SET " + updatesString + " WHERE ID = ?", (ID,))
        conn.commit()
    except Exception as e:
        return e
    
# Deletes
def deleteGame(gameId):
    try:
        c.execute("DELETE FROM game WHERE ID = ?", (gameId,))
        c.execute("DELETE FROM player WHERE gameID = ?", (gameId,))
        conn.commit()
    except Exception as e:
        return e

def updatePlayer(gameId, ID, updatesString):
    try:
        c.execute("UPDATE player SET " + updatesString + " WHERE ID = ? and gameID = ?", (ID, gameId))
        conn.commit()
        return "Player " + str(ID) + " in game " + str(gameId) + " updated successfully."
    except Exception as e:
        return e

def init():
    createGameTable()
    createPlayerTable()
    createReadMailTable()
    
def closeConn():    
    conn.close()
    
