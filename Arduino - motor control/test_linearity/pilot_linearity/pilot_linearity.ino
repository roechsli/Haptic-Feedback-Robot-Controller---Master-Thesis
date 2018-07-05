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
#define sine_signal_pin A5
int motorPinHighGain = 11; 
int testPin = 13; // Used for testing the speed of Arduino

int sine_signal = 0;

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
const int PHOTO_MIN_LEFT = 36;
const int PHOTO_MAX_LEFT = 850;
const int MAX_DISPLACEMENT_UM = 1800; // [um], has been measured

unsigned long TIME_BEGIN = 0;
unsigned long TIME_NOW = 0;
unsigned long TIME_CYCLE = 1000; // this is the time_step in [microseconds] that determines the running frequency


void setup() {
  Serial.begin(250000);
  pinMode(motorPinHighGain, OUTPUT);
  
  pinMode(sine_signal_pin, INPUT);
  pinMode(joystick_left_pin, INPUT);
  pinMode(photo_left_pin, INPUT);
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
  
  sine_signal = analogRead(sine_signal_pin);
  int photo_value_left = analogRead(photo_left_pin);
    
  int pwmValueLeftSym = 128;

  float k_p = 0.2; // k_p = 1; and k_i = 0.01; works as well
  float k_i = 0.0;
  float k_d = 0.0;

  //Writing to Processing file
  //Serial.write(joy_val_left);
  //Serial.write(joy_val_right); 
  //Serial.write((joy_val_left + joy_val_right)%256); // this is the checksum
  //Serial.println(joy_val_right);// for debugging purposes in serial monitor mode
  if (Serial.available() > 0) {
    dist_ref = (int)(FILTER_CST*dist_ref + (1-FILTER_CST)* Serial.read());
  } else {
    dist_ref = 0.99*dist_ref;// FIXME tune this param
  }

  dist_ref = sine2dist(sine_signal);
  error_left = dist_ref - sensor2dist(photo_value_left, PHOTO_MIN_LEFT, PHOTO_MAX_LEFT);
      
  int motor_output_left = k_p * error_left + k_i * sum_error_left + k_d * (error_left - last_error_left);
  sum_error_left = error_left + sum_error_left;
  last_error_left = error_left;
  // symmetric feedback left and right, (allowing for negative motor values)
  pwmValueLeftSym = pid2pwm_sym(motor_output_left, OUTPUT_RANGE_L);

  Serial.print("photo_value_left: ");
  Serial.println(photo_value_left);
  Serial.print("dist_ref: ");
  Serial.println(dist_ref);
  Serial.print("my_dist: ");
  Serial.println(sensor2dist(photo_value_left, PHOTO_MIN_LEFT, PHOTO_MAX_LEFT));


  analogWrite(motorPinHighGain, pwmValueLeftSym);//pwmValueLeftSym
 
  while ((micros() - TIME_BEGIN) < TIME_CYCLE) {  } // do nothing until we reach the time step of TIME_CYCLE
  digitalWrite(testPin, LOW); //instructions in between take roughly 640 microseconds
}

int sensor2dist(int sensor_value, int min_val, int max_val) {
  // maps the measured value to the distance (assumed linearity) in micrometers
  return MAX_DISPLACEMENT_UM - (sensor_value - min_val) * (MAX_DISPLACEMENT_UM /60) / (max_val - min_val) * 60;
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

int sine2dist(int sine){
  return (((sine / 4) * (MAX_DISPLACEMENT_UM / 15) / 16) * 15) / 16; 
  // sine / 1024 * MAX_DISPLACEMENT_UM had to be rewritten due to overflow
}

