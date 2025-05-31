#include <Controllino.h>
#define SAMPLING_TIME 200
const float squareTime = 2.0;      // Square wave 
float currentTime=0;

void setup() {
  Serial.begin(9600);
  pinMode(CONTROLLINO_AO0, OUTPUT); 
  pinMode(CONTROLLINO_AO1, OUTPUT); 
  pinMode(CONTROLLINO_AI12, INPUT);   
  delay(2000);
  Serial.println("Input_Voltage,Output_Voltage");
}

void loop() {
  if (currentTime <= 600) {
  float CycleTime = currentTime;
  while (CycleTime >= squareTime) {
    CycleTime -= squareTime;  
  }

  long int analogOutVoltage;
  if (CycleTime < squareTime / 2) {  
    analogOutVoltage = 0;           
  } else {                             
    analogOutVoltage = 3000;              
  }

  long int analogOut = (255 * analogOutVoltage) / 10000;
  int fan = (int)((1.0 / 10.0) * 255);
  analogWrite(CONTROLLINO_AO0, analogOut);
  analogWrite(CONTROLLINO_AO1, fan);


  int ADC_O = analogRead(CONTROLLINO_AI12);  
  double outputVoltage = (ADC_O * 10.0) / 1023.0;  

  Serial.print(currentTime); 
  Serial.print(",");
  Serial.print(analogOutVoltage / 1000.0); 
  Serial.print(",");
  Serial.println(outputVoltage);

  delay(SAMPLING_TIME);
  currentTime += (SAMPLING_TIME / 1000.0);
} else {
    analogWrite(CONTROLLINO_AO0, 0); // Stop after 600 seconds
    analogWrite(CONTROLLINO_AO1, 10);
  }
}