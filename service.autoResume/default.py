'''
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import os
import xbmc
import xbmcaddon
import json
from time import sleep


ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
FOLDER = ADDON.getSetting('autoresume.save.folder').encode('utf-8', 'ignore')
FREQUENCY = int(ADDON.getSetting('autoresume.frequency'))
PATH = os.path.join(FOLDER, 'autoresume.txt')
PATHLIST = os.path.join(FOLDER, 'autoresume.m3u')

def resume():
  for x in range(0,120):
    if os.path.exists(FOLDER):
      if os.path.exists(PATH):
        # Read from autoresume.txt.
        f = open(PATH, 'r')
        mediaFile = f.readline().rstrip('\n')
        position = 0
        playlistPos = 0

        if mediaFile:
          position = float(f.readline())
          playlistPos = int(f.readline())
        f.close()

        if playlistPos  > 0:
            # Load playlist
            log("Playlist ************************")
            if os.path.exists(PATHLIST):
                log("Playlist loaded")
                log(PATHLIST)
                result = xbmc.PlayList(xbmc.PLAYLIST_MUSIC).load(PATHLIST)
                log(result)

                xbmc.Player().playselected(playlistPos)
                xbmc.Player().pause()
                while (not xbmc.Player().isPlaying()):
                  sleep(0.5)
                sleep(0.5)
                xbmc.Player().seekTime(position)
        else:
            # Play file.
            xbmc.Player().play(mediaFile)
            xbmc.Player().pause()
            while (not xbmc.Player().isPlaying()):
              sleep(0.5)
            sleep(1)
            # Seek to last recorded position.
            xbmc.Player().seekTime(position)
            sleep(1)
            # Make sure it actually got there.
            if abs(position - xbmc.Player().getTime()) > 30:
              xbmc.Player().seekTime(position)

      break
    else:
      # If the folder didn't exist maybe we need to wait longer for the drive to be mounted.
      sleep(5)

def recordPosition():
  if xbmc.Player().isPlayingAudio():
    mediaFile = xbmc.Player().getPlayingFile()
    position = xbmc.Player().getTime()
    playlistPos = xbmc.PlayList(xbmc.PLAYLIST_MUSIC).getposition()

    # Write info to file
    f = open(PATH, 'w')
    f.write(mediaFile)
    f.write('\n')
    f.write(repr(position))
    f.write('\n')
    f.write(repr(playlistPos))
    f.write('\n')

    f.close()

    json_string = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Playlist.GetItems", "params": { "properties": ["file"], "playlistid": 0 }, "id": 1}')
    parsed_json = json.loads(json_string)

    if parsed_json['result']['limits']['total'] > 0:
        f = open(PATHLIST, 'w')

        for item in parsed_json['result']['items']:
            f.write(item['file'].encode('utf8'))
            f.write('\n')

        f.close()

def log(msg):
  xbmc.log("%s: %s" % (ADDON_ID, msg), xbmc.LOGNOTICE)


if __name__ == "__main__":
  resume()
  while (not xbmc.abortRequested):
    recordPosition()
    sleep(FREQUENCY)
