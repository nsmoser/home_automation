from flask import Flask, render_template, redirect, url_for, request
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    deviceInfo = open('deviceStatus.txt','r+')
    if deviceInfo.read().find(',') == -1:
        deviceInfo.write('0,0,')
    deviceInfo.seek(0)
    devices = deviceInfo.read().split(',')
    devices.pop()
    for i in range(len(devices)):
        print(devices[i])
    deviceInfo.close()
    return render_template('welcome.html', room1 = int(devices[0]), room2 = int(devices[1]))
    
@app.route('/handler', methods = ['POST','GET'])
def handler():
    if request.method == 'POST':
        result = list(request.form.listvalues())
        action = result[0][0]
        deviceInfo = open('deviceStatus.txt','r+')
        device = deviceInfo.read().split(',')
        if action.find('tog1') != -1:
            print("toggle 1 occurring")
            if device[0] == '0':
                deviceInfo.seek(0)
                deviceInfo.write('1'+','+device[1]+',')
                deviceInfo.truncate()
            else:
                deviceInfo.seek(0)
                deviceInfo.write('0'+','+device[1]+',')
                deviceInfo.truncate()
        if action.find('tog2') != -1:
            print("toggle 2 occurring")
            if device[1] == '0':
                deviceInfo.seek(0)
                deviceInfo.write(device[0]+','+'1'+',')
                deviceInfo.truncate()
            else:
                deviceInfo.seek(0)
                deviceInfo.write(device[0]+','+'0'+',')
                deviceInfo.truncate()
        deviceInfo.close()
        return redirect(url_for('index'))
    
    
if __name__ == '__main__':
    socketio.run(app, port=80, host='0.0.0.0')
