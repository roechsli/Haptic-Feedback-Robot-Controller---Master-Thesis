/*
  Roman Oechslin
  Robot controller with haptic feedback
  2018/08/07  Tokyo
  Version 1.0
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
int motorPinLeft = 3;    // Motor connected to digital pin 3 (PWM)
int motorPinRight = 11;    // Motor connected to digital pin 11 (PWM)

float dist_ref = 0.0;
float FILTER_CST = 0.5; // filter when reading new feedback value
int OUTPUT_PER_VOLT = 255/5; // the arduino can output 5V max
int MOTOR_MAX_VOLTAGE = 20; // change this according to motor
int LEFT_HAND_AMPLIFIER_GAIN = 10;
int RIGHT_HAND_AMPLIFIER_GAIN = 10;
const int OUTPUT_RANGE_L = 2 * MOTOR_MAX_VOLTAGE * OUTPUT_PER_VOLT / LEFT_HAND_AMPLIFIER_GAIN;
const int OUTPUT_RANGE_R = 2 * MOTOR_MAX_VOLTAGE * OUTPUT_PER_VOLT / RIGHT_HAND_AMPLIFIER_GAIN;

float error_left = 0.0;
float error_left_last = 0.0;
float sum_error_left = 0.0;
float numerator_l_last_f = 0.0;
float error_right = 0.0;
float error_right_last = 0.0;
float sum_error_right = 0.0;
float numerator_r_last_f = 0.0;
float dT = 0.001;
float filter_coeff = 0.05; // filter on derivative part

int photo_value_left_raw = 0;
int photo_value_right_raw = 0;

const int PHOTO_MIN_LEFT = 640;
const int PHOTO_MAX_LEFT = 840;
const int PHOTO_MIN_RIGHT = 700;
const int PHOTO_MAX_RIGHT = 880;
const float MAX_DISPLACEMENT_MM = 1.8; // [mm], has been measured

// If Yoke controller is used:
/*
const int PHOTO_MIN_LEFT = 550;
const int PHOTO_MAX_LEFT = 780;
const int PHOTO_MIN_RIGHT = 600;
const int PHOTO_MAX_RIGHT = 763;
const float MAX_DISPLACEMENT_MM = 5.0; // [mm], has been measured
*/

unsigned long TIME_BEGIN = 0;
unsigned long TIME_NOW = 0;
unsigned long TIME_CYCLE = 1000; // this is the time_step in [microseconds] that determines the running frequency


void setup() {
  Serial.begin(250000);
  pinMode(motorPinLeft, OUTPUT);
  pinMode(motorPinRight, OUTPUT);
  
  pinMode(joystick_left_pin, INPUT);
  pinMode(photo_left_pin, INPUT);
  pinMode(joystick_right_pin, INPUT);
  pinMode(photo_right_pin, INPUT);

  TCCR2B = TCCR2B & B11111000 | B00000001; // for PWM frequency of 31372.55 Hz
  #if FASTADC
  // set prescale to 16
  sbi(ADCSRA, ADPS2) ;
  cbi(ADCSRA, ADPS1) ;
  cbi(ADCSRA, ADPS0) ;
  #endif
}

void loop() {
  TIME_BEGIN = micros();
  
  int joy_val_left = analogRead(joystick_left_pin);
  joy_val_left = joy_val_left>>2; // the joystick value is [0..1023] converts it to 8bit
  int joy_val_right = analogRead(joystick_right_pin);
  joy_val_right = joy_val_right>>2; // the joystick value is [0..1023] converts it to 8bit

  photo_value_left_raw = analogRead(photo_left_pin);
  photo_value_right_raw = analogRead(photo_right_pin);
    
  int pwmValueLeftSym = 128;
  int pwmValueRightSym = 128;

//  float k_p = 0.243;
//  float k_i = 0.63;
//  float k_d = 0.00126;
  float k_p = 0.3;
  float k_i = 0.0;
  float k_d = 0.0;

  // If Yoke controller is used:
  /*
   float k_p = 5.0; // [V/mm]
   float k_i = 0.0;
   float k_d = 0.0;

   k_p = k_p * 255 / 40; // to convert it to arduino values
   */

  // Writing to Processing file
  Serial.write(joy_val_left);
  Serial.write(joy_val_right); 
  Serial.write((joy_val_left + joy_val_right)%256); // this is the checksum
  if (Serial.available() > 0) {
    dist_ref = (int)(FILTER_CST*dist_ref + (1-FILTER_CST)* Serial.read()*(MAX_DISPLACEMENT_MM) / 255);
  } else {
    dist_ref = FILTER_CST*dist_ref;
  }
  error_left = dist_ref - sensor2dist(photo_value_left_raw, PHOTO_MIN_LEFT, PHOTO_MAX_LEFT);
  error_right = dist_ref - sensor2dist(photo_value_right_raw, PHOTO_MIN_RIGHT, PHOTO_MAX_RIGHT);
  
  sum_error_left = error_left + sum_error_left;
  sum_error_right = error_right + sum_error_right;
  float numerator_l = error_left - error_left_last;
  float numerator_r = error_right - error_right_last;
  float numerator_l_f = numerator_l*filter_coeff + numerator_l_last_f * (1-filter_coeff);
  float numerator_r_f = numerator_r*filter_coeff + numerator_r_last_f * (1-filter_coeff);

  numerator_l_last_f = numerator_l_f;
  numerator_r_last_f = numerator_r_f;
  error_left_last = error_left;
  error_right_last = error_right;
  
  int des_mot_volt_left = k_p * error_left + k_i * sum_error_left*dT + k_d * numerator_l_f/dT;
  int des_mot_volt_right =  k_p * error_right + k_i * sum_error_right*dT + k_d * numerator_r_f/dT;

  // symmetric feedback left and right, (allowing for negative motor values)
  pwmValueLeftSym = pid2pwm_sym(des_mot_volt_left, OUTPUT_RANGE_L);
  pwmValueRightSym = pid2pwm_sym(des_mot_volt_right, OUTPUT_RANGE_R);

  analogWrite(motorPinLeft, pwmValueLeftSym);
  analogWrite(motorPinRight, pwmValueRightSym); 
 
  while ((micros() - TIME_BEGIN) < TIME_CYCLE) {  } // do nothing until we reach the time step of TIME_CYCLE
}

float sensor2dist(int sensor_value, int min_val, int max_val) {
  // maps the measured value to the distance (assumed linearity) in millimeters
  return MAX_DISPLACEMENT_MM - (sensor_value - min_val) * (MAX_DISPLACEMENT_MM ) / (max_val - min_val) ;
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
