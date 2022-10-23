#include <ESP8266WebServer.h> 
#include <ESP8266WiFi.h>

#define BUZZER 4
#define LIGHT1 5
#define LIGHT2 13
const char *ssid = "multimedia_komputer"; // Write your wifi ssid here 
const char *password = "mariusz7419";     // Write your wifi password here 

ESP8266WebServer server(80); 
 IPAddress local_IP(192, 168, 0, 9);
 IPAddress gateway(192, 168, 0, 1);
 IPAddress subnet(255, 255, 255, 224);

void stronaGlowna(){
   server.send(200, "text/html", "<h2>To jest strona główna</h2>");
}
void buzzerOn(){
   pinMode(BUZZER,OUTPUT);
   digitalWrite(BUZZER,LOW);
   server.send(200, "text/html", "<h2>Buzzer wlaczony <3 </h2>");
   delay(5000);
   buzzerOff();
}

void buzzerOff(){
   pinMode(BUZZER,OUTPUT);
   digitalWrite(BUZZER,HIGH);
   server.send(200, "text/html", "<h2>Buzzer wylaczona :)</h2>"); 

}
void flashAllertOn(){
   pinMode(LIGHT1,OUTPUT);
   digitalWrite(LIGHT1,HIGH);
   server.send(200, "text/html", "<h2>Flash 1 On ;)</h2>"); 
   delay(5000);
   flashAllertOff();
}

void flashAllertOff(){
   pinMode(LIGHT1,OUTPUT);
   digitalWrite(LIGHT1,LOW);
   server.send(200, "text/html", "<h2>Flash 1 Off ;)</h2>"); 
   
}

void flashAllertOn2(){
   pinMode(LIGHT2,OUTPUT);
   digitalWrite(LIGHT2,HIGH);
   server.send(200, "text/html", "<h2>Flash 2 On ;)</h2>"); 
   buzzerOn();
   delay(5000);
   flashAllertOff2();
   buzzerOff();
}
void flashAllertOff2(){
   pinMode(LIGHT2,OUTPUT);
   digitalWrite(LIGHT2,LOW);
   server.send(200, "text/html", "<h2>Flash 2 Off ;)</h2>"); 
}


void handleNotFound() { 
   String message = "Brak strony na serwerze...";
   server.send(404, "text/plain", message);
}

void setup(){
   server.on("/", stronaGlowna);
   server.on("/BuzzerOn", buzzerOn);
   server.on("/BuzzerOff", buzzerOff);
   server.on("/FlashOn", flashAllertOn);
   server.on("/FlashOff", flashAllertOff);
   server.on("/FlashOn2", flashAllertOn2);
   server.on("/FlashOff2", flashAllertOff2);
   server.onNotFound(handleNotFound);
   
    Serial.begin(115200);        
  delay(10);
  Serial.println('\n');

  WiFi.config(local_IP, subnet, gateway);
  WiFi.begin(ssid, password);            
  Serial.print("Connecting to ");
  Serial.print(ssid); Serial.println(" ...");

  int i = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(++i); Serial.print(' ');
  }

  Serial.println('\n');
  Serial.println("Connection established!");  
  Serial.print("IP address:\t");
  Serial.println(WiFi.localIP());
  server.begin();

}
void loop(){
   server.handleClient();
}  
