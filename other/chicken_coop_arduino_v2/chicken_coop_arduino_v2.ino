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

// Debounce configuration
#define DEBOUNCE_DELAY 20  // 20ms debounce time

// Debounce state tracking
unsigned long lastSensorOpenDebounce = 0;
unsigned long lastSensorCloseDebounce = 0;
unsigned long lastDirectionDebounce = 0;
bool lastSensorOpenState = 1;
bool lastSensorCloseState = 1;
bool lastDirectionState = 1;

// Debounce function for noise-resistant sensor reading
bool debouncedRead(int pin, bool &lastState, unsigned long &lastDebounce) {
  bool reading = digitalRead(pin);

  // If the reading has changed, reset the debounce timer
  if (reading != lastState) {
    lastDebounce = millis();
    lastState = reading;
  }

  // Only accept the new reading if it has been stable for DEBOUNCE_DELAY
  if ((millis() - lastDebounce) > DEBOUNCE_DELAY) {
    return reading;
  }

  // Return the last stable state if not enough time has passed
  return lastState;
}

void setup() {
    Serial.begin(115200);
    stepper.begin(RPM);
    stepper.setMicrostep(MICROSTEP);

    // Configure sensor pins with pull-up resistors to prevent floating inputs
    pinMode(SENSOR_OPEN_PIN, INPUT_PULLUP);
    pinMode(SENSOR_CLOSED_PIN, INPUT_PULLUP);
    pinMode(READ_DIRECTION_PIN, INPUT_PULLUP);
}

bool read_sensor_open() {
  return !debouncedRead(SENSOR_OPEN_PIN, lastSensorOpenState, lastSensorOpenDebounce);
}
bool read_sensor_close() {
  return !debouncedRead(SENSOR_CLOSED_PIN, lastSensorCloseState, lastSensorCloseDebounce);
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
    stats["direction_wanted"] = (debouncedRead(READ_DIRECTION_PIN, lastDirectionState, lastDirectionDebounce) == OPENING ? "Opening" : "Closing");
    stats["direction"] = (stepper.getDirection() == 1 ? "Opening" : "Closing");
    stats["sleeping"] = is_sleeping();
    stats["uptime"] = millis();
    serializeJson(stats, Serial);
    Serial.println();  // Add newline for Python parser
    status_throttle = millis();
  }
}

void read_direction() {
  bool direction = debouncedRead(READ_DIRECTION_PIN, lastDirectionState, lastDirectionDebounce);

  if (direction == OPEN && !read_sensor_open()) {
    if (stepper.getDirection() == CLOSING || read_sensor_close() && is_sleeping()) {
      stepper.startRotate(OPENING * MAX_ROTATE_DEGREES);
      stepper.enable();
    }
  }
  if (direction == CLOSE && !read_sensor_close()) {
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
        // Keep motor powered when door is open (holds position against gravity)
        // Disable motor when closed
        if (read_sensor_close()) {
            stepper.disable();
        }
        // If door is open: motor stays enabled to hold position
        send_status();
    }

    // (optional) execute other code if we have enough time
    if (wait_time_micros > 10){
        send_status();
    }
}
