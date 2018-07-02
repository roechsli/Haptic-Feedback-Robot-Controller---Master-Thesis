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
int controlPin = 6; // Used for checking the distance

int sine_signal = 0;
int photo_value_left_raw = 0;
int photo_value_right_raw = 0;

int dist_ref = 0;
int OUTPUT_PER_VOLT = 255 / 5; // the arduino can output 5V max
int MOTOR_MAX_VOLTAGE = 20; // change this according to motor
int LEFT_HAND_AMPLIFIER_GAIN = 10;
int RIGHT_HAND_AMPLIFIER_GAIN = 10;
const int OUTPUT_RANGE_L = 2 * MOTOR_MAX_VOLTAGE * OUTPUT_PER_VOLT / LEFT_HAND_AMPLIFIER_GAIN;
const int OUTPUT_RANGE_R = 2 * MOTOR_MAX_VOLTAGE * OUTPUT_PER_VOLT / RIGHT_HAND_AMPLIFIER_GAIN;

float error_left = 0;
//float last_error_left = 0;
float sum_error_left = 0;
float error_right = 0;
//float last_error_right = 0;
float sum_error_right = 0;
float dT = 0.001;
float filter_coeff = 0.1;
/*
float photo_value_left_filtered = 0;
float photo_value_right_filtered = 0;
float last_photo_value_left_filtered = 0;
float last_photo_value_right_filtered = 0;
float error_left_filtered = 0;
float error_right_filtered = 0;
float last_error_left_filtered = 0;
float last_error_right_filtered = 0;*/
float error_left_last = 0;
float error_right_last = 0;
float numerator_l_last_f = 0;
float numerator_r_last_f = 0;

const int PHOTO_MIN_LEFT = 640;//650;
const int PHOTO_MAX_LEFT = 840;//830;
const int PHOTO_MIN_RIGHT = 700;//700;
const int PHOTO_MAX_RIGHT = 880;//870;
const int MAX_DISPLACEMENT_UM = 1800; // [um], has been measured

char buf[16];
char all[512];
char *p = all;
char *init_p = all;
char semicolon[5] = ";";
char end_char[5] = "\n";

unsigned long TIME_BEGIN = 0;
unsigned long TIME_NOW = 0;
unsigned long TIME_CYCLE = 1000; // this is the time_step in [us] that determines the running frequency

