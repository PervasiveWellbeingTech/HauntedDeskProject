#include "OneButton.h"
#include <Pushbutton.h>
#include <NewPing.h>
#include <microsmooth.h>
#include <autotune.h>
#include <Chrono.h>
#include <LightChrono.h>
#include <Wire.h>
#include <Adafruit_MLX90614.h>

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
//Initialize the ultrasonic sensor
NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE);
uint16_t *history = ms_init(SGA);

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
      Serial.println(current_height_cm);
      current_height_cm = get_height_cm();
    }
  }
  else {
    lower();
    while (current_height_cm > height_in_cm + tolerance && !timeOut.hasPassed(timeOutTime, false) && !snooze) {
      Serial.println(current_height_cm);
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

void setup() {
  mlx.begin();
  Serial.begin(9600);
  setPinModes();
  pres = true;
  linkButtons();
}

//Called to automatically set the desk height to change from down to up or vice versa
//Depends on where the desk is when called (aka, responds to user changes)
void switchPosition() {
  if (get_height_cm() <= (tall_height + short_height) / 2) {
    Serial.println(F("MOVING UP - AUTOMATIC")); 
    set_desk_height(tall_height);
  }
  else {
    Serial.println(F("MOVING DOWN - AUTOMATIC"));
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
        Serial.println(F("Tall Height Change"));
        tall_height = current_height_cm;
      } else {
        Serial.println(F("Short Height Change"));
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
    Serial.println(F(", Present Thermal"));
    pres = true;
  } else {
    Serial.println(F(", Not Present Thermal"));
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
  if (!use_thermal) Serial.println();
}

void loop() {
  snooze = false;
  Serial.print(get_height_cm());
  checkButtons();
  checkPresentAndMovement();
}

// This function will be called once, when the up button is pressed for a long time.
void up_longPressStart() {
  Serial.println(F("User Up longPress start"));
  raise_up();
} 


// This function will be called once, when the up button is released after beeing pressed for a long time.
void up_longPressStop() {
  Serial.println(F("User Up longPress stop"));
  stop_desk();
} 


// This function will be called once, when the down button is pressed for a long time.
void down_longPressStart() {
  Serial.println(F("User Down longPress start"));
  lower();
} 


// This function will be called once, when the down button is released after beeing pressed for a long time.
void down_longPressStop() {
  Serial.println(F("User Down longPress stop"));
  stop_desk();
} 
