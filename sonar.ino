#include <Servo.h>

#define SERVO_PIN 10
#define TRIG_PIN 11
#define ECHO_PIN 12
#define MIN_ANGLE 30
#define MAX_ANGLE 150
#define DELAY_SERVO 5 // ms, velocidade que o servinho gira
#define DELAY_TRIG_LOW 2 // microseconds, tempo que o trigger do sensor fica low
#define DELAY_TRIG_HIGH 10 // microseconds
#define SOUND_SPEED 0.0343 // cm/microseconds

Servo servo;

void setup() {
    Serial.begin(9600);

    servo.attach(SERVO_PIN);

    pinMode(TRIG_PIN, OUTPUT);
    pinMode(ECHO_PIN, INPUT);
}


void loop() {
    for(int i = MIN_ANGLE; i < MAX_ANGLE; i++) {
        servo.write(i);
        delay(DELAY_SERVO);

        // angulo,distancia.angulo,distancia...
        Serial.print(i); // angle
        Serial.print(',');
        Serial.print(calcDist());
        Serial.print('.');
    }
    for(int i = MAX_ANGLE; i > MIN_ANGLE; i--) {
        servo.write(i);
        delay(DELAY_SERVO);

        Serial.print(i); // angle
        Serial.print(',');
        Serial.print(calcDist());
        Serial.print('.');
    }
}

int calcDist() {
    long duration;

    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(DELAY_TRIG_LOW);
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(DELAY_TRIG_HIGH);
    
    duration = pulseIn(ECHO_PIN, HIGH); // microseconds
    return (int) (SOUND_SPEED * ((double) duration/2)); // cm
}
