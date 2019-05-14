from bs4 import BeautifulSoup
import html
import requests
import ast
import sys
import re
import time

rxSplit = re.compile(r'\{(.)+?\}')

def efu(username="DentistRhapsody", verbose=False):
  return extractFromUsername(username, verbose)
def extractFromUsername(username="DentistRhapsody", verbose=False):
  shows = []
  if verbose:
    print("This tool will extract the MAL profile of '" + username + "'.\n\tDownloading webpage now...", end="")
  pageRaw = requests.get("https://myanimelist.net/animelist/" + username) # + "?status=7&order=6&order2=0"
  while(not pageRaw):
    if verbose:
      print(" failed. ", end="")
    yn = input("->\tError code " + str(pageRaw.status_code) + " occurred. Would you like to retry? y/n >> ")
    if (yn.index("y") or yn.index("Y")):
      pageRaw = requests.get("https://myanimelist.net/animelist/" + username)
    else:
      print("Aborting...")
      return []
  if verbose:
    print(" complete.")
    print("\tBeginning parse of downloaded webpage...", end="")
  soup = BeautifulSoup(pageRaw.text, 'html.parser')
  data = soup.find_all(class_="list-table")[0].attrs['data-items']
  data = data.replace(":false,", ":False,")  # Temporary input purifying of exclusively edgecases I have previously caught.
  data = data.replace(":true,", ":True,")
  data = data.replace(":null,", ":None,")
  data = html.unescape(data)
  iter = rxSplit.finditer(data)
  for match in iter:
    shows.append(match.group())
  for i in range(0, len(shows)):  # Purify this input!
    shows[i] = ast.literal_eval(shows[i])
  if verbose:
    print(" complete.\n\tBeginning purification of irrelevant data...", end="")
  validEntries = [False] * len(shows)
  totalInvalids = len(shows)
  for i in range(0, len(shows)):
    if (shows[i]['score'] > 0 and (shows[i]['anime_media_type_string'] == 'TV' or shows[i]['anime_media_type_string'] == 'movie')):
      validEntries[i] = True
      totalInvalids -= 1
  for i in reversed(range(0, len(shows))):
    if not validEntries[i]:
      del shows[i]
  if verbose:
    print(" complete. " + str(totalInvalids) + " shows were removed.")
  return shows
  # 'shows' is now a list of dictionaries, each one representing up to 300 shows extracted from MAL.
  # The number 300 is how many MAL loads by default. Look into selenium / phantomjs to maybe get all?

def singleton():
  print("Welcome to the Witte MAL Extractor!")
  time.process_time() 
  shows = extractFromUsername("DentistRhapsody", True)
  endTime = time.process_time() 
  if (len(shows) > 0):
    print("Population was successful!")
    print("Variable 'shows' contains " + str(len(shows)) + " shows, such as '" + shows[0]['anime_title'] + "' and '" + shows[-1]['anime_title'] + "'.")
  print("Total time taken: " + str(endTime * 1000) + " ms.")
  
if __name__ == "__main__":
  singleton()
