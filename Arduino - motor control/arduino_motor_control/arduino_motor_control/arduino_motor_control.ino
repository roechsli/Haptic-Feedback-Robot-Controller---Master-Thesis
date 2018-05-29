/*
  Roman Oechslin
  Robot controller with haptic feedback
  2018/04/06  Tokyo
*/

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
bool USE_JOYSTICK_DIRECT_LINK = false;

int error_left = 0; 
int last_error_left = 0;
int sum_error_left = 0;
int error_right = 0; 
int last_error_right = 0;
int sum_error_right = 0;
const int PHOTO_MIN_LEFT = 514;//500;//0;//514;
const int PHOTO_MAX_LEFT = 787;//770;//1023;//787;
const int PHOTO_MIN_RIGHT = 678;//680;//0;//678;
const int PHOTO_MAX_RIGHT = 773;//770;//1023;//773;

unsigned long TIME_BEGIN = 0;
unsigned long TIME_NOW = 0;
unsigned long TIME_CYCLE = 1000; // this is the time_step in [microseconds] that determines the running frequency


void setup() {
  Serial.begin(115200);
  pinMode(motorPinLowGain, OUTPUT);
  pinMode(motorPinHighGain, OUTPUT);
  pinMode(joystick_left_pin, INPUT);
  pinMode(photo_left_pin, INPUT);
  pinMode(joystick_right_pin, INPUT);
  pinMode(photo_right_pin, INPUT);
  pinMode(testPin, OUTPUT);

  TCCR2B = TCCR2B & B11111000 | B00000001; // for PWM frequency of 31372.55 Hz
}

void loop() {
  digitalWrite(testPin, HIGH); // this is only used to measure the operating frequency
  TIME_BEGIN = micros();
  
  int joy_val_left = analogRead(joystick_left_pin);
  joy_val_left = joy_val_left>>2; // the joystick value is [0..1023] and I want to convert it to 8bit
  int joy_val_right = analogRead(joystick_right_pin);
  joy_val_right = joy_val_right>>2; // the joystick value is [0..1023] and I want to convert it to 8bit

  int pwmValueLeft = 0;
  int pwmValueRight = 0;
  int pwmValueLeftSym = 128;
  int pwmValueRightSym = 128;
  
  if (USE_JOYSTICK_DIRECT_LINK) {
    pwmValueLeft = output2pwm_sym((joy_val_left-127)>0?joy_val_left:0, LEFT_HAND_AMPLIFIER_GAIN);
    pwmValueRight = output2pwm_sym((joy_val_right-127)>0?joy_val_right:0, RIGHT_HAND_AMPLIFIER_GAIN);
  } else {
    int photo_value_left = analogRead(photo_left_pin);
    int photo_value_right = analogRead(photo_right_pin);
    float k_p = 1.0; // k_p = 1; and k_i = 0.01; works as well
    float k_i = 0.0;
    float k_d = 0.0;
    photo_value_left = limit_value(photo_value_left, PHOTO_MIN_LEFT, PHOTO_MAX_LEFT);
    photo_value_right = limit_value(photo_value_right, PHOTO_MIN_RIGHT, PHOTO_MAX_RIGHT);
    // just to be sure that it is not out of expected boundaries

    //Serial.println(joy_val_right);
    Serial.write(joy_val_left);
    Serial.write(joy_val_right); 
    Serial.write((joy_val_left + joy_val_right)%256); // this is the checksum
    //Serial.println(joy_val_right);// for debugging purposes in serial monitor mode
    if (Serial.available() > 0) {
      dist_ref = (int)(FILTER_CST*dist_ref + (1-FILTER_CST)* Serial.read());
    } else {
      dist_ref = 0.99*dist_ref;// FIXME tune this param
    }
    error_left = dist_ref - map_to_255(photo_value_left, PHOTO_MIN_LEFT, PHOTO_MAX_LEFT);
    error_right = dist_ref - map_to_255(photo_value_right, PHOTO_MIN_RIGHT, PHOTO_MAX_RIGHT);
        
    int motor_output_left = k_p * error_left + k_i * sum_error_left + k_d * (error_left - last_error_left);
    int motor_output_right =  k_p * error_right + k_i * sum_error_right + k_d * (error_right - last_error_right);//FIXME need two different control parameters?
    sum_error_left = error_left + sum_error_left;
    last_error_left = error_left;
    sum_error_right = error_right + sum_error_right;
    last_error_right = error_right;
    // feedbackLeft
    //pwmValueLeft = feedback2pwm(motor_output_left, LEFT_HAND_AMPLIFIER_GAIN); // TODO CHANGETHIS should be motoroutput
    // feedbackRight
    //pwmValueRight = feedback2pwm(motor_output_right, RIGHT_HAND_AMPLIFIER_GAIN); // TODO CHANGETHIS should be motoroutput
    // symmetric feedbackLeft, (allowing for negative motor values)
    pwmValueLeftSym = output2pwm_sym(motor_output_left, LEFT_HAND_AMPLIFIER_GAIN); //motor_output_left
    // symmetric feedbackRight, (allowing for negative motor values)
    pwmValueRightSym = output2pwm_sym(motor_output_right, RIGHT_HAND_AMPLIFIER_GAIN);

  }
  analogWrite(motorPinLowGain, pwmValueLeftSym);//pwmValueLeftSym
  analogWrite(motorPinHighGain, pwmValueRightSym); //pwmValueRightSym
 
  while ((micros() - TIME_BEGIN) < TIME_CYCLE) {  } // do nothing until we reach the time step of TIME_CYCLE
  digitalWrite(testPin, LOW); //instructions in between take roughly 640 microseconds
}

int map_to_255(int receptor_value, int min_val, int max_val) {
  // this function maps the measured value to the feedback range [0..255]
  int converted = (receptor_value - min_val) * 51 / (max_val - min_val) * 5;
  converted = 255 - converted;
  return converted;
}

int limit_value(int value, int lower, int upper) {
  if (value < lower) {
    value = lower;
  } else if (value > upper) {
    value = upper;
  }
  return value;
}

int output2pwm_sym(int output, float gain) {
  // This function converts the reference symmetrically into a PWM where 0 is full power in one direction and 255 is full power in the other
  // Due to the non exactness of the sensor MIN and MAX values, this still results in some asymmetries however
  // conversion of feedback to pwm[0..255]:
  
  // limit to MAX_VOLTAGE
  int limit_val = 2 * MOTOR_MAX_VOLTAGE * OUTPUT_PER_VOLT / gain;
  float pwm = (float) output / 16 * limit_val / (32) + limit_val / 2;
  return limit_value((int) pwm, 0, limit_val);
}

