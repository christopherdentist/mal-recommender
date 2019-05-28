import re
import scrapedata
import mysql.connector
import sys
import warnings
import atexit

defaultUsername = "DentistRhapsody"
dbName = "mal"
piAddress = '192.168.1.22'
socket = None
c = None

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
    
  def go(self, shouldReset=False):
    if shouldReset:
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
    self.c.execute("insert into users (uid) values (%s) on duplicate key update uid=values(uid)", (self.userShowList[0][0],))
    self.socket.commit()
    
  def populateShows(self):
    vals = list(zip(*self.userShowList))
    vals = list(zip(vals[1], vals[5]))
    self.c.executemany("insert into shows (sid, name) values (%s, %s) on duplicate key update name=values(name)", list(vals))
    self.socket.commit()
    
  def populateShowList(self):
    vals = list(zip(*self.userShowList))
    vals = list(zip(vals[0], vals[1], vals[2], vals[3], vals[4]))
    self.c.executemany("insert into showlist (uid, sid, score, eps, date) values (%s, %s, %s, %s, %s) on duplicate key update score=values(score), eps=values(eps), date=values(date)", vals)
    self.socket.commit()
  
# --------------------------------------------
# Functions designed for my sanity within this class

def _showListReader(show):
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

def _connect():
  try:
    socket = mysql.connector.connect(user='pythonscript', password='pythonDeshita', host=piAddress, database=dbName)
  except mysql.connector.Error as err:
    print("Connection issue! " + str(err))
    return (None, None)
  else:
    c = socket.cursor()
    try:
      c.execute("use {}".format(dbName))
    except:
      print("Unable to use database {}!".format(dbName))
      return (socket, None)
  return (socket, c)
      
def _singleton():
  print("-- Singleton databasehelper test beginning. --")
  print("Connecting... ", end='')
  (s, co) = connect()
  socket = s
  c = co
  if (socket == None or c == None):
    print("Connection failed, exiting")
    sys.exit()
  print("success.\nAcquiring user data for {}... ".format(defaultUsername), end='')
  showListData = scrapedata.efu()
  sld = []
  for s in showListData:
    sld.append((("", defaultUsername) + showListReader(s))[1:])
  print("complete.\nNow initiating database management class... ".format(len(sld)), end='')
  db = buildDB(c, socket, userShows=sld)
  print("success.\nNow beginning population of database with 1 user and {} shows.")
  db.go()
  print("-- Full process finished. --")

def _constructDataForUser(username, c):
  showListData = scrapedata.efu(username)
  sld = []
  for s in showListData:
    sld.append((("", username) + showListReader(s))[1:])
  db = buildDB(c, socket, userShows=sld)
  db.go()
  
def _close():
  if (c != None):
    c.close()
  if (socket != None):
    socket.close()
  print("c and socket have been closed.")

# --------------------------------------------
# Functions meant to be used by other classes

class databaseAssistant:

  def __init__(self):
    self.socket = None
    self.cursor = None

  def getUserData(self, username=defaultUsername):
    # Retrieves user data.
    if (self.socket == None or self.cursor == None):
      (self.socket, self.cursor) = _connect()
    if (self.socket == None or self.cursor == None):
      print("Connection failed in getShowData.")
      sys.exit()
    self.cursor.execute("select * from users where uid='{}' limit 1;".format(username))
    return self.cursor.fetchone()

  def getUserShowData(self, username=defaultUsername, fancy=False):
    # Retrieves show data for a specific user.
    if (self.socket == None or self.cursor == None):
      (self.socket, self.cursor) = _connect()
    if (self.socket == None or self.cursor == None):
      print("Connection failed in getShowData.")
      sys.exit()
    self.cursor.execute("select * from users where uid='{}' limit 1;".format(username))
    userExists = self.cursor.fetchone() != None
    if (userExists == False):
      _constructDataForUser(username, self.cursor)
    if (fancy):
      self.cursor.execute("select s.name,u.score,u.date,u.eps from ((select sid,score,date,eps from showlist where uid='{}') as u inner join shows as s on u.sid=s.sid)".format(username))
    else:
      self.cursor.execute("select sid,score,date,eps from showlist where uid='{}';".format(username))
    return self.cursor.fetchall()

  def getShowData(self, showid):
    # Retrieves data for a specific show or list of shows.
    if (isinstance(showid, int)):
      showid = [showid]
    showid = ",".join(str(x) for x in showid)
    print(showid)
    if (self.socket == None or self.cursor == None):
      (self.socket, self.cursor) = _connect()
    if (self.socket == None or self.cursor == None):
      print("Connection failed in getShowData.")
      sys.exit()
    self.cursor.execute("select * from shows where sid in ({})".format(str(showid)))
    return self.cursor.fetchall()

# --------------------------------------------

warnings.filterwarnings('ignore')
atexit.register(_close)

if __name__ == "__main__":
  singleton()
  
