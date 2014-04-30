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

  AllArtist = []

  # Read The masterList of artists
  with open(__location__+"/AllArtists.txt") as f:
    AllArtists = f.read().splitlines()

  # Find the latest GPWW site
  latestURLs = retrieveLatest(__site__)

  # if devMode:
  #   latestURLs = ['http://www.bbc.co.uk/programmes/b03zjd84#segments']

  # Read in the GPWW website:
  for curURL in latestURLs:
    TempHTML = readGPWW(curURL)

    # Create a list of Artists played this week
    AllArtists = getNewArtists(TempHTML,AllArtists)


  playListTxt = ""

  AllArtists = sorted(AllArtists)
  txt = open(__location__+"/AllArtists.txt", "w")
  for artist in AllArtists:
    txt.write("%s\n" % artist)
    # Lookup artist's top10 from spotify and return uri's for playlist
  txt.close()


  txt = open("playlist.txt", "w")

  for artist in AllArtists:
    songs = top10(artist)
    for song in songs:
        txt.write("%s\n" % song["uri"])
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
