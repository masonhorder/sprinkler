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
from time import sleep

cron = CronTab(user="pi")


zonePins = [7,11,13,15,29,37,35,32,36,38,12,16,18,22,24,26]

scheduleId = list(sys.argv)[1]


def clear():
  GPIO.setmode(GPIO.BOARD)
  GPIO.setwarnings(False)
  for zone in zonePins:
    GPIO.setup(zone,GPIO.OUT)
    GPIO.output(zone,GPIO.HIGH)

clear()

# with open("data/zones.json") as zoneFileContent:
#   data = zoneFileContent.read()
#   zoneJson = json.loads(data)

with open("/home/pi/server/data/schedules.json") as scheduleFileContent:
  data = scheduleFileContent.read()
  schedulesJson = json.loads(data)
  

# zones=zoneJson['zones']

schedules=schedulesJson['schedules']

index = 0
for schedule in schedules:
  
  if index == int(scheduleId)-1:
    for zone in schedule[3]:
      print("running zone: " + str(zone[0]))
      GPIO.output(zonePins[zone[0]-1],GPIO.LOW)
      sleep(zone[1])
      GPIO.output(zonePins[zone[0]-1],GPIO.HIGH)


  index+=1