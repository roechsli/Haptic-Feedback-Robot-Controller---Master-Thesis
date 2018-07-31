/*
  Roman Oechslin
  Robot controller with haptic feedback
  2018/04/06  Tokyo`
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
#define sine_signal_pin A5
int motorPinLowGain = 3;    // Motor connected to digital pin 3 (PWM)
int motorPinHighGain = 11;    // Motor connected to digital pin 11 (PWM)
int testPin = 13; // Used for testing the speed of Arduino

int sine_signal = 0;
int photo_value_left_raw = 0;
int photo_value_right_raw = 0;

float dist_ref = 0.0;
int OUTPUT_PER_VOLT = 255 / 5; // the arduino can output 5V max
int MOTOR_MAX_VOLTAGE = 20; // change this according to motor
int LEFT_HAND_AMPLIFIER_GAIN = 10;
int RIGHT_HAND_AMPLIFIER_GAIN = 10;
const int OUTPUT_RANGE_L = 2 * MOTOR_MAX_VOLTAGE * OUTPUT_PER_VOLT / LEFT_HAND_AMPLIFIER_GAIN;
const int OUTPUT_RANGE_R = 2 * MOTOR_MAX_VOLTAGE * OUTPUT_PER_VOLT / RIGHT_HAND_AMPLIFIER_GAIN;

float error_left = 0;
float last_error_left = 0;
float sum_error_left = 0;
float error_right = 0;
float last_error_right = 0;
float sum_error_right = 0;
const int PHOTO_MIN_LEFT = 550;
const int PHOTO_MAX_LEFT = 780;
const int PHOTO_MIN_RIGHT = 600;
const int PHOTO_MAX_RIGHT = 763;
const float MAX_DISPLACEMENT_UM = 5.0; // [mm], has been measured

char buf[16];
char all[512];
char *p = all;
char *init_p = all;
char semicolon[5] = ";";
char end_char[5] = "\n";

unsigned long TIME_BEGIN = 0;
unsigned long TIME_NOW = 0;
unsigned long TIME_CYCLE = 1000; // this is the time_step in [us] that determines the running frequency


void setup() {
  Serial.begin(250000);
  pinMode(motorPinLowGain, OUTPUT);
  pinMode(motorPinHighGain, OUTPUT);

  pinMode(sine_signal_pin, INPUT);
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

  sine_signal = analogRead(sine_signal_pin);
  photo_value_left_raw = analogRead(photo_left_pin);
  photo_value_right_raw = analogRead(photo_right_pin);

  int pwmValueLeftSym = 128;
  int pwmValueRightSym = 128;

  float k_p = 5.0; // [V/mm]
  float k_i = 0.0;
  float k_d = 0.0;

  k_p = k_p * 255 / 40; // to convert it to arduino values
  // ignore Serial and read sine wave signal as reference
  dist_ref = (float) sine2dist((float) sine_signal);
  error_left = dist_ref - sensor2dist(photo_value_left_raw, PHOTO_MIN_LEFT, PHOTO_MAX_LEFT);
  error_right = dist_ref - sensor2dist(photo_value_right_raw, PHOTO_MIN_RIGHT, PHOTO_MAX_RIGHT);

  int des_mot_volt_left = k_p * error_left + k_i * sum_error_left + k_d * (error_left - last_error_left);
  int des_mot_volt_right =  k_p * error_right + k_i * sum_error_right + k_d * (error_right - last_error_right);//FIXME need two different control parameters?
  sum_error_left = error_left + sum_error_left;
  last_error_left = error_left;
  sum_error_right = error_right + sum_error_right;
  last_error_right = error_right;

  // symmetric feedback left and right, (allowing for negative motor values)
  pwmValueLeftSym = pid2pwm_sym(des_mot_volt_left, OUTPUT_RANGE_L);
  pwmValueRightSym = pid2pwm_sym(des_mot_volt_right, OUTPUT_RANGE_R);

  analogWrite(motorPinLowGain, pwmValueLeftSym); //pwmValueLeftSym
  analogWrite(motorPinHighGain, pwmValueRightSym); //pwmValueRightSym
  
  //fastest way of writing data to serial
  all[0] = '\0';
  p = mystrcat(init_p, itoa(dist_ref*1000, buf, 16));
  p = mystrcat(p, semicolon);
  p = mystrcat(p, itoa(photo_value_left_raw, buf, 16));
  p = mystrcat(p, semicolon);
  p = mystrcat(p, itoa(photo_value_right_raw, buf, 16));
  p = mystrcat(p, semicolon);
  p = mystrcat(p, itoa(TIME_BEGIN, buf, 16));
  p = mystrcat(p, semicolon);
  p = mystrcat(p, end_char);
  Serial.print(all); //TODO this is necessary for logging
  // message format: dist ref | left val | right val | time stamp

  /*
  Serial.print("photo_value_right_raw: ");
  Serial.println(photo_value_right_raw);
  Serial.print("dist_ref: ");
  Serial.println(dist_ref);
  Serial.print("my_dist: ");
  Serial.println(sensor2dist(photo_value_right_raw, PHOTO_MIN_RIGHT, PHOTO_MAX_RIGHT));
  Serial.print("pwm: ");
  Serial.println(pwmValueRightSym);
  Serial.print("ref = ");
  Serial.println(dist_ref);
  Serial.print("photo_value_left_raw = ");
  Serial.println(photo_value_left_raw);
  Serial.print("error = ");
  Serial.println(error_left);
  Serial.print("des_mot_volt_right = ");
  Serial.println(des_mot_volt_right);
  Serial.print("pwmValueLeftSym = ");
  Serial.println(pwmValueLeftSym);
  Serial.print("sensor dist = ");
  Serial.println(sensor2dist(photo_value_left_raw, PHOTO_MIN_LEFT, PHOTO_MAX_LEFT));*/
  

  while ((micros() - TIME_BEGIN) < TIME_CYCLE) {  } // do nothing until we reach the time step of TIME_CYCLE
}


char* mystrcat( char* dest, char* src )
{
  // taken from https://stackoverflow.com/questions/21880730/c-what-is-the-best-and-fastest-way-to-concatenate-strings?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
  while (*dest) dest++;
  while (*dest++ = *src++);
  return --dest;
}

float sine2dist(float sine){
  return (sine / 4.0) * (MAX_DISPLACEMENT_UM) / 256.0 ; 
  // sine / 1024 * MAX_DISPLACEMENT_UM had to be rewritten due to overflow
}

float sensor2dist(int sensor_value, int min_val, int max_val) {
  // maps the measured value to the distance (assumed linearity) in micrometers
  //Serial.println(MAX_DISPLACEMENT_UM - (sensor_value - min_val) * (MAX_DISPLACEMENT_UM) / (max_val - min_val));
  return MAX_DISPLACEMENT_UM - (sensor_value - min_val) * (MAX_DISPLACEMENT_UM) / (max_val - min_val) ;
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


