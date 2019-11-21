#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
RF24 radio(10, 9); // CE, CSN
//const byte address[6] = "00001";
const uint64_t address = 0xF1F1F0F0E0LL;//0xE0E0F1F1E0LL; //
const uint64_t pipes[2] = {0xE0E0F1F1E0LL,0xF1F1F0F0E0LL};// receiver and sender

boolean button_state = 0;
int led_pin = 3;
void setup() {
pinMode(PD6, OUTPUT);
Serial.begin(9600);
radio.begin();
radio.setChannel(0x76) ;            // set chanel at 76

radio.openWritingPipe(pipes[1]); //Setting the address where we will send the data
radio.openReadingPipe(1, pipes[0]);   //Setting the address at which we will receive the data

radio.enableDynamicPayloads() ;
radio.enableAckPayload();               // not used here
radio.setRetries(6, 15);                // Smallest time between retries, max no. of retries
radio.setAutoAck( true ) ;
radio.setPALevel(RF24_PA_MAX);       //You can set this as minimum or maximum depending on the distance between the transmitter and receiver.

//radio.startListening();

}
void loop()
{
digitalWrite(PD6,HIGH);
if (radio.available())              //Looking for the data.
{
    Serial.println("Recieving message from pi");


char text[33] = {0} ;   // set incmng message for 32 bytes
radio.read(&text, sizeof(text));    //Reading the data
radio.stopListening();              //This sets the module as transmettor
delay(500);
Serial.println(text);


}

else{
      Serial.println("Sending message to pi");

  const char response[] = "Hello World";
  radio.write(&response, sizeof(response));
  radio.startListening();
}

delay(500);
} 
