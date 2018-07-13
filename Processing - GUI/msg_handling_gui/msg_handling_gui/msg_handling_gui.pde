/*
//  Controller for Topy's Crawler Robot
 //  Author: Roman Oechslin
 //  Master project - haptic feedback controller - Yamamoto's lab, Uni Tokyo
 //  
 //  Date 2018/07/03
 //  Version 1.02
 
 Todo:
 replace magic numbers with constants
 check if COMs available, otherwise it crashes
 limit current feedback when stopping abruptly
 robot behaves strangely when turning
 pc receives (very rarely) wrong msgs which changes feedback abruptly or driving mode
 test different baud rates and check how smoothly it runs (also update frequency)
 
 
 Improvements:
 Bleulers comment: replace constant force output by vibrating to make it perceived more easily
 
 Bugs, Errors and FIXMEs
 sometimes it stops and goes
 battery should be warned first and if it consits, it has to be a major error
 
 */

import processing.serial.*;
Serial crawlerPort;
Serial arduinoPort;

PFont warningFont;

boolean DEBUG = true; // some cryptic terminal output with a lot of numbers 
boolean VERBOSE = false; // verbose output in terminal
boolean IGNORE_COM = false; // if no port available

int msg_stop[] = {0xFF, 0xEE, 0x00, 0x00, 0x00, 0x00, 0x01, 0x4E, 0x01, 0x6E, 0x01, 
                  0x2D, 0x32, 0x32, 0x02, 0x17, 0x02, 0x17, 0x37, 0x00, 0x00, 0x00, 
                  0x00, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x12, 0x11, 
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0x00, 0x1E, 0xED, 0x0D};
int msg_forward[] = {0xFF, 0xEE, 0x00, 0x46, 0x00, 0x46, 0x01, 0x4E, 0x01, 0x6E, 0x01, 
                    0x2D, 0x32, 0x32, 0x02, 0x17, 0x02, 0x17, 0x37, 0x00, 0x00, 0x00, 
                    0x07, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x12, 0x11, 
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x00, 0x1E, 0x83, 0x0D};
int my_msg[] = msg_stop;
int driving_speed_left = 0x46; // default driving speed of 70%
int driving_speed_right = 0x46; // default driving speed of 70%
boolean time_init = false;
int program_init_time[] = {hour(), minute(), second()}; // to know how long the program has been running
int offset_sec = 0; // offset between computer program and robot

int pitch_angle = 0;
int roll_angle = 0;
final int MAX_ANGLE = 25; // maximum angle for some feedback laws (25 is appropriate)
final int DEADZONE_CST = 27; // deadzone for joystick values (27 is appropriate)
final int ONE_BYTE_LENGTH = 256;
int ARDU_MSG_LENGTH = 3; // number of bytes received from arduino
int RX_ROBOT_MSG_LENGTH = 70; // number of bytes in msg from robot to pc

int crawler_current_left = 0;
int crawler_current_right = 0;
int current_offset[] = {529, 550}; // FIXME check if offset values set correctly, can vary over time

final int STOP_MODE = 0; // both stop
final int FORWARD_MODE = 1; // both forward
final int BACKWARD_MODE = 2; // both backward
final int BL_FR = 3; // backward left forward right
final int FL_BR = 4; // forward left backward right
int driving_mode = STOP_MODE;
int feedback_law = 0; // 0 -> pitch + roll, 1 -> pitch*roll, 2 -> current
int FEEDBACK_MAX = 3; // number of possible different feedback laws
int SAFETY_FACTOR = 1; // factor by which final motor command is diveded by 2 (1 is appropriate)
int ARDU_MSG_SHIFT = 2; // allows to shift msg by 2

int global_loop_counter = 0;
boolean critical_battery_level = false; // is true when voltage drops below 11.5 V

void setup() {
  // setup loop
  if (!IGNORE_COM) arduinoPort = new Serial(this, "COM3", 250000);//9600);
  if (!IGNORE_COM) crawlerPort = new Serial(this, "COM4", 250000);
  size(500, 500);
  frameRate(50); // FIXME was 50
  println("Started up program!");
  if (IGNORE_COM) println("ignoring com ports");
  if (DEBUG) println("DEBUG MODE ON");
  else println("DEBUG MODE OFF");
  if (VERBOSE) println("VERBOSE MODE ON");
  else println("VERBOSE MODE OFF");

  warningFont = createFont("Arial", 16, true);

  fill(0);
  text("Left feedback", width/4-width/20, height/6-height/45);
  text("Right feedback", 3*width/4-width/20, height/6-height/45);
  text("Driving direction", width/2-width/20, height/20-height/45);
  text("Feedback mode\nPress mouse button\n to change.", 9*width/20, 9*height/20-3*height/45);
  text("Battery level", 9*width/20, 15*height/20-height/45);
}

