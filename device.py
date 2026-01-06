from flask import Flask, jsonify, request, render_template, url_for
from netmiko import ConnectHandler 
from difflib import HtmlDiff 
import re 
from collections import defaultdict
import json
import os
import threading

app = Flask(__name__)


#File to store devices information in JSON format
device_db_file = 'devices_db.json'


#Function to write device info to file
def writeToFile(devices_db):
    try:
        with open(device_db_file, 'w') as devFile:
            #Using json.dump() method to write data to file
            json.dump(dict(devices_db), devFile)  

        print(f"Data written to {device_db_file}")

    except (Exception, IOError) as e:
        print(f"Write error: {e}")


#Function to load device info from file
def loadFromFile():
    try:
        if os.path.exists(device_db_file):
          with open(device_db_file, 'r') as devFile:
              #Using json.load() method to read data from file
              return json.load(devFile)

        else:
          print(f"{device_db_file} not found")
          return defaultdict(dict)


    except FileNotFoundError:
        return defaultdict(dict)



devices_db = loadFromFile()
if not devices_db:
    #Returns an empty dictionary if file not found or empty
    devices_db = defaultdict(dict)



#Defining route to render html pages
@app.route("/", methods=["GET", "POST"])
def home():
  return render_template("dashboard.html")

@app.route("/hostname", methods=["GET", "POST"])
def hostname():
  return render_template("hostname.html")

@app.route("/runningConfig", methods=["GET", "POST"])
def runningConfig():
  return render_template("running-config.html")

@app.route("/startupConfig", methods=["GET", "POST"])
def startupConfig():
  return render_template("startup-config.html")

@app.route("/compareConfigs", methods=["GET", "POST"])
def compareConfigs():
  return render_template("compare-config.html")

@app.route("/ciscoHardening", methods=["GET", "POST"])
def ciscoHardening():
  return render_template("cisco-hardening.html")

@app.route("/loopback", methods=["GET", "POST"])
def loopback():
  return render_template("loopback.html")

@app.route("/interface", methods=["GET", "POST"])
def interface():
  return render_template("interface.html")

@app.route("/routeProtocols", methods=["GET", "POST"])
def routeProtocols():
  return render_template("route-protocols.html")

@app.route("/ACL", methods=["GET", "POST"])
def ACL():
  return render_template("acl.html")






if __name__ == "__main__":
  app.run(debug=True)
