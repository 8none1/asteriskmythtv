#!/usr/bin/python
#
# Get some guide information from a rough descrption of a programme
#
#
# Useful links:  
# https://github.com/MythTV/mythtv/blob/master/mythtv/bindings/python/MythTV/methodheap.py
# http://www.mythtv.org/wiki/Titanimport.py
# http://zaf.github.io/asterisk-googletts/
#
# Will Cooke - 15th December 2013
# http://www.whizzy.org
# Twitter: @8none1
#
# Made available with no restrictions and no testing.
# I have no idea what I'm doing.


import MythTV
import sys
#import parsedatetime.parsedatetime as pdt
import datetime
import os

os.environ['MYTHCONFDIR'] = "/var/lib/asterisk/.mythtv"

sim=False
env = {}
commands=['record','delete','channel']
debug = True
#cal = pdt.Calendar()
chan_lookup={'bbc1':'BBC 1', 'bbc2':'BBC 2', 'bbc3':'BBC THREE', 'bbc4':'BBC FOUR',
             '5star':'5*', '5star+1':'5* +1', 'channel4+1':'Channel 4+1', 'channel5':'Channel 5',
             'channel5+1':'Channel 5+1', 'e4':'E4','e4+1':'E4+1', 'more4':'More4', 'channel4':'Channel 4'
            }
              
#db = MythTV.MythDB(DBHostName="localhost", DBName="mythconverg", DBUserName="mythtv", DBPassword="TEkOj2BU")
db = MythTV.MythDB()
guide_list = []



def check_commands(data):
  s = data.split()
  for k in commands:
    if k in s:
      return k
  return False

def agi_out(string):
  sys.stdout.write("%s\n" % string)
  sys.stdout.flush()

def log(string):
  if debug:
    sys.stderr.write("%s\n" % string)
    sys.stderr.flush()

def speak(string):  
  sys.stdout.write("""EXEC AGI googletts.agi,"%s",en\n""" % string)
  sys.stdout.flush()

def clean_up(string):
  string = string.replace(",", "")
  string = string.replace(".", "")
  return string


while 1:
  line = sys.stdin.readline().strip()
  if line=='':
    break
  try:
      key,data=line.split(':')
      if key[:4] != "agi_":
          log("Ignoring something which is not AGI header")
          continue
      else:
        key = key.strip()
        data = data.strip()
        if key != '':  env[key]=data
  except:
    speak("Sorry, does not compute")
    agi_out("200 result=0")
    sys.exit(1)

    
#log("AGI Environment Dump:")
#for key in env.keys():
#   log(" -- %s = %s" % (key, env[key]))


if 'agi_arg_1' in env:
  utterance = env['agi_arg_1'].lower()
  command = check_commands(utterance)
  if command == "record":
    utterance = clean_up(utterance)
    title   =   utterance.partition(command)[2].rpartition(' on ')[0].strip()
    channel =   utterance.partition(command)[2].rpartition(' on ')[2].replace(" ","")
    if channel in chan_lookup:
      channel = chan_lookup[channel]
    #stime,fmt    =   cal.parse(utterance.partition(command)[2].rpartition('at')[2].partition('on')[0].strip())
    #stime = datetime.datetime(*stime[:6])
    log("Title = "+title)
    log("channel = "+channel)
    #log("time = "+str(stime))
    guides = db.searchGuide(fuzzytitle=title, callsign=channel, startafter=datetime.datetime.now())
    for x in range(10):
      try:
        guide_list.append(guides.next())
      except StopIteration:
         break
    if len(guide_list) > 0:
      speak("I found a matching programme.")
      guide = guide_list[0]
      if not sim:
         rec = MythTV.Record.fromGuide(guide, MythTV.Record.kAllRecord)
      else:
        log("Simulation only.  Not really doing anything")
      speak(clean_up(guide.get('title')))
      speak(clean_up(guide.get('description')))
      speak(guide.get('starttime').strftime("%A %d %B at %I %M %p"))
      speak("Recording set.  Goodbye.")
    else:
      speak("Sorry, I didn't find that programme.  Better luck next time.")

  else:
    log("No commands found.")
    speak("I didn't hear a command.  Please try again.")    
else:
    speak("Meh.  General error")


agi_out("200 result=0")

