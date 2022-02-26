from __future__ import division
import re
import sys
import os
from getpass import getpass
from flask import Flask, request, render_template,jsonify,redirect
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import RPi.GPIO as GPIO
import json
from crontab import CronTab

cron = CronTab(user="pi")


zonePins = [7,11,13,15,29,37,35,32,36,38,12,16,18,22,24,26]

zones={}
schedules={}

def setData():
  global zones, schedules
  print("retreiving data")
  with open("/home/pi/server/data/zones.json") as zoneFileContent:
    data = zoneFileContent.read()
    zoneJson = json.loads(data)

  with open("/home/pi/server/data/schedules.json") as scheduleFileContent:
    data = scheduleFileContent.read()
    schedulesJson = json.loads(data)
    

  zones=zoneJson['zones']

  schedules=schedulesJson['schedules']

setData()

def clear():
  GPIO.setmode(GPIO.BOARD)
  GPIO.setwarnings(False)
  for zone in zonePins:
    GPIO.setup(zone,GPIO.OUT)
    GPIO.output(zone,GPIO.HIGH)

clear()

def turnZoneOn(zone):
  print("on")
  GPIO.output(zonePins[zone-1],GPIO.LOW)
  zones[zone-1][2]=1

def turnZoneOff(zone):
  GPIO.output(zonePins[zone-1],GPIO.HIGH)
  zones[zone-1][2]=0


app = Flask(__name__)

def clearAllJobs():
  print("clearing")
  cron.remove_all()
  cron.write()
  clear_zones = cron.new(command = "/usr/bin/python3 ~/server/server.py")
  clear_zones.setall("@reboot")
  cron.write()

@app.route('/')
def home():
  index = 0
  clearAllJobs()
  for schedule in schedules:
    cron_command = "/usr/bin/python3 ~/server/runSchedule.py"
    cron_command += " " + str(index+1) 
    
    job = cron.new(command = str(cron_command))
    cron_time = str(schedule[1]) + " " + str(schedule[0]) + " * * *"
    job.setall(cron_time)
    print(job.is_valid())
    job.enable()
    cron.write()


    index+=1


  return render_template('home.html', zones=zones, schedules=schedules)


@app.route('/zoneon', methods=['GET', 'POST'])
def zoneon():
  zone = int(request.args.getlist("zone")[0])
  turnZoneOn(zone)
  return redirect("/")

@app.route('/zoneoff', methods=['GET', 'POST'])
def zoneoff():
  zone = int(request.args.getlist("zone")[0])
  turnZoneOff(zone)
  return redirect("/")

@app.route('/newSchedule', methods=['GET'])
def newSchedule():
  data = request.args
  print(data.getlist('name')[0])

  addition = 0
  if data.getlist('ampm')[0] == "pm":
    addition = 12
  schedules+=[[int(data.getlist('hour')[0])+addition,int(data.getlist('minute')[0]),data.getlist('name')[0],[]]]
  schedulesJson["schedules"]=schedules
  with open('/home/pi/server/data/schedules.json', 'w') as scheduleWrite:
    json.dump(schedulesJson, scheduleWrite)
  print(schedules)
  return redirect("/")











@app.route('/assignZone', methods=['GET'])
def assignZone():
  with open("/home/pi/server/data/zones.json") as zoneFileContent:
    data = zoneFileContent.read()
    zoneJson = json.loads(data)

  with open("/home/pi/server/data/schedules.json") as scheduleFileContent:
    data = scheduleFileContent.read()
    schedulesJson = json.loads(data)
    

  zones=zoneJson['zones']
  schedules=schedulesJson['schedules']
  data = request.args

  print(schedules[int(data.getlist('schedule')[0])-1][3])
  schedules[int(data.getlist('schedule')[0])-1][3]+=[[data.getlist('zone')[0], data.getlist('runDuration')[0]]]
  schedulesJson["schedules"]=schedules
  with open('/home/pi/server/data/schedules.json', 'w') as scheduleWrite:
    json.dump(schedulesJson, scheduleWrite)
  print(schedules)
  return redirect("/")


 
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

# labels make it the name
# editing run time
# editing run duration
# delete schedule
# make assignnig zone to schedule in one button
# general style
# show time in am/pm
# show run duration in minutes seconds
# change name of zone
# manual turn zone on deactivates others
# run schedule now