void draw() {
  // main loop
  draw_direction_rectangle();
  if (critical_battery_level) {
    warn_battery();
    send_over_serial(msg_stop);
  } else {
    if (global_loop_counter == 5) { //FIXME was 5
      global_loop_counter = 0;
      construct_msg();
      send_over_serial(my_msg);
      receive_robot_msg();
    }
    receive_arduino_msg();
    draw_feedback_rectangles();

    send_arduino_feedback();
    global_loop_counter +=1 ;
  }
}


void mouseClicked() {
  // change feedback_law by mouse_click
  feedback_law = (feedback_law + 1) %FEEDBACK_MAX;
}

void draw_feedback_rectangles() {
  // visualize feedback on GUI with different feedback_law
  float feedback = get_feedback(roll_angle, pitch_angle, crawler_current_left, crawler_current_right);
  float bar_height = height*0.4;
  switch (feedback_law) {
  case 0:
    // left hand feedback
    fill(145);
    rect(width/4-width/20, height/6, width/10, height*0.4);
    fill(0, 0, 255);
    rect(width/4-width/20, height/6+(1-feedback)*bar_height, width/10, bar_height*feedback);

    // right hand feedback
    fill(145);
    rect(3*width/4-width/20, height/6, width/10, height*0.4);
    fill(0, 0, 255);
    rect(3*width/4-width/20, height/6+(1-feedback)*bar_height, width/10, bar_height*feedback);

    // feedback type indication
    fill(255, 0, 0);
    rect(9*width/20, 9*height/20, width/10, height/10);
    break;
  case 1:
    // left hand feedback
    fill(145);
    rect(width/4-width/20, height/6, width/10, height*0.4);
    fill(0, 0, 255, 255*feedback);
    rect(width/4-width/20, height/6, width/10, height*0.4);

    // right hand feedback
    fill(145);
    rect(3*width/4-width/20, height/6, width/10, height*0.4);
    fill(0, 0, 255, 255*feedback);
    rect(3*width/4-width/20, height/6, width/10, height*0.4);

    // feedback type indication
    fill(0, 255, 0);
    rect(9*width/20, 9*height/20, width/10, height/10);
    break;
  case 2:
    // left hand feedback
    fill(145);
    rect(width/4-width/20, height/6, width/10, height*0.4);
    fill(0, 255, 0);
    rect(width/4-width/20, height/6+(1-feedback)*bar_height, width/10, bar_height*feedback);

    // right hand feedback
    fill(145);
    rect(3*width/4-width/20, height/6, width/10, height*0.4);
    fill(0, 255, 0);
    rect(3*width/4-width/20, height/6+(1-feedback)*bar_height, width/10, bar_height*feedback);

    // feedback type indication
    fill(0, 0, 255);
    rect(9*width/20, 9*height/20, width/10, height/10);
    break;
  }
}


