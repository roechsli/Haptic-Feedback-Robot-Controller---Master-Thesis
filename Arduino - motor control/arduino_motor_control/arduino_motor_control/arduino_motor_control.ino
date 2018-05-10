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

int feedback = 0;
float FILTER_CST = 0.5;
int OUTPUT_PER_VOLT = 255/5; // the arduino can output 5V max
int MOTOR_MAX_VOLTAGE = 20; // change this according to motor
int LEFT_HAND_AMPLIFIER_GAIN = 5;
int RIGHT_HAND_AMPLIFIER_GAIN = 5;
bool USE_JOYSTICK_DIRECT_LINK = false;

int error_left = 0; 
int last_error_left = 0;
int sum_error_left = 0;
int error_right = 0; 
int last_error_right = 0;
int sum_error_right = 0;
const int PHOTO_MIN_LEFT = 500;//0;
const int PHOTO_MAX_LEFT = 770;//1023;
const int PHOTO_MIN_RIGHT = 680;//0;
const int PHOTO_MAX_RIGHT = 770;//1023;

void setup() {
  Serial.begin(115200);
  pinMode(motorPinLowGain, OUTPUT);
  pinMode(motorPinHighGain, OUTPUT);
  pinMode(joystick_left_pin, INPUT);
  pinMode(photo_left_pin, INPUT);
  pinMode(joystick_right_pin, INPUT);
  pinMode(photo_right_pin, INPUT);

  TCCR2B = TCCR2B & B11111000 | B00000001; // for PWM frequency of 31372.55 Hz
}

void loop() {
  int joy_val_left = analogRead(joystick_left_pin);
  joy_val_left = joy_val_left>>2; // the joystick value is [0..1023] and I want to convert it to 8bit
  int joy_val_right = analogRead(joystick_right_pin);
  joy_val_right = joy_val_right>>2; // the joystick value is [0..1023] and I want to convert it to 8bit

  int pwmValueLeft = 0;
  int pwmValueRight = 0;
  
  if (USE_JOYSTICK_DIRECT_LINK) {
    pwmValueLeft = feedback2pwm((joy_val_left-127)>0?joy_val_left:0, LEFT_HAND_AMPLIFIER_GAIN);
    pwmValueRight = feedback2pwm((joy_val_right-127)>0?joy_val_right:0, RIGHT_HAND_AMPLIFIER_GAIN);
  } else {
    int photo_value_left = analogRead(photo_left_pin);
    int photo_value_right = analogRead(photo_right_pin);
    float k_p = 1.5; // k_p = 1; and k_i = 0.01; works as well
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
      feedback = (int)(FILTER_CST*feedback + (1-FILTER_CST)* Serial.read());
    } else {
      feedback = 0.99*feedback;// FIXME tune this param
    }
    error_left = feedback - map_to_255(photo_value_left, PHOTO_MIN_LEFT, PHOTO_MAX_LEFT);
    error_right = feedback - map_to_255(photo_value_right, PHOTO_MIN_RIGHT, PHOTO_MAX_RIGHT);
        
    int motor_output_left = k_p * error_left + k_i * sum_error_left + k_d * (error_left - last_error_left);
    int motor_output_right =  k_p * error_right + k_i * sum_error_right + k_d * (error_right - last_error_right);//FIXME need two different control parameters?
    sum_error_left = error_left + sum_error_left;
    last_error_left = error_left;
    sum_error_right = error_right + sum_error_right;
    last_error_right = error_right;
    // feedbackLeft
    pwmValueLeft = feedback2pwm(motor_output_left, LEFT_HAND_AMPLIFIER_GAIN); // TODO CHANGETHIS should be motoroutput
    // feedbackRight
    pwmValueRight = feedback2pwm(motor_output_right, RIGHT_HAND_AMPLIFIER_GAIN); // TODO CHANGETHIS should be motoroutput


/*
    //FOR DEBUGGING PURPOSES
    Serial.print("right photo value mapped [0..255]: ");
    Serial.println(map_to_255(photo_value_right, PHOTO_MIN_RIGHT, PHOTO_MAX_RIGHT));
    Serial.print("right photo value: ");
    Serial.println(photo_value_right);
    Serial.print("right motor: ");
    Serial.println(pwmValueRight);*/
  }
  analogWrite(motorPinLowGain, pwmValueLeft);
  analogWrite(motorPinHighGain, pwmValueRight);
 
  delay(1);
}

int map_to_255(int receptor_value, int min_val, int max_val) {
  // this function maps the measured value to the feedback range [0..255]
  //int converted = (int) ((float) ((receptor_value - min_val) / (max_val - min_val)) * 255 );
  int converted = (receptor_value - min_val) * 51 / (max_val - min_val) * 5;
  //int converted = (int) ((long int) ((receptor_value - min_val) * 5 ) / (max_val - min_val)*51);
  converted = 255 - converted;
  return converted;
}

int limit_value(int motor_output, int lower, int upper) {
  if (motor_output < lower) {
    motor_output = lower;
  } else if (motor_output > upper) {
    motor_output = upper;
  }
  return motor_output;
}

int feedback2pwm(int feedback, float gain){
  // conversion of feedback to pwm[0..255]:
  int pwm = 0;
  feedback = limit_value(feedback, 0, 255);
  // cut off at MAX_VOLTAGE
  pwm = ((float) feedback) * MOTOR_MAX_VOLTAGE * OUTPUT_PER_VOLT / gain / 255;
  //pwm = ((float) feedback)*MAX_VOLTAGE_FB*gain/255;
  return pwm;
}

