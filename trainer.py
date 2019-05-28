import databasehelper

defaultUsername = "DentistRhapsody"

# Class that does the work
class trainer:
  def __init__(self, username=defaultUsername):
    self.username = username
    self.printListOfShows()
    
  def printListOfShows(self):
    d = databasehelper.databaseAssistant()
    print(d.getUserShowData(fancy=True))
    
  def printShowData(self):
    d = databasehelper.databaseAssistant()
    print(d.getShowData([1, 28825, 22123]))

def singleton():
  print("-- Trainer has been launched independently. --")
  t = trainer()
  print("-- Trainer has completed. --")
  
if __name__ == "__main__":
  singleton()
