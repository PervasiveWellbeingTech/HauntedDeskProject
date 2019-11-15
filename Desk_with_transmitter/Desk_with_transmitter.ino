// Library for desk // 
#include "OneButton.h"
#include <Pushbutton.h>
#include <NewPing.h>
#include <microsmooth.h>
#include <autotune.h>
#include <Chrono.h>
#include <LightChrono.h>
#include <Wire.h>
#include <Adafruit_MLX90614.h>

// Library for transmitter //

#include <SPI.h>
#include <SD.h>
#include <nRF24L01.h>
#include <RF24.h>


/* ******************************************** VARIABLES FOR THE TRANSMITTER ***************************************** */

RF24 radio(10, 9); // CE, CSN

//const uint64_t pipes[2] = {0x1DECAF0001LL, 0x2DECAF0001LL}; // receiver and sender
const uint64_t pipes[2] = {0x1DECAF0000LL, 0x2DECAF0000LL}; // receiver and sender

// Variables for sd card logger
const bool debugMode = 1;
const int chipSelect = PD7;
const String goodCommand = "data";
int year = 19;
int month = 11;
int day = 29;
int hour = 23;

int J;

String fileName;
String oldFileName;
File dataFile;


/* *********************************************** VARIABLES FOR THE DESK ************************************************ */

//CHANGE THESE VALUES
int short_height = 67;
int tall_height = 106;
bool use_thermal = true;
bool remember_heights = true;
#define CHANGE_TIME 30 //__ times 60 seconds
//CHANGE THESE VALUES

//Pins for Ultrasonic Sensor
#define TRIGGER_PIN  7
#define ECHO_PIN     6
#define MAX_DISTANCE 200

//Pins for buttons/desk movement
#define UP_BUTTON_PIN 5
#define DOWN_BUTTON_PIN 4
#define MOTOR_UP_PIN 3
#define MOTOR_DOWN_PIN 2


//Height and time tolerances/presettings
#define tolerance 1
#define short_delay_time 50
int prev_height = 0;
int set_new_height_time = 10;
int timeOutTime = 15;
bool snooze = false;
bool pres;

Adafruit_MLX90614 mlx = Adafruit_MLX90614();

// Setup a new OneButton for user up.
OneButton up_button(UP_BUTTON_PIN, true);
// Setup a new OneButton for user down.
OneButton down_button(DOWN_BUTTON_PIN, true);

//Initialize timer for automatic height changes
Chrono changeTimer(Chrono::SECONDS);
Chrono timeOut(Chrono::SECONDS);
Chrono heightChangeTimer(Chrono::SECONDS);

// Initialize chrono for logging Data
Chrono presTimer(Chrono::SECONDS);




//Initialize the ultrasonic sensor
NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE);
uint16_t *history = ms_init(SGA);

/* ************************************************* END OF DESK VARIABLES ************************************************ */

/* *********************************************** BEGINNING OF TRANSMITTER FUNCTIONS ****************************************** */

String getDateTime() {
  hour++;
  return String(year) + String(month) + String(day) + String(hour);
}


void debug(String content) {
  if (debugMode) {
    Serial.println(content);
  }
}

void logData(String data,Chrono & chrono,float logging_time){

  if(dataFile){
    

    if(chrono.hasPassed(logging_time,false)){
          debug(F("Logging"));

          dataFile.println(data);
          chrono.restart(0);

    }
  }
  else{
    debug(F("Unable to open the dataFile, something in the code went wrong"));
  }

  
}


void cout(String content) {
  char charContent[33] = {0};
  content.toCharArray(charContent, sizeof(charContent));
  if (radio.write(&charContent, sizeof(charContent))) {
    debug(F("Sucess"));
  } else {
    debug(F("Failure for packet ")); debug(String(charContent));
  }
  //Serial.print(content);


}

bool rf24SendR(String content, int retries) {
  char charContent[33] = {0};
  int trial = 0;
  content.toCharArray(charContent, sizeof(charContent));
  while (trial < retries) {

    if (radio.write(&charContent, sizeof(charContent))) {
      debug(F("Success for packet: "));debug(String(charContent));
      trial = retries; // just in case
      return true;

    } else {
      trial++;
      debug("Failure for packet: " + String(charContent));
    }
    //Serial.print(content);

  }
  return false; /// if the loop exit we return false


}

