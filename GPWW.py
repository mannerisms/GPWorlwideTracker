# Read Gilles Peterson website
# parse lines like <span class="artist" property="foaf:name">Electric Wire Hustle</span>


# Regular Expressions
reArtists = "class=\"artist\" property=\"foaf:name\">([\w\s]*)</span>"
reSites = "<a href=\"/programmes/([\S]*)#segments\">Music Played</a>"


# Creates logs and prints whilst developing
devMode = False

# Imports
import urllib2, os, sys, re
import requests # for querying the API
import json # for interpreting the data returned by the API

# Path to Script
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
__site__ = 'http://www.bbc.co.uk/programmes/b01fm4ss/episodes/guide'

def main():

  if devMode: print "Script Started"

  AllArtist = [] # List to hold all unique artists
  AllTracks = [] # List to hold all unique tracks
  newTracks = [] # List to hold all freshly added tracks

  # Read The masterList of artists
  with open(__location__+"/AllArtists.txt") as f:
    AllArtists = f.read().splitlines()

  # Read The masterList of all tracks
  with open(__location__+"/playlist.txt") as f:
    AllTracks = f.read().splitlines()  

  # Find the latest GPWW site
  latestURLs = retrieveLatest(__site__)

<<<<<<< HEAD
  # if devMode:
  #   latestURLs = ['http://www.bbc.co.uk/programmes/b03zjd84#segments']
=======
  # In devMode, only check one week's new artists
  if devMode:
    latestURLs = ['http://www.bbc.co.uk/programmes/b03zjd84#segments']
>>>>>>> FETCH_HEAD

  # Read in the GPWW website:
  for curURL in latestURLs:
    if devMode:
      print "Checking a new URL"
    TempHTML = readGPWW(curURL)

    # Create a list of Artists played this week
    AllArtists = getNewArtists(TempHTML,AllArtists)


  playListTxt = ""
  artistsTxt = ""

  AllArtists = sorted(AllArtists)

  iter = 1
  for artist in AllArtists:
    if devMode: print "Checking %s for new songs" %artist
    artistsTxt += "%s\n" % artist
    songs = top10(artist)
    for song in songs:
        playListTxt += "%s\n" % song["uri"]
        if song["uri"] not in AllTracks:
          newTracks.append(song)
          if devMode: print "New Track found"
  
  # Write text files for storage
  txt = open(__location__+"/AllArtists.txt", "w")
  txt.write(artistsTxt)
  txt.close()
  txt = open(__location__+"/playlist.txt", "w")
  txt.write(playListTxt)
  txt.close()


  # Temporary, but has to eventually do something nifty with the new tracks
  txt = open(__location__+"/FreshTracks.txt", "w")
  for song in newTracks:
    txt.write("%s\n" %song["uri"])
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
    if artist not in lst:
      lst.append(artist)
      if devMode:
        print "New artist added: %s" %artist

  return lst

# Function copied from http://www.andresworld.co.uk/code/creating-a-festival-playlist-on-spotify-using-python/
def top10(artist):
  # an empty list of tracks
  tracks = []
  # set up for requests module
  query_params = {'q': 'artist:'+artist} # nospace after colon
  endpoint = 'http://ws.spotify.com/search/1/track.json'
  response = requests.get(endpoint, params= query_params)
  # print response.status_code
  # print artist
  if response.status_code == 200: # server responds nicely
    data = json.loads(response.content) # load the json data
    i = 0
    while len(tracks) < 10:       # check we have some results, or haven't reached the end of them      
      if int(data['info']['num_results']) == i or 100 == i:
        break
      # construct our 'track' library
      track = {'name':data['tracks'][i]['name'], 'artist':data['tracks'][i]['artists'][0]['name'], 'uri':data['tracks'][i]['href']}       
      # check the returned artist matches the queried artist      
      if artist == track['artist']:
        add = True      
        # Check the track is available in my territory -> NL
        if not 'NL' in data['tracks'][i]['album']['availability']['territories']:
          add = False
        # Check the track isn't included already, eliminates including single and album versions
        for t in tracks:
          if t['name'] == track['name']:
            add = False
        # Passed all the tests?
        if add:
          tracks.append(track)
      i = i + 1
    return tracks
  else:
    # bad response from the server
    print artist+' caused an error'


if __name__ == '__main__':
  main()
