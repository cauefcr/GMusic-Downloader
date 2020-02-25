#!/usr/bin/env python

import os
import sys
import eyed3
from goldfinch import validFileName as vfn
from gmusicapi import Mobileclient
import getpass
import json
try:
  from urllib.request import urlretrieve
except ImportError:
  from urllib import urlretrieve


def normalizePath(input):
  return vfn(input, space="keep", initCap=False).decode('utf-8').rstrip(".")  


targetDir = os.getcwd()
# targetDir = "D:/Minhas músicas"

eyed3.log.setLevel("ERROR")


api = Mobileclient(debug_logging=False)
if os.path.exists("config.json"):
  with open('config.json', 'r') as fp:
    ids = json.load(fp)
  i = 0
  while True:
    try:
      api.oauth_login(ids[i])
      break
    except:
      print("oops, this didn't work, trying again")
      i+=1
      i%=len(ids)
else:
  oa = api.perform_oauth()
  api.oauth_login(Mobileclient.FROM_MAC_ADDRESS,oauth_credentials=oa)
  devices = api.get_registered_devices()
  ids = []
  for i in devices:
    ids.append(i['id'][2:])
  with open('config.json', 'w') as fp:
      json.dump(ids, fp)



songs = api.get_all_songs()
for song in songs:
  dirName = normalizePath("%s - %s" % (song["artist"], song["album"]))
  dirPath = targetDir + "/" + dirName
  if not os.path.exists(dirPath):
    print("downloading to directory: " + dirPath)
    os.makedirs(dirPath)
  fileName = normalizePath("%s. %s - %s.mp3" % (song["trackNumber"], song["artist"], song["title"]))
  filePath = dirPath + "/" + fileName
  if os.path.exists(filePath):
    print(fileName+" already exists, skipping")
    continue
  url = api.get_stream_url(song_id=song["id"], quality="hi")
  print("downloading: " + fileName)
  urlretrieve(url, filePath)
  
  audio = eyed3.load(filePath)
  if audio.tag is None:
    audio.tag = eyed3.id3.Tag()
    audio.tag.file_info = eyed3.id3.FileInfo(filePath)
  audio.tag.artist = song["artist"]
  audio.tag.album = song["album"]
  audio.tag.album_artist = song["artist"]
  audio.tag.title = song["title"]
  audio.tag.track_num = song["trackNumber"]
  audio.tag.save()

print("done.")
