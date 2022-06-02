#include <ESP8266WiFi.h>
#include "Adafruit_MQTT.h"
#include "Adafruit_MQTT_Client.h"

//Info for connecting to wifi
#define WIFI_SSID  ""
#define WIFI_PWD  ""

//Info for connecting to MQTT server
//Username and password are not necessary
#define MQTT_SERVER  ""
#define MQTT_SERVERPORT  1883
#define MQTT_USERNAME  ""
#define MQTT_PASSWORD  ""

//Define pin to be used with toggle button
//Pin should be high by default; ESP8266 doesn't start when pin is pulled low by default
#define TOGGLE_BUTTON 2

//Create object for interacting with wifi
WiFiClient client;

//Create objects for MQTT
//Creates MQTT object, publishing object, and subscribing object
//publishing object is topic to be publish to
//subscribing object is topic to be subscribed to
Adafruit_MQTT_Client mqtt(&client, MQTT_SERVER, MQTT_SERVERPORT, MQTT_USERNAME, MQTT_PASSWORD);
Adafruit_MQTT_Publish lightStatPub = Adafruit_MQTT_Publish(&mqtt, "room1/handler");
Adafruit_MQTT_Subscribe lightStatSub = Adafruit_MQTT_Subscribe(&mqtt, "room1/light");

//Function used to connect to MQTT server=
//Usually called on startup or upon disconnect
void MQTT_connect();

//Interrupt handler for button press
//Button press published a toggle instruction to room handler topic
ICACHE_RAM_ATTR void buttonHandler(){
  Serial.println("Button pressed");
  //publish instruction to topic using object created before startup
  lightStatPub.publish("togLight");
}

void setup() {
  //Set up serial for debugging
  Serial.begin(115200);
  //set toggle button pin as input
  pinMode(TOGGLE_BUTTON, INPUT);
  delay(10);
  Serial.println();

  //Connect to wifi
  WiFi.begin(WIFI_SSID,WIFI_PWD);

  Serial.print("Connecting...");

  //hang until wifi is connected
  while(WiFi.status() != WL_CONNECTED){
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  //give ip address
  Serial.print("Connected, IP address: ");
  Serial.println(WiFi.localIP());
  //subscribe to topic using object created before setup
  mqtt.subscribe(&lightStatSub);
  //attach button handler interrupt to falling edge events on toggle button pin
  attachInterrupt(digitalPinToInterrupt(TOGGLE_BUTTON), buttonHandler, FALLING);
}

void loop() {
  //call MQTT connect function in case of disconnect
  MQTT_connect();
  //Check is anything has been published to subscribed topic
  Adafruit_MQTT_Subscribe *subscription;
  //wait for instruction to be published to topic for 20 seconds before pinging
  while ((subscription = mqtt.readSubscription(20000))){
    //if something has been published
    if (subscription == &lightStatSub){
      //print published instruction
      Serial.print(F("Got: "));
      Serial.println((char *)lightStatSub.lastread);
    }
  }
  //if no ping is received
  if(! mqtt.ping()){
    //disconnect from MQTT broker
    mqtt.disconnect();
  }
}

//Function for forcing connection to MQTT broker
void MQTT_connect(){
  int8_t ret;
  //if already connected to the broker
  if(mqtt.connected()){
    //leave the function
    return;
  }
  Serial.print("Connecting to MQTT");
  //number of tries to reconnect
  uint8_t retries = 3;
  //if reconnect has failed
  while ((ret = mqtt.connect()) != 0){
    Serial.println(mqtt.connectErrorString(ret));
    Serial.println("Retrying MQTT connection in 5 seconds.");
    //force a disconnect
    mqtt.disconnect();
    //wait five seconds before reconnecting
    delay(5000);
    //decrement number of connection tries
    retries--;
    //if connection has failed set number of times
    if (retries == 0){
      //cause device to hang
      while(1);
    }
  }
  Serial.println("MQTT Connected");
  //request current state after connected
  lightStatPub.publish("startup");
}
