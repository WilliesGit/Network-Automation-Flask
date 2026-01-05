from flask import Flask, jsonify, request, render_template, url_for
from netmiko import ConnectHandler 
from difflib import HtmlDiff 
import re 
from collections import defaultdict
import json
import os
import threading

app = Flask(__name__)





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