float get_feedback(int roll, int pitch, int crawler_current_left, int crawler_current_right) {
  // sends back a feedback between 0 and 1
  // uses different input or functions depending on feedback_law
  float feedback = 0.0;
  if (driving_mode == FORWARD_MODE || driving_mode == STOP_MODE) {
    float K_P = 0.5/sin(MAX_ANGLE*TWO_PI/360); // proportional gain
    float K_P1 = 1/(sin(MAX_ANGLE*TWO_PI/360)*sin(MAX_ANGLE*TWO_PI/360)); // proportional gain
    float K_P2_inv = 4000; // 4000 seems to be a good unification factor, since AmpMax = 2.0A

    roll = abs(roll);
    pitch = abs(pitch);
    if (roll > MAX_ANGLE) roll = MAX_ANGLE;
    if (pitch > MAX_ANGLE) pitch = MAX_ANGLE;

    switch (feedback_law) {
    case 0:
      feedback = (float) K_P*(sin(roll*TWO_PI/360) + sin(pitch*TWO_PI/360));
      break;
    case 1: 
      if (roll > MAX_ANGLE && pitch > MAX_ANGLE) { 
        // obsolete due to limiting to MAX_ANGLE, but better safe than sorry
        feedback = (float) K_P1*(sin(MAX_ANGLE*TWO_PI/360) * sin(MAX_ANGLE*TWO_PI/360));
      } else if (pitch > MAX_ANGLE) {
        feedback = (float) K_P1*(sin(roll*TWO_PI/360) * sin(MAX_ANGLE*TWO_PI/360));
      } else if (roll > MAX_ANGLE) {
        feedback = (float) K_P1*(sin(MAX_ANGLE*TWO_PI/360) * sin(pitch*TWO_PI/360));
      } else {
        feedback = (float) K_P1*(sin(roll*TWO_PI/360) * sin(pitch*TWO_PI/360));
      }
      break;
    case 2:
      feedback = (float) (crawler_current_left + crawler_current_right) / K_P2_inv;
      break;
    default:
      feedback = 0.0;
      break;
    }
  } else {
    feedback = 0.0;
  }
  if (feedback > 1) feedback = 1.0;
  return feedback;
}


void receive_arduino_msg() { 
  // read the message from the arduino over serial port
  int joystick_value_left = 127;
  int joystick_value_right = 127;
  int received_msg[] = new int[ARDU_MSG_LENGTH + ARDU_MSG_SHIFT];
  int counter = 0;

  while (!IGNORE_COM && arduinoPort.available() > 0 && counter < ARDU_MSG_LENGTH + ARDU_MSG_SHIFT) {
    received_msg[counter] = arduinoPort.read();
    //if (DEBUG) println("read " + counter + " as " + received_msg[counter]);
    counter++;
  }
  
  if (counter == ARDU_MSG_LENGTH + ARDU_MSG_SHIFT) {
    int shift = 0;
    while ((received_msg[0+shift] + received_msg[1+shift])%256 != 
        received_msg[2+shift] && shift < ARDU_MSG_SHIFT) {
      shift += 1;
    } 
    if (shift < ARDU_MSG_SHIFT) {
      joystick_value_left = received_msg[shift];
      joystick_value_right = received_msg[1 + shift];
      //if (DEBUG) println("received: " + joystick_value_left + " and " + joystick_value_right);
    } else { //checksum does not check
      if (DEBUG) println("i did not find anything");
      return;
    }
  } else {
    return;
  }

  if (!IGNORE_COM) arduinoPort.clear(); //TODO think about filtering maybe or taking average

  // shift joystick values by 127 (half a byte) to make it symmetric around 0
  joystick_value_left = joystick_value_left - 127;
  joystick_value_right = joystick_value_right - 127;

  // check for left joystick
  if (abs(joystick_value_left) > DEADZONE_CST) { 
    if (joystick_value_left > DEADZONE_CST) { // driving forwards
      if (VERBOSE) println("left going forward");
      driving_mode = FORWARD_MODE;
      driving_speed_left = joystick_value_left - DEADZONE_CST; 
      // joystick_value_left is bounded between (27..127)
    } else if (-joystick_value_left > DEADZONE_CST) { // driving backwards
      if (VERBOSE) println("left going backwards");
      driving_mode = BACKWARD_MODE;
      driving_speed_left = abs(joystick_value_left + DEADZONE_CST); 
      // joystick_value_left is bounded between (-127..-27)
    }
  } else {
    if (VERBOSE) println("left stopping");
    driving_mode = STOP_MODE;
    driving_speed_left = 0;
  }

  // check for right joystick
  if (abs(joystick_value_right) > DEADZONE_CST) { 
    if (joystick_value_right > DEADZONE_CST) { // driving forward
      if (VERBOSE) println("right going forward");
      if (driving_mode == BACKWARD_MODE) {
        driving_mode = BL_FR;
      } else {
        driving_mode = FORWARD_MODE; // FIXME if i drop this i can forbid one sided turns
      }
      driving_speed_right = joystick_value_right - DEADZONE_CST; 
      // joystick_value_right is bounded between (27..127)
    } else if (-joystick_value_right > DEADZONE_CST) { // driving backwards
      if (VERBOSE) println("right going backwards");
      if (driving_mode == FORWARD_MODE) {
        driving_mode = FL_BR;
      } else {
        driving_mode = BACKWARD_MODE; // FIXME if i drop this i can forbid one sided turns
      }
      driving_speed_right = abs(joystick_value_right + DEADZONE_CST); 
      // joystick_value_right is bounded between (-127..-27)
    }
  } else {
    if (VERBOSE) println("right stopping");
    driving_speed_right = 0;
  }

  //FIXME if safety factor == 0, the robot does not move anymore
  driving_speed_left = driving_speed_left >> SAFETY_FACTOR;
  driving_speed_right = driving_speed_right >> SAFETY_FACTOR;
  if (DEBUG) println("driving speed = " + driving_speed_left + " and " + driving_speed_right);
}