//trial:
int test_valpid = 0;
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
  pinMode(controlPin, OUTPUT);

  

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

  // k_p = 0.243; k_i = 0.63; k_d =0.00126
  float k_p = 0.243;//1.6; // k_p = 0.8; and k_i = 0.01; k_d = 0.008; works as well
  float k_i = 0.63; // k_p = 1.0; and k_i = 0.01; k_d = 0.05; works as well
  float k_d = 0.00126;//0.014;

  // ignore Serial and read sine wave signal as reference
  dist_ref = sine2dist(sine_signal);
  error_left = dist_ref - sensor2dist(photo_value_left_raw, PHOTO_MIN_LEFT, PHOTO_MAX_LEFT);
  error_right = dist_ref - sensor2dist(photo_value_right_raw, PHOTO_MIN_RIGHT, PHOTO_MAX_RIGHT);

  /*photo_value_left_filtered = last_photo_value_left_filtered * (1- filter_coeff) + photo_value_left_raw * filter_coeff;
  photo_value_right_filtered = last_photo_value_right_filtered * (1- filter_coeff) + photo_value_right_raw * filter_coeff;
  error_left_filtered = dist_ref - sensor2dist(photo_value_left_filtered, PHOTO_MIN_LEFT, PHOTO_MAX_LEFT);
  error_right_filtered = dist_ref - sensor2dist(photo_value_right_filtered, PHOTO_MIN_RIGHT, PHOTO_MAX_RIGHT);
  float derror_left = (error_left_filtered - last_error_left_filtered);
  float derror_right = (error_right_filtered - last_error_right_filtered);
  last_error_left_filtered = error_left_filtered;
  last_error_right_filtered = error_right_filtered;*/
  sum_error_left = error_left*dT + sum_error_left;
  sum_error_right = error_right*dT + sum_error_right;
  float numerator_l = error_left - error_left_last;
  float numerator_r = error_right - error_right_last;
  float numerator_l_f = numerator_l*filter_coeff + numerator_l_last_f * (1-filter_coeff);
  float numerator_r_f = numerator_r*filter_coeff + numerator_r_last_f * (1-filter_coeff);

 
  numerator_l_last_f = numerator_l_f;
  numerator_r_last_f = numerator_r_f;
  error_left_last = error_left;
  error_right_last = error_right;
  
  int des_mot_volt_left = k_p * error_left + k_i * sum_error_left + k_d * numerator_l_f/dT;
  int des_mot_volt_right =  k_p * error_right + k_i * sum_error_right + k_d * numerator_r_f/dT;

  // symmetric feedback left and right, (allowing for negative motor values)
  pwmValueLeftSym = pid2pwm_sym(des_mot_volt_left, OUTPUT_RANGE_L);
  pwmValueRightSym = pid2pwm_sym(des_mot_volt_right, OUTPUT_RANGE_R);

  analogWrite(motorPinLowGain, pwmValueLeftSym); //pwmValueLeftSym
  analogWrite(motorPinHighGain, pwmValueRightSym); //pwmValueRightSym
  
  //fastest way of writing data to serial
  all[0] = '\0';
  p = mystrcat(init_p, itoa(dist_ref, buf, 16));
  p = mystrcat(p, semicolon);
  p = mystrcat(p, itoa(photo_value_left_raw, buf, 16));
  p = mystrcat(p, semicolon);
  p = mystrcat(p, itoa(photo_value_right_raw, buf, 16));
  p = mystrcat(p, semicolon);
  p = mystrcat(p, itoa(TIME_BEGIN, buf, 16));
  p = mystrcat(p, semicolon);
  p = mystrcat(p, end_char);
  //Serial.print(all); //TODO this is necessary for logging
  // message format: dist ref | left val | right val | time stamp

  /*
  Serial.print("ref = ");
  Serial.println(dist_ref);
  Serial.print("photo_value_right_raw = ");
  Serial.println(photo_value_right_raw)
  Serial.print("error = ");
  Serial.println(error_right);
  Serial.print("des_mot_volt_right = ");
  Serial.println(des_mot_volt_right);
  Serial.print("pwmValueRightSym = ");
  Serial.println(pwmValueRightSym);

  Serial.print("measured dist = ");
  Serial.println(sensor2dist(photo_value_right_raw, PHOTO_MIN_RIGHT, PHOTO_MAX_RIGHT));*/
  Serial.print("error right = ");
  Serial.println( error_right);
  Serial.print("proportional term = ");
  Serial.println(k_p * error_right);/*
  Serial.print("integral term = ");
  Serial.println( k_i * sum_error_right);*/
  Serial.print("derivative term = ");
  Serial.println(k_d * numerator_r_f/dT);
  Serial.print("numerator_r = ");
  Serial.println( numerator_r);
  
  
  while ((micros() - TIME_BEGIN) < TIME_CYCLE) {  } // do nothing until we reach the time step of TIME_CYCLE
  digitalWrite(testPin, LOW); //instructions in between take roughly 640 microseconds
  analogWrite(controlPin, 255-map(photo_value_right_raw,PHOTO_MIN_RIGHT, PHOTO_MAX_RIGHT, 0, 255)); 
  //analogWrite(controlPin, 255-map(photo_value_left_raw,PHOTO_MIN_LEFT, PHOTO_MAX_LEFT, 0, 255));  
}


char* mystrcat( char* dest, char* src )
{
  // taken from https://stackoverflow.com/questions/21880730/c-what-is-the-best-and-fastest-way-to-concatenate-strings?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
  while (*dest) dest++;
  while (*dest++ = *src++);
  return --dest;
}

int sine2dist(int sine){
  return (((sine / 4) * (MAX_DISPLACEMENT_UM / 15) / 16) * 15) / 16; 
  // sine / 1024 * MAX_DISPLACEMENT_UM had to be rewritten due to overflow
}

int sensor2dist(int sensor_value, int min_val, int max_val) {
  // maps the measured value to the distance (assumed linearity) in micrometers
  return MAX_DISPLACEMENT_UM - (sensor_value - min_val) * (MAX_DISPLACEMENT_UM /15) / (max_val - min_val) * 15;
}

int sensor2(int dist_value, int min_val, int max_val) {
  // maps the measured value to the distance (assumed linearity) in micrometers
  return (MAX_DISPLACEMENT_UM - dist_value) * (max_val - min_val) / MAX_DISPLACEMENT_UM + min_val;
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


