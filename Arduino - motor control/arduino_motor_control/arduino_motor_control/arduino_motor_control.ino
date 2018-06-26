/*
  Roman Oechslin
  Robot controller with haptic feedback
  2018/04/06  Tokyo
*/
#define FASTADC 1

// defines for setting and clearing register bits
#ifndef cbi
#define cbi(sfr, bit) (_SFR_BYTE(sfr) &= ~_BV(bit))
#endif
#ifndef sbi
#define sbi(sfr, bit) (_SFR_BYTE(sfr) |= _BV(bit))
#endif

#define joystick_left_pin A0
#define photo_left_pin A2
#define joystick_right_pin A1
#define photo_right_pin A3
int motorPinLowGain = 3;    // Motor connected to digital pin 3 (PWM)
int motorPinHighGain = 11;    // Motor connected to digital pin 11 (PWM)
int testPin = 13; // Used for testing the speed of Arduino

int dist_ref = 0;
float FILTER_CST = 0.5;
int OUTPUT_PER_VOLT = 255/5; // the arduino can output 5V max
int MOTOR_MAX_VOLTAGE = 20; // change this according to motor
int LEFT_HAND_AMPLIFIER_GAIN = 10;
int RIGHT_HAND_AMPLIFIER_GAIN = 10;
const int OUTPUT_RANGE_L = 2 * MOTOR_MAX_VOLTAGE * OUTPUT_PER_VOLT / LEFT_HAND_AMPLIFIER_GAIN;
const int OUTPUT_RANGE_R = 2 * MOTOR_MAX_VOLTAGE * OUTPUT_PER_VOLT / RIGHT_HAND_AMPLIFIER_GAIN;

int error_left = 0;
int last_error_left = 0;
float sum_error_left = 0;
int error_right = 0;
int last_error_right = 0;
float sum_error_right = 0;
const int PHOTO_MIN_LEFT = 650;
const int PHOTO_MAX_LEFT = 830;
const int PHOTO_MIN_RIGHT = 700;
const int PHOTO_MAX_RIGHT = 870;
const int MAX_DISPLACEMENT_UM = 1800; // [um], has been measured

unsigned long TIME_BEGIN = 0;
unsigned long TIME_NOW = 0;
unsigned long TIME_CYCLE = 1000; // this is the time_step in [microseconds] that determines the running frequency


void setup() {
  Serial.begin(250000);
  pinMode(motorPinLowGain, OUTPUT);
  pinMode(motorPinHighGain, OUTPUT);
  
  pinMode(joystick_left_pin, INPUT);
  pinMode(photo_left_pin, INPUT);
  pinMode(joystick_right_pin, INPUT);
  pinMode(photo_right_pin, INPUT);
  pinMode(testPin, OUTPUT);

  TCCR2B = TCCR2B & B11111000 | B00000001; // for PWM frequency of 31372.55 Hz
  #if FASTADC
  // set prescale to 16
  sbi(ADCSRA, ADPS2) ;
  cbi(ADCSRA, ADPS1) ;
  cbi(ADCSRA, ADPS0) ;
  #endif
}

void loop() {
  digitalWrite(testPin, HIGH); // this is only used to measure the operating frequency
  TIME_BEGIN = micros();
  
  int joy_val_left = analogRead(joystick_left_pin);
  joy_val_left = joy_val_left>>2; // the joystick value is [0..1023] and I want to convert it to 8bit
  int joy_val_right = analogRead(joystick_right_pin);
  joy_val_right = joy_val_right>>2; // the joystick value is [0..1023] and I want to convert it to 8bit

  int photo_value_left = analogRead(photo_left_pin);
  int photo_value_right = analogRead(photo_right_pin);
    
  int pwmValueLeftSym = 128;
  int pwmValueRightSym = 128;
  

  float k_p = 0.2; // k_p = 1; and k_i = 0.01; works as well
  float k_i = 0.0;
  float k_d = 0.0;

  //Writing to Processing file
  Serial.write(joy_val_left);
  Serial.write(joy_val_right); 
  Serial.write((joy_val_left + joy_val_right)%256); // this is the checksum
  //Serial.println(joy_val_right);// for debugging purposes in serial monitor mode
  if (Serial.available() > 0) {
    dist_ref = (int)(FILTER_CST*dist_ref + (1-FILTER_CST)* Serial.read());
  } else {
    dist_ref = 0.99*dist_ref;// FIXME tune this param
  }
  error_left = dist_ref - sensor2dist(photo_value_left_raw, PHOTO_MIN_LEFT, PHOTO_MAX_LEFT);
  error_right = dist_ref - sensor2dist(photo_value_right_raw, PHOTO_MIN_RIGHT, PHOTO_MAX_RIGHT);
      
  int motor_output_left = k_p * error_left + k_i * sum_error_left + k_d * (error_left - last_error_left);
  int motor_output_right =  k_p * error_right + k_i * sum_error_right + k_d * (error_right - last_error_right);//FIXME need two different control parameters?
  sum_error_left = error_left + sum_error_left;
  last_error_left = error_left;
  sum_error_right = error_right + sum_error_right;
  last_error_right = error_right;
  // symmetric feedback left and right, (allowing for negative motor values)
  pwmValueLeftSym = pid2pwm_sym(des_mot_volt_left, OUTPUT_RANGE_L);
  pwmValueRightSym = pid2pwm_sym(des_mot_volt_right, OUTPUT_RANGE_R);

  analogWrite(motorPinLowGain, pwmValueLeftSym);//pwmValueLeftSym
  analogWrite(motorPinHighGain, pwmValueRightSym); //pwmValueRightSym
 
  while ((micros() - TIME_BEGIN) < TIME_CYCLE) {  } // do nothing until we reach the time step of TIME_CYCLE
  digitalWrite(testPin, LOW); //instructions in between take roughly 640 microseconds
}

int sensor2dist(int sensor_value, int min_val, int max_val) {
  // maps the measured value to the distance (assumed linearity) in micrometers
  return MAX_DISPLACEMENT_UM - (sensor_value - min_val) * (MAX_DISPLACEMENT_UM /15) / (max_val - min_val) * 15;
}


int limit_value(int value, int lower, int upper) {
  if (value < lower) {
    value = lower;
  } else if (value > upper) {
    value = upper;
  }
  return value;
}

int pid2pwm_sym(int des_voltage, int range) {
  // converts motor voltage to pwm output where 128-range/2 is full power in one direction and 128+range/2 is 
  // full power in the other
  return limit_value(des_voltage, -range/2, range/2) + 128;
}

