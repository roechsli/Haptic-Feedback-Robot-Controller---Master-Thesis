/*
  Roman Oechslin
  Robot controller with haptic feedback
  2018/04/06  Tokyo`
*/

#define joystick_left_pin A0
#define photo_left_pin A2
#define joystick_right_pin A1
#define photo_right_pin A3
#define sine_signal_pin A5
int motorPinLowGain = 3;    // Motor connected to digital pin 3 (PWM)
int motorPinHighGain = 11;    // Motor connected to digital pin 11 (PWM)
int testPin = 13; // Used for testing the speed of Arduino

//int roman_zaehl_var = 0;

int dist_ref = 0;
float FILTER_CST = 0.5;
int OUTPUT_PER_VOLT = 255 / 5; // the arduino can output 5V max
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
const int PHOTO_MIN_LEFT = 650;//440;
const int PHOTO_MAX_LEFT = 830;
const int PHOTO_MIN_RIGHT = 700;//630;
const int PHOTO_MAX_RIGHT = 870;//875;

char buf[16];
char all[512];
char *p = all;
char *init_p = all;
char semicolon[5] = ";";
char end_char[5] = "\n";

unsigned long TIME_BEGIN = 0;
unsigned long TIME_NOW = 0;
unsigned long TIME_CYCLE = 1000; // this is the time_step in [microseconds] that determines the running frequency


void setup() {
  Serial.begin(115200);
  pinMode(motorPinLowGain, OUTPUT);
  pinMode(motorPinHighGain, OUTPUT);

  pinMode(sine_signal_pin, INPUT);
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

  int sine_signal = analogRead(sine_signal_pin);
  /*
    int joy_val_left = analogRead(joystick_left_pin);
    joy_val_left = joy_val_left>>2; // the joystick value is [0..1023] and I want to convert it to 8bit
    int joy_val_right = analogRead(joystick_right_pin);
    joy_val_right = joy_val_right>>2; // the joystick value is [0..1023] and I want to convert it to 8bit
  */

  int photo_value_left_raw = analogRead(photo_left_pin);
  int photo_value_right_raw = analogRead(photo_right_pin);

  int pwmValueLeft = 0;
  int pwmValueRight = 0;
  int pwmValueLeftSym = 128;
  int pwmValueRightSym = 128;

  float k_p = 3.0; // k_p = 1; and k_i = 0.01; works as well
  float k_i = 0.0;
  float k_d = 0.0;
  int photo_value_left = limit_value(photo_value_left_raw, PHOTO_MIN_LEFT, PHOTO_MAX_LEFT);
  int photo_value_right = limit_value(photo_value_right_raw, PHOTO_MIN_RIGHT, PHOTO_MAX_RIGHT);
  // just to be sure that it is not out of expected boundaries

  // ignore Serial and read sine wave signal as reference
  dist_ref = sine_signal >> 2; // dist ref is between [0..255]
  error_left = dist_ref - map_to_255(photo_value_left, PHOTO_MIN_LEFT, PHOTO_MAX_LEFT);
  error_right = dist_ref - map_to_255(photo_value_right, PHOTO_MIN_RIGHT, PHOTO_MAX_RIGHT);

  int motor_output_left = k_p * error_left + k_i * sum_error_left + k_d * (error_left - last_error_left);
  int motor_output_right =  k_p * error_right + k_i * sum_error_right + k_d * (error_right - last_error_right);//FIXME need two different control parameters?
  sum_error_left = error_left + sum_error_left;
  last_error_left = error_left;
  sum_error_right = error_right + sum_error_right;
  last_error_right = error_right;
  
  // symmetric feedback left and right, (allowing for negative motor values)
  
  pwmValueLeftSym = output2pwm_sym(motor_output_left, LEFT_HAND_AMPLIFIER_GAIN);
  pwmValueRightSym = output2pwm_sym(motor_output_right, RIGHT_HAND_AMPLIFIER_GAIN);

  analogWrite(motorPinLowGain, pwmValueLeftSym); //pwmValueLeftSym
  analogWrite(motorPinHighGain, pwmValueRightSym); //pwmValueRightSym


  //fastest way of writing data to serial
  // msg: dist_ref ;   photo val left  ;    photo val right ;    time
  all[0] = '\0';
  p = mystrcat(init_p, itoa(dist_ref, buf, 16));
  p = mystrcat(p, semicolon);
  p = mystrcat(p, itoa(photo_value_left_raw, buf, 16));
  p = mystrcat(p, semicolon);
  p = mystrcat(p, itoa(photo_value_right_raw, buf, 16));
  p = mystrcat(p, semicolon);
  /*p = mystrcat(p, itoa(pwmValueLeftSym, buf, 16));
    p = mystrcat(p, semicolon);
    p = mystrcat(p, itoa(pwmValueRightSym, buf, 16));
    p = mystrcat(p, semicolon);*/
  p = mystrcat(p, itoa(TIME_BEGIN, buf, 16));
  p = mystrcat(p, semicolon);
  p = mystrcat(p, end_char);
  Serial.print(all); //TODO this is necessary for logging
  //Serial.println(pwmValueLeftSym);
  // message format: dist ref | left val | right val | time stamp
  /*Serial.println(pwmValueLeftSym);
  Serial.print("error = ");
  Serial.println(error_left);
  Serial.print("sine = ");
  Serial.println(dist_ref);

  
  Serial.print("roman_zaehl_var = ");
  Serial.println(roman_zaehl_var);
  roman_zaehl_var += 1;
  Serial.print("pwm = ");
  Serial.println(output2pwm_sym(roman_zaehl_var, LEFT_HAND_AMPLIFIER_GAIN));
  if (roman_zaehl_var > 255) roman_zaehl_var = -255;*/

  while ((micros() - TIME_BEGIN) < TIME_CYCLE) {  } // do nothing until we reach the time step of TIME_CYCLE
  digitalWrite(testPin, LOW); //instructions in between take roughly 640 microseconds
}


char* mystrcat( char* dest, char* src )
{
  // taken from https://stackoverflow.com/questions/21880730/c-what-is-the-best-and-fastest-way-to-concatenate-strings?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
  while (*dest) dest++;
  while (*dest++ = *src++);
  return --dest;
}

int map_to_255(int receptor_value, int min_val, int max_val) {
  // this function maps the measured value to the range [0..255] =  [normal..compressed]
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
  //float pwm = (float) output / 16 * limit_val / (32) + limit_val / 2;
  float pwm = (float) output * limit_val / 2 / 255 + 128;
  return limit_value((int) pwm, (256-limit_val)/2, limit_val + (256-limit_val)/2);
}


