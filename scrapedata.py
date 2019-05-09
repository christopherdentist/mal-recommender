from bs4 import BeautifulSoup
import requests
import ast
import sys
import re

malUser = "DentistRhapsody"
rxSplit = re.compile(r'\{(.)+?\}')
shows = []

def init():
  print("Welcome to the Witte MAL Extractor!")
  print("Using default MAL profile of " + malUser + ".")
  print("Downloading webpage...", end="")
  pageRaw = requests.get("https://myanimelist.net/animelist/" + malUser) # + "?status=7&order=6&order2=0"
  while(!pageRaw):
    yn = input(" failed: error code " + str(pageRaw.status_code) + ". Would you like to retry? y/n >> ")
    if (yn.index("y") || yn.index("Y")):
	  pageRaw = requests.get("https://myanimelist.net/animelist/" + malUser")
	else:
	  print("Quitting...")
	  sys.exit()
  soup = BeautifulSoup(pageRaw.text, 'html.parser')
  data = soup.find_all(class_="list-table")[0].attrs['data-items']
  data = data.replace(":false,", ":False,")  # Temporary input purifying
  data = data.replace(":true,", ":True,")    # of exclusively edgecases I
  data = data.replace(":null,", ":None,")    # have previously caught.
  iter = rxSplit.finditer(data)
  for match in iter:
    shows.append(match.group())
  for i in range(0, len(shows)):  # Purify this input!
    shows[i] = ast.literal_eval(shows[i])
  
  # 'shows' is now a list of dictionaries, each one representing up to 300 shows extracted from MAL
  