bool validateResponse(String toValidate, unsigned long maxTime) {
  radioSetup();
  radio.startListening();
  bool validated = false;
  unsigned long time = millis();
  while (!validated && ((millis() - time) < maxTime)) {

    if (radio.available()) {

      char text[33] = {0} ;   // set incmng message for 32 bytes
      radio.read(&text, sizeof(text));    //Reading the data
      String command = String(text);
      debug(String(command));

      if (command == toValidate) {
        validated = true;
        radio.stopListening();

        return validated;
      }
    } else {
      
      //debug(F("Radio is not available "));
    }


  }

  return validated;

}

bool sendFilenameSize(String locFileName) {

  File dataTransfertFile = SD.open(locFileName, FILE_READ);
  if (dataTransfertFile) {
    debug(F("File opened and ready for transfert"));
    debug("File size is: " + String(dataTransfertFile.size()) + " bytes");
    String fz = String(dataTransfertFile.size());
    //String currentChar = String(char(dataTransfertFile.read()));
    dataTransfertFile.close();

    radioSetup();


    if (rf24SendR(locFileName, 2)) {
      debug(F("Filename has been send"));
    }
    else {
      debug(F("Fail to send filename,  waiting for another data query"));
      return false;
    };
    if (rf24SendR(fz, 2)) {
      debug(F("Filesize has been send"));
    } else {
      debug(F("Fail to send filesize,  waiting for another data query"));
      return false;
    };


    if (validateResponse("ok", 3000)) {
      debug(F("File Name and size has been acknowledge, ready to proceed file transfer"));
      return true;
    }
    else {
      debug(F("File Name and size has NOT been acknowledge, waiting for another data query"));
      return false;
    }
  }

  else {
    debug(F("Impossible to open the file,waiting for another data query"));return false;
  }
}


void startDataTransfert(String locFileName) {
  readTransfer32B(locFileName);
  rf24SendR("eof",4);
}

void readTransfer32B(String locFileName) { //File myFile){
  char   bufferr[33];     // read buffer
  uint8_t i = 0;         // buffer index to 0
  int pos = 1;
  File myFile = SD.open(locFileName, FILE_READ);
  myFile.seek(pos);
  int8_t c = myFile.read();   // read first character

  
  while (c != -1) {     // As long as there is no eof
    //debug("Pos "+String(myFile.position()));
    bufferr[i] = c;      // character in the transmit buffer
    i++;

    if (i == 32) {
      //
      // buffer full
      pos = myFile.position();
      //debug("The position is now "+String(pos));
      myFile.close();
      //digitalWrite(chipSelect, HIGH);

      radioSetup();
      //String bufferrr = "abcdefghijklmnopqrstuvwxyz123456";
      rf24SendR(bufferr, 100);
      //cout(bufferr);
      //debug("A packet of size "+String(sizeof(bufferr))+" has been send." );
      Serial.print(String(bufferr));

      myFile = SD.open(locFileName, FILE_READ);
      //debug("Newly opened file position "+String(myFile.position()));
      myFile.seek(pos);

      //debug("File position after seek "+String(myFile.position()));

      i = 0;
    }
    //
    // next read
    //

    c = myFile.read();
    if (c == -1 && i != 0) {
      debug(F("                                                       ENDING TRASNMISSIONNNNNNNN                                                            "));
      Serial.print(String(c));
      cout(bufferr); // putting out the last bytes of data
      myFile.close(); // closing the file

    }

  }


}
void radioSetup() {

  radio.begin();                  //Starting the Wireless communication
  radio.setChannel(0x76) ;            // set chanel at 76
  //radio.enableDynamicPayloads() ;
  radio.enableAckPayload();               // not used here
  radio.setRetries(0, 125);                // Smallest time between retries, max no. of retries
  radio.setAutoAck( true ) ;

  radio.openWritingPipe(pipes[1]); //Setting the address where we will send the data
  radio.openReadingPipe(1, pipes[0]);   //Setting the address at which we will receive the data

  radio.setPALevel(RF24_PA_MAX);  //You can set it as minimum or maximum depending on the distance between the transmitter and receiver.
  radio.setDataRate(RF24_1MBPS);
  radio.stopListening();          //This sets the module as transmitter
  

}

