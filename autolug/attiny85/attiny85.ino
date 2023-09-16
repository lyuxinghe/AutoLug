#define MOT1 PIN_PB1
#define MOT2 PIN_PB4
#define I2C_ADDR 0x08;
#include<TinyWireS.h>

void handleReceive(uint8_t len){
    uint8_t motor1 = TinyWireS.receive();
    uint8_t motor2 = TinyWireS.receive();
    analogWrite(MOT1, motor1);
    analogWrite(MOT2, motor2);
    TinyWireS.send(motor1);
    TinyWireS.send(motor2);
}

void setup(){
    TinyWireS.begin(0x08);
    TinyWireS.onReceive(handleReceive);
    pinMode(MOT1, OUTPUT);
    pinMode(MOT2, OUTPUT);
    analogWrite(MOT1, 0);
    analogWrite(MOT2, 0);
}

void loop(){
  delay(1000);
}