#include <Arduino.h>
#include <ArduinoJson.h>

StaticJsonDocument<200> stats;
unsigned long status_throttle = millis();
#define STATUS_THROTTLE 1000

#define MOTOR_STEPS 200
#define MICROSTEP 32
#define RPM 30
#define MAX_ROTATE_DEGREES 360 * 13

#define DIR 8
#define STEP 9
#define SLEEP 13

#define READ_DIRECTION_PIN 5
#define SENSOR_CLOSED_PIN 6
#define SENSOR_OPEN_PIN 7

#include "DRV8825.h"
#define MODE0 10
#define MODE1 11
#define MODE2 12
DRV8825 stepper(MOTOR_STEPS, DIR, STEP, SLEEP, MODE0, MODE1, MODE2);

#define OPEN HIGH
#define CLOSE LOW

#define OPENING 1
#define CLOSING -1

void setup() {
    Serial.begin(115200);
    stepper.begin(RPM);
    stepper.setMicrostep(MICROSTEP);
}

bool read_sensor_open() {
  return !digitalRead(SENSOR_OPEN_PIN);
}
bool read_sensor_close() {
  return !digitalRead(SENSOR_CLOSED_PIN);
}
bool is_sleeping() {
  return !digitalRead(SLEEP);
}

void send_status() {
  if (millis() - status_throttle >= STATUS_THROTTLE) {
    stats["sensor_open"] = read_sensor_open();
    stats["sensor_close"] = read_sensor_close();
    stats["completed_steps"] = stepper.getStepsCompleted();
    stats["remaining_steps"] = stepper.getStepsRemaining();
    stats["direction_wanted"] = (digitalRead(READ_DIRECTION_PIN) == OPENING ? "Opening" : "Closing");
    stats["direction"] = (stepper.getDirection() == 1 ? "Opening" : "Closing");
    stats["sleeping"] = is_sleeping();
    stats["uptime"] = millis();
    serializeJson(stats, Serial);
    status_throttle = millis();
  }
}

void read_direction() {
  if (digitalRead(READ_DIRECTION_PIN) == OPEN && !read_sensor_open()) {
    if (stepper.getDirection() == CLOSING || read_sensor_close() && is_sleeping()) {
      stepper.startRotate(OPENING * MAX_ROTATE_DEGREES);
      stepper.enable();
    }
  }
  if (digitalRead(READ_DIRECTION_PIN) == CLOSE && !read_sensor_close()) {
    if (stepper.getDirection() == OPENING || read_sensor_open() && is_sleeping()) {
      stepper.startRotate(CLOSING * MAX_ROTATE_DEGREES);
      stepper.enable();
    }
  }
}

void check_endstop() {
  if (stepper.getDirection() == OPENING && read_sensor_open()) {
    stepper.stop();
  }
  if (stepper.getDirection() == CLOSING && read_sensor_close()) {
    stepper.stop();
  }
}

void loop() {
    check_endstop();
    read_direction();

    // motor control loop - send pulse and return how long to wait until next pulse
    unsigned wait_time_micros = stepper.nextAction();

    // 0 wait time indicates the motor has stopped
    if (wait_time_micros <= 0) {
        stepper.disable();       // comment out to keep motor powered
        send_status();
    }

    // (optional) execute other code if we have enough time
    if (wait_time_micros > 10){
        send_status();
    }
}
