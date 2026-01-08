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



#Function to configure hostname on a device
def configureHostname(device_key, device_info, devices_db):
  try:
  
      device_data = devices_db.get(device_key)

      if not device_data:
        return {
           'status': 'error',
           'error': f'Device {device_key} not found in the database'
        }

      device_config = {
        'device_type': 'cisco_ios',
        'host': device_data['ip'],
        'username': device_data['username'],
        'password': device_data['password'],
        'secret': device_data['secret']
      }

      session = ConnectHandler(**device_config)

      if device_data.get('secret'):
        session.enable()

      #Configuring hostname
      hostname_command = f"hostname {device_info['hostname']}"
      session.send_config_set(hostname_command)

      output = session.send_command('show running-config | include hostname')
      print(output)

      session.disconnect()

      return {
      'device': device_key,
      'ip': device_data['ip'],
      'username': device_data['username'],
      'hostname': device_info['hostname'],
      'status': 'success'
      }

  
  except netmiko.NetMikoTimeoutException as e: 
     return {
        'status': 'error',
        'error': f'Connection timeout: {str(e)}'}
  
  except netmiko.NetMikoAuthenticationException as e: 
     return {
        'status': 'error',
        'error': f'Authentication failed: {str(e)}'}
  
  except (ValueError, KeyError, OSError) as e:
    return {
       'status': 'error',
       'error': str(e)}
  
  except Exception as e:
    return {
       'status': 'error',
       'error': str(e)}
  


#Funtion to get running configuration from a device
def runCon(device_key, device_info):
    try:
      device_data = device_info
      
      if not device_data:
         return {
           'status': 'error',
           'error': f'Device {device_key} not found in the database'
        }

      device_config = {
        'device_type': 'cisco_ios',
        'host': device_data['ip'],
        'username': device_data['username'],
        'password': device_data['password'],
        'secret': device_data['secret']
      }

      session = ConnectHandler(**device_config)

      if device_data.get('secret'):
          session.enable()

      output = session.send_command('show running-config')

      #Creating a file path to store devices running configuration
      filename = f'RunCon/{device_key}_running.txt'
      os.makedirs('RunCon', exist_ok=True)

      #Writing to file
      try:
         with open(filename, 'w') as run_file:
          run_file.write(output)
      
      except IOError as e:
        return {
           'status': 'error',
           'error': str(e)
        }
    
      print(output)

      session.disconnect()

      
      return {
        'device' : device_key,
        'message': f'Running config saved to file {filename}',
        'status': 'success'
      }

      
    except netmiko.NetMikoTimeoutException as e: 
      return {
          'status': 'error',
          'error': f'Connection timeout: {str(e)}'}
    
    except netmiko.NetMikoAuthenticationException as e: 
      return {
          'status': 'error',
          'error': f'Authentication failed: {str(e)}'}
    
    except (ValueError, KeyError, OSError, IOError) as e:
      return {
        'status': 'error',
        'error': str(e)}
    
    except Exception as e:
      return {
        'status': 'error',
        'error': str(e)}

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
