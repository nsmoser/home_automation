from machine import UART, Pin
import utime

def espSetup(espDevice):
    cwmode = '1'
    wifiSSID = '"testSSID"'
    wifiPWD = '"testPWD"'
    setup_phrases = ['AT+GMR','AT+CWMODE='+cwmode,'AT+CWJAP='+wifiSSID+','+wifiPWD]
    endcode = '\r\n'
    for i in range(len(setup_phrases)-1):
        espWrite(espDevice,str(setup_phrases[i]))
        utime.sleep(0.25)
    espDevice.write(str(setup_phrases[len(setup_phrases)-1])+endcode)
    utime.sleep(0.25)
    while espDevice.any():
        espResponse = str(espDevice.readline())
        espEndIndex = len(espResponse)
        print(espResponse[2:espEndIndex-5])
        if(espResponse.find('WIFI GOT IP') != -1):
            return 1
        else:
            utime.sleep(5)


def espWrite(espDevice,phrase):
    endcode = '\r\n'
    espDevice.write(str(phrase)+endcode)
    utime.sleep(0.25)
    while espDevice.any():
        espResponse = str(espDevice.readline())
        espEndIndex = len(espResponse)
        print(espResponse[2:espEndIndex-5])
    if(espResponse.find('OK') != -1):
        return 1
    else:
        return 0

        
espDevice = UART(0, baudrate=115200, tx=Pin(0), rx = Pin(1), timeout = 2)

if espSetup(espDevice) != 1:
    print("ope. setup failed")
    exit()
    
while True:
    print(espWrite(espDevice,'AT'))
    utime.sleep(2)