void send_arduino_feedback() {
  // write the feedback according to the specified feedback_law to the arduino serial port
  float feedback = get_feedback(roll_angle, pitch_angle, crawler_current_left, crawler_current_right);
  int arduino_feedback = (int) (feedback*255);//(feedback*1800);//FIXME this should be a constant
  if (!IGNORE_COM) arduinoPort.write(arduino_feedback);
  if (DEBUG) println("send feedback to arduino: " + arduino_feedback);
}

void receive_robot_msg() {
  // read the message received from the robot over the serial port
  // if first message: assign initial offsets
  int received_msg[] = {};
  if (VERBOSE) println("\nread: (in receive robot msg)");
  int msg_length = 0;
  if (!IGNORE_COM) {
    while (crawlerPort.available() > 0) {
      msg_length += 1;
      int inByte = crawlerPort.read();
      received_msg = append(received_msg, inByte);
      if (VERBOSE) print(inByte + ' ');
    }
  }//end IGNORE_COM
  if (VERBOSE) {
    print("\n");
    if (msg_length >= RX_ROBOT_MSG_LENGTH) {
      if (VERBOSE) println("elapsed time is: " + received_msg[67]); 
      //67 is the index of elapse time, beware of second byte in front!!
    }
  }

  if (!time_init && msg_length >= RX_ROBOT_MSG_LENGTH) {
    time_init = true;
    offset_sec = received_msg[66]*ONE_BYTE_LENGTH + received_msg[67] - 
        ((hour() - program_init_time[0])*60+ minute() - program_init_time[1])*60 + 
        second() - program_init_time[2];
    if (VERBOSE) println("I initialized the time with " + offset_sec);
  } 

  if (msg_length >= RX_ROBOT_MSG_LENGTH) {
    roll_angle = convert_angles(received_msg[23], received_msg[24]);
    pitch_angle = convert_angles(received_msg[21], received_msg[22]);
    // read and convert measured crawler currents
    crawler_current_left = abs(convert16bit(received_msg[16], received_msg[17]) - 
        (msg_forward[16]*256) - msg_forward[17]);
    crawler_current_left *= 16000/1024;
    crawler_current_right = abs(convert16bit(received_msg[12], received_msg[13]) - 
        (msg_forward[16]*256) - msg_forward[17]);
    crawler_current_right *= 16000/1024;
    if (VERBOSE) println("crawler current = " + (crawler_current_right + crawler_current_left));
    check_battery_status(received_msg[36]);
  }
  
}

int convert_angles(int high_byte_val, int low_byte_val) {  // FIXME why can't I use convert16bit here?
  // This function converts a 16bit value for the angles to an integer
  int angle = 0;

  if (high_byte_val > 127) {
    angle = -(255 - high_byte_val) << 8;
  } else {
    angle = high_byte_val << 8;
  }
  if (low_byte_val > 127) {
    angle = angle -(255 - low_byte_val);
  } else {
    angle = angle + low_byte_val;
  }
  return angle;
}

int convert16bit(int high_byte_val, int low_byte_val) {
  // This function converts a 16bit value to an integer
  int value = 0;
  value =  (high_byte_val<<8) + low_byte_val;
  if (VERBOSE) println("value = " + value + " high = " + high_byte_val + " low = " + low_byte_val);
  return value;
}

