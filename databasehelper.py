import re
import scrapedata
import mysql.connector
import sys
import warnings

defaultUsername = "DentistRhapsody"
dbName = "mal"
socket = None
c = None
warnings.filterwarnings('ignore')

# Class to be called to construct a database.
class buildDB:
  userShowList = []
  showDetails = []  # doesn't exist :)
  c = None
  socket = None

  def __init__(self, cursor, socket, userShows=None, shows=None):
    self.c = cursor
    self.socket = socket
    self.userShowList = userShows
    self.showDetails = shows  # This currently does not exist
    print(cursor)
    print(socket)
    
  def go(self):
    self.resetDatabase()
    self.createTables()
    self.populateUsers()
    self.populateShows()
    self.populateShowList()
    
  def createTables(self):
    self.c.execute("create table if not exists users (uid char(16) not null, primary key (uid))")
    self.c.execute("create table if not exists shows (sid smallint(5) not null, name blob, primary key (sid))")
    self.c.execute("create table if not exists showlist (sid smallint(5) not null, uid char(16) not null, score tinyint, date date, eps smallint(5), constraint slid primary key (sid, uid), foreign key (uid) references users(uid), foreign key (sid) references shows(sid))")
    self.socket.commit()
      
  def resetDatabase(self, db=dbName):
    shouldRestart = input("Would you like to drop the content of the '{}' database? y/n >> ".format(dbName)).lower()
    while (shouldRestart != "y" and shouldRestart != "n"):
      shouldRestart = input("/tInvalid input. Please try again. >> ")
    if (shouldRestart == "y"):
      self.c.execute("set FOREIGN_KEY_CHECKS = 0")
      self.c.execute("drop database {}".format(dbName))
      self.c.execute("create database {}".format(dbName))
      self.c.execute("use {}".format(dbName))
    self.socket.commit()
      
  def populateUsers(self):
    # Temp code since it's one user at a time right now
    self.c.execute("insert ignore  into users (uid) values (%s)", (self.userShowList[0][0],))
    self.socket.commit()
    
  def populateShows(self):
    vals = list(zip(*self.userShowList))
    vals = list(zip(vals[1], vals[5]))
    self.c.executemany("insert into shows (sid, name) values (%s, %s) on duplicate key update name=values(name)", list(vals))
    self.socket.commit()
    
  def populateShowList(self):
    vals = list(zip(*self.userShowList))
    vals = list(zip(vals[0], vals[1], vals[2], vals[3], vals[4]))
    self.c.executemany("insert into showlist (uid, sid, score, eps, date) values (%s, %s, %s, %s, %s) on duplicate key update score=values(score), eps=values(score), date=values(date)", vals)
    self.socket.commit()
  
# --------------------------------------------

def showListReader(show):
  def getSID(userShow):
    # rx = re.compile(r"\/([0-9]+)\\")
    # return rx.search(show['anime_url']).group()
    return int(userShow['anime_id'])
  
  def getScore(userShow):
    return int(userShow['score'])
    
  def getEpisodes(userShow):
    return int(userShow['num_watched_episodes'])
  
  def getDate(userShow):
    rx = re.compile(r"[0-9]{1,4}")
    data = userShow['finish_date_string']
    if data == None:
      return None
    d = rx.findall(data)
    return d[2] + "-" + d[0] + "-" + d[1]
    
  def getName(userShow):
    return userShow['anime_title']
    
  return (getSID(show), getScore(show), getEpisodes(show), getDate(show), getName(show))

def connect():
  try:
    socket = mysql.connector.connect(user='pythonscript', password='pythonDeshita', host='192.168.1.22', database=dbName)
  except mysql.connector.Error as err:
    print("Connection issue! " + err)
    return (None, None)
  else:
    c = socket.cursor()
    try:
      c.execute("use {}".format(dbName))
    except:
      print("Unable to use database {}!".format(dbName))
      return (socket, None)
  return (socket, c)
      
def singleton():
  (s, co) = connect()
  socket = s
  c = co
  if (socket == None or c == None):
    print("Exiting...")
    sys.exit()
  showListData = scrapedata.efu()
  sld = []
  for s in showListData:
    sld.append((("", defaultUsername) + showListReader(s))[1:])
  print("List of shows acquired, preparing to create database...")
  db = buildDB(c, socket, userShows=sld)
  print("Database creation finished. Beginning full process...")
  db.go()
  print("Full process finished.")
  c.close()
  socket.close()

# --------------------------------------------

if __name__ == "__main__":
  singleton()
  