void listenToPI(){
  /// this must be replace by a time
      debug(F("Good command:"));
      dataFile.close();
      debug("  - current dataFile " + fileName + " closed");
      oldFileName = fileName; // backup the filename

      unsigned long time = millis();
      unsigned long maxTime  = 18000000; // eq 5 hours in millis
      while ((millis()-time)<maxTime) {
        if (validateResponse("data",3000)) {
          if (sendFilenameSize(oldFileName)) {
            debug(F("Handshake for sending file name and size has been sucessfull"));

            startDataTransfert(oldFileName);
            fileName = getDateTime() + ".txt";
            SD.remove(fileName);
            dataFile = SD.open(fileName, FILE_WRITE);
            debug("  - new dataFile " + fileName + " opened.");
            return;
          }
          else {
            debug(F("Handshake for sending file name and size has FAILED"));
          }


        }else{
         String time_left = String( (maxTime-(millis()-time))/1000);
         debug(("Data command has not been received trying again for: "+ time_left+ " seconds"));
          }
        
      }
}

void setupSD(){
  J=0;
    debug(F("Initializing SD card..."));
  pinMode(chipSelect, OUTPUT);

  // see if the card is present and can be initialized:
  if (!SD.begin(chipSelect)) {
    debug(F("Card failed, or not present"));
    // don't do anything more:
    while (1);
  }
  debug(F("Card initialized."));
  fileName = getDateTime() + ".txt";
  dataFile = SD.open(fileName, FILE_WRITE);
  if (dataFile) {
    debug("dataFile " + fileName + " opened.");
  } else {
    debug(F("ERROR: dataFile not opened."));
  }
}

/* *********************************************** BEGINNING of DESK FUNCTIONS ************************************************ */


// Return the distance in cm from the ultrasonic sensor
int getDistance(int trigPin, int echoPin) // returns the distance (cm)
{
  long duration, distance;
  digitalWrite(trigPin, HIGH); // We send a 10us pulse
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  duration = pulseIn(echoPin, HIGH, 20000); // We wait for the echo to come back, with a timeout of 20ms, which corresponds approximately to 3m
  // pulseIn will only return 0 if it timed out. (or if echoPin was already to 1, but it should not happen)
  if (duration == 0) // If we timed out
  {
    pinMode(echoPin, OUTPUT); // Then we set echo pin to output mode
    digitalWrite(echoPin, LOW); // We send a LOW pulse to the echo pin
    delayMicroseconds(200);
    pinMode(echoPin, INPUT); // And finaly we come back to input mode
  }
  distance = (duration / 2) / 29.1; // We calculate the distance (sound speed in air is aprox. 291m/s), /2 because of the pulse going and coming
  return distance; //We return the result. Here you can find a 0 if we timed out
}

//Processes the height from the ultrasonic sensor
int get_height_cm() {
  int current_height_cm = getDistance (TRIGGER_PIN, ECHO_PIN);
  //int current_height_cm = sonar.ping_cm();
  int processed_value = sma_filter(current_height_cm, history);
  return  processed_value;
  //return current_height_cm;
}

//Sets desk motor to move up
void raise_up() {
  digitalWrite(MOTOR_UP_PIN, HIGH);
}

//Sets desk motor to move down
void lower() {
  digitalWrite(MOTOR_DOWN_PIN, HIGH);
}

//Stops the desk motor
void stop_desk() {
  digitalWrite(MOTOR_UP_PIN, LOW);
  digitalWrite(MOTOR_DOWN_PIN, LOW);
}

//Sets the height of the desk to the given height
void set_desk_height(int height_in_cm) {
  int current_height_cm = get_height_cm();
  timeOut.restart(0);
  if (current_height_cm < height_in_cm - tolerance) {
    raise_up();
    while (current_height_cm < height_in_cm - tolerance && !timeOut.hasPassed(timeOutTime, false) && !snooze) {
      debug(String(current_height_cm));
      current_height_cm = get_height_cm();
    }
  }
  else {
    lower();
    while (current_height_cm > height_in_cm + tolerance && !timeOut.hasPassed(timeOutTime, false) && !snooze) {
      debug(String(current_height_cm));
      current_height_cm = get_height_cm();
    }
  }
  snooze = false;
  stop_desk();
}