void check_battery_status(int bat_msg) {
  float battery_level = (float) bat_msg *30/255;
  if (VERBOSE) println("battery status = " + battery_level);

  if (battery_level > 13.4) { // everything is fine
    critical_battery_level = false;
    fill(0, 255, 0);
  } else if (battery_level > 12.5) { // mid range
    critical_battery_level = false;
    fill(255, 255, 0);
  } else if (battery_level > 12.1) { // critical, warn
    critical_battery_level = false;
    fill(255, 100, 0);
  } else if (battery_level > 11.5) { // critical, stop
    critical_battery_level = true;
    fill(255, 0, 0);
  } else if (battery_level > 0.01) { // very critical, stop
    print("battery so critically low: "+battery_level);
    critical_battery_level = true;
    fill(255, 0, 0);
  } else {
    println("battery problem: battery level at: " + battery_level + "V!");
  }
  // battery charge indication
  rect(8*width/20, 15*height/20, width/5, height/10);
  fill(0);
  text(floor(battery_level) + "." + (int) ((battery_level - (float) floor(battery_level))*10),
    9*width/20, 16.5*height/20);
}

void draw_direction_rectangle() {
  // indicates in which direction the robot is commanded 
  // (green = forward, red = backward, grey = no command)
  fill(200);
  rect(width/2-width/20, height/20-height/60, width/3, height/14);
  textFont(warningFont, 32);
  switch (driving_mode) {
  case STOP_MODE:
    fill(0, 0, 0);
    text("halt", width/2-width/20, height/10);
    break;
  case FORWARD_MODE:
    fill(0, 255, 0);
    text("forward", width/2-width/20, height/10);
    break;
  case BACKWARD_MODE:
    fill(255, 0, 0);
    text("backward", width/2-width/20, height/10);
    break;
  default:
    fill(0, 0, 0);
    break;
  }
}

void construct_msg() {
  // assigns the driving mode and driving speed for the two crawlers
  switch (driving_mode) {
  case STOP_MODE:
    my_msg = msg_stop;
    if (VERBOSE) println("stop mode\n");
    break;
  case FORWARD_MODE:
    my_msg = msg_forward;
    my_msg[2] = 0;
    my_msg[4] = 0;
    my_msg[3] = driving_speed_right;
    my_msg[5] = driving_speed_left;
    if (VERBOSE) println("forward mode\n");
    break;
  case BACKWARD_MODE:
    my_msg = msg_forward;
    my_msg[2] = 255;
    my_msg[4] = 255;
    my_msg[3] = 255-driving_speed_right;
    my_msg[5] = 255-driving_speed_left;
    if (VERBOSE) println("backward mode\n");
    break;
    //FIXME complete this list
  case FL_BR:
    my_msg = msg_forward;
    my_msg[2] = 255;
    my_msg[3] = 255-driving_speed_right;
    my_msg[4] = 0;
    my_msg[5] = driving_speed_left;
    if (VERBOSE) println("FL BR mode\n");
    break;
  case BL_FR:
    my_msg = msg_forward;
    my_msg[2] = 0;
    my_msg[3] = driving_speed_right;
    my_msg[4] = 255;
    my_msg[5] = 255-driving_speed_left;
    if (VERBOSE) println("BL FR mode\n");
    break;
  default:
    my_msg = msg_stop;
    if (VERBOSE) println("Error, no known driving mode\n");
    break;
  }

  if (time_init) {
    int passed_time = ((hour() - program_init_time[0])*60 + minute() - 
      program_init_time[1])*60 + second() - program_init_time[2] + offset_sec;
    if (passed_time > ONE_BYTE_LENGTH-1) {
      my_msg[40] = passed_time/ONE_BYTE_LENGTH;
    }
    my_msg[41] = passed_time % ONE_BYTE_LENGTH;
    if (VERBOSE) println("\nupdated time to " + passed_time);
  }
}

void send_over_serial(int my_msg[]) {
  // calculates the check_sum and sends message over serial port to robot
  int checksum = 0;
  if (VERBOSE) println("sent message is:\n");
  for (int i=0; i<=43; i++) {
    if (i<42) {
      checksum = checksum + my_msg[i];
    } else if (i == 42) {
      my_msg[i] = checksum%ONE_BYTE_LENGTH;
    }
    if (!IGNORE_COM) crawlerPort.write(my_msg[i]);
    if (VERBOSE) print(my_msg[i] + " ");
  }
  if (VERBOSE) println();
}

void warn_battery() {
  fill(100);
  rect(width/20, height/20, 9*width/10, 9*height/10);
  textFont(warningFont, 40);
  fill(255, 0, 0);
  text("Battery charge critical!\nCharge battery!", width/16, height/2);
}