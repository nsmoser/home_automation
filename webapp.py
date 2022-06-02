from flask import Flask, render_template, redirect, url_for, request
from flask_mqtt import Mqtt

app = Flask(__name__)
#Make Flask app object

app.config['MQTT_BROKER_URL'] = '127.0.0.1'
#MQTT broker runs on device, so use the loopback IP
app.config['MQTT_BROKER_PORT'] = 1883
#Default MQTT Port
app.config['MQTT_USERNAME'] = ''
#No username necessary for this implementation
app.config['MQTT_PASSWORD'] = ''
#No password necessary for this implementation
app.config['MQTT_KEEPALIVE'] = 120
#Set keepalive ping to 2 minutes, can be changed if needed
app.config['MQTT_TLS_ENABLED'] = False
#No TLS

mqtt = Mqtt(app)
#Make MQTT Object

#When the site first starts and connects to the MQTT Broker
@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
        mqtt.subscribe('room1/handler')
        #Subscribe to the room 1 handler
        print('subscribed to room 1')
        mqtt.subscribe('room2/handler')
        #Subscribe to the room 2 handler
        print('subscribed to room 2')

#When the site receives a published message from a subscribed topic
@mqtt.on_message()
def mqtt_message_handler(client, userdata, message):
        topic = message.topic
        #Get topic of instruction
        instruction = message.payload.decode()
        #Get instruction published to topic
        print(topic+' '+instruction)
        deviceInfo = open('deviceStatus.txt','r+')
        #Open backend file which holds states of all lights
        deviceInfo.seek(0)
        devices = deviceInfo.read().split(',')
        #Break room states into individual rooms
        devices.pop()
        #Drop last room due to the way split() works
        if topic.find('handler') != -1:
        #If the instruction requires a handler for any room
                if instruction.find('togLight') != -1:
                #If a light is to be toggled
                        if topic.find('room1') != -1:
                        #If a light in room 1 is to be toggled
                                if devices[0] == '0':
                                #If the light in room 1 is off
                                        mqtt.publish('room1/light','on')
                                        #Publish an on instruction to room 1 light
                                        deviceInfo.seek(0)
                                        deviceInfo.write('1'+','+devices[1]+',')
                                        #Update backend file
                                if devices[0] == '1':
                                #If the light in room 1 is on
                                        mqtt.publish('room1/light','off')
                                        #Publish an off instruction to room 1 light
                                        deviceInfo.seek(0)
                                        deviceInfo.write('0'+','+devices[1]+',')
                                        #Update backend file
                        if topic.find('room2') != -1:
                        #If a light in room 2 is to be toggled
                                if devices[1] == '0':
                                #If the light in room 2 is off
                                        mqtt.publish('room2/light','on')
                                        #Publish an on instruction to room 2 light
                                        deviceInfo.seek(0)
                                        deviceInfo.write(devices[0]+','+'1'+',')
                                        #Update backend file
                                if devices[1] == '1':
                                #If the light in room 2 is on
                                        mqtt.publish('room2/light','off')
                                        #Publish an off instruction to room 2 light
                                        deviceInfo.seek(0)
                                        deviceInfo.write(devices[0]+','+'0'+',')
                                        #Update backend file
                if instruction.find('startup') != -1:
                #If a device has just connected to the MQTT broker
                #Devices do not retain state or update on power off, so this updates on startup
                        if topic.find('room1') != -1:
                        #If the room 1 device just connected
                                if devices[0] == '0':
                                #If room 1 is supposed to be turned off on startup
                                        mqtt.publish('room1/light','off')
                                        #Publish an off instruction to room 1 light
                                if devices[0] == '1':
                                #If room 1 is supposed to be turn on on startup
                                        mqtt.publish('room1/light','on')
                                        #Publish an on instruction to room 1 light
                        if topic.find('room2') != -1:
                        #If the room 2 light just connected
                                if devices[1] == '0':
                                #If room 2 is supposed to be turned off on startup
                                        mqtt.publish('room2/light','off')
                                        #Publish an off instruction to room 2 light
                                if devices[1] == '1':
                                #If room 2 is supposed to be turned on on startup
                                        mqtt.publish('room2/light','on')
                                        #Publish an on instruction to room 2 light
        deviceInfo.close()
        #Close backend file

#Default route when client connects to server
#Loads on connect or refresh
@app.route('/')
def index():
        deviceInfo = open('deviceStatus.txt','r+')
        #Open backend file which keeps track of light states
        if deviceInfo.read().find(',') == -1:
        #If the backend file does not have any light states
                deviceInfo.write('0,0,')
                #Write both states as off
        deviceInfo.seek(0)
        #Return cursor in file to zero
        devices = deviceInfo.read().split(',')
        #Break room states into individual rooms
        devices.pop()
        #Drop last room due to the way split() works
        for i in range(len(devices)):
        #Print current device states for debugging
                print(devices[i])
        deviceInfo.close()
        #Close backend file
        return render_template('welcome.html', room1 = int(devices[0]), room2 = int(devices[1]))
        #Handoff room state info to welcome site and display site for user

#Route for handling button presses on website
#Only works when button posts to /handler route
@app.route('/handler', methods = ['POST','GET'])
def handler():
        if request.method == 'POST':
        #If the handler route is accessed via post
                result = list(request.form.listvalues())
                #Get info posted to handler route
                action = result[0][0]
                #Parse info for use in toggling
                if action.find('tog1') != -1:
                #If room 1 is to be toggled
                        print("toggle 1 occurring")
                        mqtt.publish('room1/handler','togLight')
                        #Publish a light toggle instruction to room 1 handler topic
                if action.find('tog2') != -1:
                #If room 2 is to be toggled
                        print("toggle 2 occurring")
                        mqtt.publish('room2/handler','togLight')
                        #Publish a light toggle instruction to room 2 handler topic
                return redirect(url_for('index'))
                #Bring user back to default route

if __name__ == '__main__':
        app.run(host='0.0.0.0', port=5000)
        #Used to select host address and port