void setPinModes() {
  pinMode(MOTOR_DOWN_PIN, OUTPUT);
  pinMode(MOTOR_UP_PIN, OUTPUT);

  pinMode(TRIGGER_PIN, OUTPUT);
  pinMode(ECHO_PIN, OUTPUT);
}

void linkButtons() {
  // link the up button functions.
  up_button.attachLongPressStart(up_longPressStart);
  up_button.attachLongPressStop(up_longPressStop);

  // link the down button functions.
  down_button.attachLongPressStart(down_longPressStart);
  down_button.attachLongPressStop(down_longPressStop);
}



//Called to automatically set the desk height to change from down to up or vice versa
//Depends on where the desk is when called (aka, responds to user changes)
void switchPosition() {
  if (get_height_cm() <= (tall_height + short_height) / 2) {
    debug(F("MOVING UP - AUTOMATIC")); 
    set_desk_height(tall_height);
  }
  else {
    debug(F("MOVING DOWN - AUTOMATIC"));
    set_desk_height(short_height);
  }
  stop_desk();
}

void changePresets() {
  int current_height_cm = get_height_cm();
  if (prev_height == current_height_cm || prev_height == current_height_cm + 1 || prev_height == current_height_cm - 1) {
    if (heightChangeTimer.hasPassed(set_new_height_time, false)) {
      heightChangeTimer.restart(0);
      if (current_height_cm > (tall_height + short_height) / 2) {
        debug(F("Tall Height Change"));
        tall_height = current_height_cm;
      } else {
        debug(F("Short Height Change"));
        short_height = current_height_cm;
      }
    }
  } else {
    heightChangeTimer.restart(0);
  }
  prev_height = current_height_cm;
}

void checkPresent() {
  
  double ambtemp = mlx.readAmbientTempC(); 
  double objtemp = mlx.readObjectTempC();
  if(objtemp > ambtemp + 0.45) {
    debug(F(", Present Thermal"));
    pres = true;
  } else {
    J++;
    //debug(", Not Present Thermal " + String(J));
    logData("Not present thermal"+ String(J),presTimer,0.2);
    

    pres = false;
  }
}

void checkButtons() {
  up_button.tick();
  down_button.tick();
}

void checkPresentAndMovement() {
  if (changeTimer.hasPassed(CHANGE_TIME, false)) {
    changeTimer.restart(0);
    if (pres) switchPosition();
  }
  if (remember_heights) changePresets();
  if (use_thermal) checkPresent();
  if (!use_thermal); //Serial.println();
}



// This function will be called once, when the up button is pressed for a long time.
void up_longPressStart() {
  debug(F("User Up longPress start"));
  raise_up();
} 


// This function will be called once, when the up button is released after beeing pressed for a long time.
void up_longPressStop() {
  debug(F("User Up longPress stop"));
  stop_desk();
} 


// This function will be called once, when the down button is pressed for a long time.
void down_longPressStart() {
  debug(F("User Down longPress start"));
  lower();
} 


// This function will be called once, when the down button is released after beeing pressed for a long time.
void down_longPressStop() {
  debug(F("User Down longPress stop"));
  stop_desk();
} 



/* *********************************************** END OF DESK FUNCTIONS ************************************************ */

/* *********************************************** MAIN LOOPS ************************************************ */

void setup() {
  mlx.begin();
  Serial.begin(9600);
  setPinModes();
  pres = true;
  linkButtons();
  setupSD();
}

void loop() {
  snooze = false;
  //Serial.print(get_height_cm());
  checkButtons();
  checkPresentAndMovement();

    // open the file. note that only one file can be open at a time,
  // so you have to close this one before opening another.
  if (Serial.available()) { /// this needs to be replace with a code that triggers at one time 
    debug(F("Command received: "));
    String command = Serial.readString();
    debug(command);

    if (command == goodCommand) { 
      listenToPI();


    } else {
      debug(F("WARNING: bad command."));
    }
  }


  
}
