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



#Function to get startup configuration from a device
def startCon(device_key, device_info):
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

      output = session.send_command('show startup-config')

      #Creating a file path to store devices startup configuration
      filename = f'StartCon/{device_key}_startup.txt'
      os.makedirs('StartCon', exist_ok=True)

      #Writing to file
      try:
        with open(filename, 'w') as start_file:
          start_file.write(output)

      except IOError as e:
        return {
           'status': 'error',
           'error': str(e)
        }
    
      print(output)

      session.disconnect()

      
      return {
        'device' : device_key,
        'message': f'Startup config saved to file {filename}',
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
    
    

#Function to configure an interface on a device
def interfaceConfig(device_key, interface_configs, devices_db):
   try:
      device_data = devices_db.get(device_key)
      if not device_data:
          return {
             'status': 'error',
             'error': f'Device {device_key} not found in the database'
          }
      
      int_config = ''
      #Looping through the interface configurations for each device
      for int_key, int_con in interface_configs.items():
        if int_key == device_key:
          int_config = int_con
          break

      interface = int_config['interface']
      ip = int_config['ip']
      mask = int_config['mask']

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


      #Interface Configuration Commands
      interface_command = [
              f"interface {interface}",
              f"ip address {ip} {mask}",
              "no shutdown"]
                          
       
      session.send_config_set(interface_command)

      output = session.send_command(f'show ip interface brief | include {interface}')
      print(output)


      session.disconnect()

      return {
        'device': device_key,
        'message': 'Configuration Complete!',
        'interface_info': output.strip(),
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
   

#Function to configure a loopback interface on a device
def loopbackConfig(device_key, loopback_configs, devices_db):
   try:
      device_data = devices_db.get(device_key)
      if not device_data:
          return {
             'status': 'error',
             'error': f'Device {device_key} not found in the database'
          }
      
      loopback_config = ''
      #Looping through the interface configurations for each device
      for key, loopback_con in loopback_configs.items():
        if key == device_key:
          loopback_config = loopback_con
          break

      interface = loopback_config['interface']
      ip = loopback_config['ip']
      mask = loopback_config['mask']


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

      #Loopback Configuration Commands
      loopback_command = [
            f"interface {interface}",
            f"ip address {ip} {mask}",
            "no shutdown"]
                        

      session.send_config_set(loopback_command)

      output = session.send_command(f'show ip interface brief | include {interface.capitalize()}')
      print(output)

      session.disconnect()

      return{
        'device': device_key,
        'message': 'Configuration Complete!',
        'loopback_info': output.strip(),
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
   


#Function to configure routing protocols on a device 
def routeConfig(device_key, route_config, devices_db):
   try:
      device_data = devices_db.get(device_key)

      if not device_data:
          return {
             'status': 'error',
             'error': f'Device {device_key} not found in the database'
          }
      
      #List to store routing commands
      commands = []
      protocol = ''


      for index, config in route_config.items():
          protocol = config['protocol']

          if protocol == "OSPF":
            print("Selected Protocol: ",protocol)
            commands = [
              f"router ospf {config['process_id']}",
              f"network {config['ip']} {config['mask']} area {config['area']}"
            ]


          elif protocol == "EIGRP":
            print("Selected Protocol: ",protocol)
            commands = [
              f"router eigrp {config['as_num']}",
              f"network {config['ip']} {config['mask']}"
            ]

        
          elif protocol == "RIP":
            print("Selected Protocol: ",protocol)
            commands = [
              f"router rip",
              f"version 2",
              f"network {config['ip']}"
            ]

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

      session.send_config_set(commands)

      output = session.send_command(f'show running-config | section router')
      print(output)

      session.disconnect()

      return{
        'device': device_key,
        'route_info': output.strip(),
        'message': f"{protocol} Configured Successfully",
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



#Function to configure ACL on a device
def aclConfig(device_key, acl_config, dir_config, devices_db):
   try:
      device_data = devices_db.get(device_key)

      if not device_data:
          return {
             'status': 'error',
             'error': f'Device {device_key} not found in the database'
          }

      #List to store all commands
      commands = []
      acl_commands = []
      dir_commands = []
      acl_type = ''
      acl_dir = ''

      #Looping through the ACL configurations for each device
      for index, acl in acl_config.items():
          acl_type = acl['type']

          if acl_type == "Standard":
            print("Selected Type: ",acl_type)
            acl_commands = [
              f"access-list {acl['deny_no']} {acl['deny_action']} {acl['deny_source']}",
              f"access-list {acl['permit_no']} {acl['permit_action']} {acl['permit_source']}"
            ]

          elif acl_type == "Extended":
            print("Selected Type: ",acl_type)
            acl_commands = [
              f"access-list {acl['deny_no']} {acl['deny_action']} {acl['deny_protocol']} {acl['deny_source']} {acl['deny_dest']} eq {acl['deny_port']}",
              f"access-list {acl['permit_no']} {acl['permit_action']} {acl['permit_protocol']} {acl['permit_source']} {acl['permit_dest']} eq {acl['permit_port']}",
              f"access-list {acl['permit_no']} permit {acl['permit_protocol']} any any"
            ]

      #Looping through the ACL direction configurations for each device
      for index, direction in dir_config.items():
           acl_dir = direction['direction']  

           if acl_dir == "in":
              print("Selected Direction: ",acl_dir)
              dir_commands = [
                f"interface {direction['interface']}",
                f"ip access-group {direction['group_no']} in"
            ] 

           elif acl_dir == "out":
              print("Selected Direction: ",acl_dir)
              dir_commands = [
                f"interface {direction['interface']}",
                f"ip access-group {direction['group_no']} out"
            ]
              
      
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

      #Combining ACL and direction commands
      commands.extend(acl_commands)
      commands.extend(dir_commands)

      session.send_config_set(commands, cmd_verify=False)

      output = session.send_command('show access-lists')

      session.disconnect()

      return {
        'device': device_key,
        'route_info': output.strip(),
        'message': f"{acl_type} Configured Successfully",
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



#API endpoint to receive device information and store it
@app.route("/api/device_info", methods=['POST'])
def device_info():

  #Retrieve user input as JSON data from the request
  data = request.json

  try:
    devices = data['devices']

    #Loops through devices and stores each device info in the devices_db
    for device_key, device_info in devices.items(): 
      devices_db[device_key] = device_info

    #Saving the devices confiiguration to file
    writeToFile(devices_db)
    return jsonify({'status':'success', 'results': 'Devices information stored'}), 200

  except (ValueError, KeyError, IOError) as e:
    return jsonify({'error': str(e)}), 400

  except Exception as e:
    return jsonify({'error': str(e)}), 400



#API endpoint to configure hostname on devices
@app.route("/api/hostname_config", methods=['POST'])
def hostname_config():

  #Retrieve user input as JSON data from the request
  data = request.json

  #List to store result to be sent back for processing
  results = []
  threads = []
  lock = threading.Lock()   

  
  hostnames = data['devices']
  
  def worker(device_key, device_info):
      result = configureHostname(device_key, device_info, devices_db)
      with lock:
          results.append(result)

  #Create a thread per device
  for device_key, device_info in hostnames.items():
      print('Device keys: ',device_key)
      
      t = threading.Thread(target=worker, args=(device_key, device_info))
      threads.append(t)
      t.start() 

  #Wait for all threads to complete
  for t in threads:
      t.join()

  any_success = False

  for r in results:
      if r.get('status') == 'success':
          any_success = True
          break
      
  if any_success:
      status_code = 200 
  else:
      status_code = 400

  return jsonify({'devices': results}), status_code



#API endpoint to get running configuration from devices
@app.route("/api/running_config", methods=['POST'])
def running_config():
    
    #Retrieve user input as JSON data from the request
    data = request.json

    #List to store result to be sent back for processing
    results = []
    threads = []
    lock = threading.Lock()   
    
    
    devices = data['devices']

    def worker(device_key, device_info):
        result = runCon(device_key, device_info)
        with lock:
            results.append(result)

    #Create a thread per device
    for device_key, device_info in devices.items(): 
      print('Device keys: ',device_key)
      
      t = threading.Thread(target=worker, args=(device_key, device_info))
      threads.append(t)
      t.start() 

    #Wait for all threads to complete
    for t in threads:
        t.join()

    any_success = False

    for r in results:
        if r.get('status') == 'success':
            any_success = True
            break
        
    if any_success:
        status_code = 200 
    else:
        status_code = 400

    return jsonify({'results': results}), status_code    
  

#API endpoint to get startup configuration from devices
@app.route("/api/start_config", methods=['POST'])
def start_config():
    #Retrieve user input as JSON data from the request
    data = request.json

    #List to store result to be sent back for processing
    results = []
    threads = []
    lock = threading.Lock()   
    
    
    devices = data['devices']

    def worker(device_key, device_info):
        result = startCon(device_key, device_info)
        with lock:
            results.append(result)

    #Create a thread per device
    for device_key, device_info in devices.items(): 
      print('Device keys: ',device_key)
      
      t = threading.Thread(target=worker, args=(device_key, device_info))
      threads.append(t)
      t.start() 

    #Wait for all threads to complete
    for t in threads:
        t.join()

    any_success = False

    for r in results:
        if r.get('status') == 'success':
            any_success = True
            break
        
    if any_success:
        status_code = 200 
    else:
        status_code = 400

    return jsonify({'results': results}), status_code  


#API endpoint to compare running and startup configurations
@app.route("/api/compare_configs", methods=['POST'])
def compare_configs():
    
    #Retrieve user input as JSON data from the request
    data = request.json
    #List to store result to be sent back for processing
    results = []

    try:
      device_key = data.get('device_key')
  
      if not device_key:
          results.append({'error': f'Device {device_key} is required'}), 400

      #Checks if file with the device_key(dev1, dev2, dev3) exists
      run_path = f"RunCon/{device_key}_running.txt"
      start_path = f"StartCon/{device_key}_startup.txt"
      diff_path = f"diff_{device_key}.html"
     

      #For running configuration
      if not os.path.exists(run_path):
        print(f"Missing: {run_path}")
        return jsonify({'error': f"Missing running configuration {run_path}"}), 404

      #For startup configuration
      if not os.path.exists(start_path):
        print(f"Missing: {start_path}")
        return jsonify({'error': f"Missing startup configuration {start_path}"}), 404


      #Reading running config from the file
      try:
        with open(run_path, 'r') as run_file:
          run_lines = run_file.read().splitlines()
      except IOError as e:
        return jsonify({'error': str(e)}), 400


      #Reading startup config from the file
      try:
        with open(start_path, 'r') as start_file:
          start_lines = start_file.read().splitlines()
      except IOError as e:
        return jsonify({'error': str(e)}), 400


      #Running comparison using difflib
      diff = HtmlDiff()
      comp_run_start = diff.make_file(run_lines, start_lines)

      try:
        with open(f"templates/{diff_path}", "w", encoding="utf-8") as diffFile:
          diffFile.write(comp_run_start)
      except IOError as e:
        return jsonify({'error': str(e)}), 400

      #Storing config difference in the templates folder 
      diff_url = f"/templates/{diff_path}" 
    

      #Appends the result
      results.append({
        'device' : device_key,
        'diff_url': diff_url,
        'message': f'Comparison saved to {diff_url}'
      })

      return jsonify({'status':'success', 'results': results}), 200

    
    except (ValueError, KeyError, OSError, IOError) as e:
      return jsonify({'error': str(e)}), 400
    
    except Exception as e:
      return jsonify({'error': str(e)}), 400
    


#API endpoint to check for Cisco device hardening advice
@app.route("/api/cisco_hardening", methods=['POST'])
def cisco_hardening():
    
    #Retrieve user input as JSON data from the request
    data = request.json

    #List to store result to be sent back for processing
    results = []

    try:
      device_key = data.get('device_key')
      device = data.get('selected_dev')
  
      if not device_key or not device:
          results.append({'error': f'Device {device_key} and {device} is required'}), 400


      #Checks if file with the device_key(dev1, dev2, dev3) exists
      run_path = f"RunCon/{device_key}_running.txt"
      
     
      #For running configuration
      if not os.path.exists(run_path):
        print(f"Missing: {run_path}")
        return jsonify({'error': f"Missing running configuration {run_path}"}), 404

  
      #Reading running config from the file
      try:
        with open(run_path, 'r') as run_file:
          run_lines = run_file.read().splitlines()
      except IOError as e:
        return jsonify({'error': str(e)}), 400


      #Cisco Device Hardening Advice
      hardening_advices = [
        {
          "id" : "no-pw-recovery",
          "pattern": r"^no service password-recovery",
          "commands": ["no service password-recovery"]
        },

        {
          "id" : "tcp-keepalives",
          "pattern": r"^service tcp-keepalives-(in|out)",
          "commands": ["service tcp-keepalives-in", "service tcp-keepalives-out"]
        },

        {
          "id" : "ip-options-drop",
          "pattern": r"^ip options drop",
          "commands": ["ip options drop"]
        },

        {
          "id" : "no-ip-source-route",
          "pattern": r"^no ip source-route",
          "commands": ["no ip source-route"]
        },

        {
          "id" : "memory-reserve",
          "pattern": r"^memory reserve console",
          "commands": ["memory reserve console"]
        },
        
      ]

      #List to store missing cisco hardening advice configuration
      missing_advice = []

      #Checking for missing hardening advice in the running configuration
      for advice in hardening_advices:
        found = False
        for line in run_lines:
              line = line.strip()
              if re.search(advice['pattern'], line, re.IGNORECASE):
                found = True
                break

        if not found:
          missing_advice.append({
              "id" : advice['id'],
              "commands": advice['commands']
          })
      print(missing_advice)


      #Appends the result
      results.append({
        'device' : device_key,
        'ip' : device['ip'],
        'missing_ad_count': len(missing_advice),
        'missing_advice': missing_advice,
        'message': 'Comparison Completed!'
      })

      return jsonify({'status':'success', 'results': results}), 200


    except (ValueError, KeyError) as e:
      return jsonify({'error': str(e)}), 400
    
    except Exception as e:
      return jsonify({'error': str(e)}), 400

      

#API endpoint to fix missing Cisco hardening advice 
@app.route("/api/fix_hardening", methods=['POST'])
def fix_hardening():
    
    #Retrieve user input as JSON data from the request
    data = request.json
    #List to store result to be sent back for processing
    results = []
    #List to store commands to be configured
    commands = []
    
    try:
      device_key = data.get('device_key')
      device = data.get('selected_dev')
      missing_advice = data.get('missing_advice')

      if not device_key or not device:
          results.append({'error': f'Device {device_key} and {device} is required'}), 400

      device_data = devices_db.get(device_key)


      device_config = {
          'device_type': 'cisco_ios',
          'host': device_data['ip'],
          'username': device_data['username'],
          'password': device_data['password'],
          'secret': device_data['secret']
      }

      session = ConnectHandler(**device_config)

      if device.get('secret'):
          session.enable()

      #Looping through the missing advice 
      for advice in missing_advice:
        advice_list = advice.get('commands')
        #Extending the commands list with the missing advice
        commands.extend((advice_list))
         
         
      session.send_config_set(commands)

      output = session.send_command('show running-config')
      print(output)


      #Saving updated running configuration to file
      run_path = f"RunCon/{device_key}_running.txt"

      #For running configuration
      if not os.path.exists(run_path):
        print(f"Missing: {run_path}")
        return jsonify({'error': f"Missing running configuration {run_path}"}), 404

      #Writing updated Running Config to file
      try:
        with open(run_path, 'w') as run_file:
          run_file.write(output)
      except IOError as e:
        return jsonify({'error': str(e)}), 400
      

      #Appends the result
      results.append({
        'device' : device_key,
        'ip' : device['ip'],
        'message': f'Configuration Fixed!. See {run_path}',
        
      })

      return jsonify({'status':'success', 'results': results}), 200


    
    except netmiko.NetMikoTimeoutException as e: 
     return jsonify({'error': str(e)}), 400
  
    except netmiko.NetMikoAuthenticationException as e: 
      return jsonify({'error': str(e)}), 400
    
    except (ValueError, KeyError, OSError) as e:
      return jsonify({'error': str(e)}), 400
    
    except Exception as e:
      return jsonify({'error': str(e)}), 400




if __name__ == "__main__":
  app.run(debug=True)
