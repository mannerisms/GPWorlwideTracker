# Read Gilles Peterson website
# parse lines like <span class="artist" property="foaf:name">Electric Wire Hustle</span>


# Regular Expressions
reArtists = "class=\"artist\" property=\"foaf:name\">([\w\s]*)</span>"
reSites = "<a href=\"/programmes/([\S]*)#segments\">Music Played</a>"


# Creates logs and prints whilst developing
devMode = True

# Imports
import urllib2, os, sys, re

# Path to Script
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
__site__ = 'http://www.bbc.co.uk/programmes/b01fm4ss/episodes/guide'

def main():

  AllArtist = []

  # Read The masterList of artists
  with open(__location__+"/AllArtists.txt") as f:
    AllArtists = f.read().splitlines()

  # Find the latest GPWW site
  latestURLs = retrieveLatest(__site__)

  if devMode:
    latestURLs = ['http://www.bbc.co.uk/programmes/b03zjd84#segments']

  # Read in the GPWW website:
  for curURL in latestURLs:
    TempHTML = readGPWW(curURL)

    # Create a list of Artists played this week
    AllArtists = getNewArtists(TempHTML,AllArtists)

  AllArtists = sorted(AllArtists)
  txt = open(__location__+"/AllArtists.txt", "w")
  for artist in AllArtists:
    txt.write("%s\n" % artist)
  txt.close()

  if devMode:
    print "Script Complete"


def retrieveLatest(EpisodeURL):
  newSites = []
  response = urllib2.urlopen(EpisodeURL)
  html = response.read()
  response.close()

  codes = re.findall(reSites, html)

  for code in codes:
    code = "http://www.bbc.co.uk/programmes/%s#segments" %code
    newSites.append(code)

  return newSites


def readGPWW(siteAddress):
  response = urllib2.urlopen(siteAddress)
  txt = response.read()
  response.close()
  return txt

# Reads website and parses for artists
def getNewArtists(txt, lst):

  artists = re.findall(reArtists, txt)

  for artist in artists:
    if devMode:
     print "Checking artist: %s" %artist
    if artist not in lst:
      lst.append(artist)
      if devMode:
        print "New artist added: %s" %artist

  return lst

if __name__ == '__main__':
  main()
