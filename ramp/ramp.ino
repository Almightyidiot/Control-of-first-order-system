#include <Controllino.h>
#define CONTROLLINO_AO0 //input
#define CONTROLLINO_AO1  // fan
#define CONTROLLINO_AI12   // output 
#define SAMPLING_TIME 100

float currentTime=0;
void contr(double analogOutVoltage)
{
  int outputvoltage = analogRead(CONTROLLINO_AI12);  // Read 0-1023
  double outputVoltage = (outputvoltage / 1023.0 ) * 10.0 ;  // Convert to 0-10V 
  double input_voltage = (analogOutVoltage / 10.0) * 255.0;
  int analogOut = (int) input_voltage;
  int fan = (int)((1.0 / 10.0) * 255.0);
  analogWrite(CONTROLLINO_AO0, analogOut);
  analogWrite(CONTROLLINO_AO1, fan);
   

  Serial.print(currentTime); 
  Serial.print(",");
  Serial.print(analogOutVoltage, 2); // Input voltage in V
  Serial.print(",");
  Serial.print(outputVoltage, 2);// Output voltage in V
  Serial.println();
  delay(SAMPLING_TIME);
  currentTime += (SAMPLING_TIME / 1000.0);
}

void loop(void) {
  double analogOutVoltage;
  if (currentTime <= 300) { 
    for (analogOutVoltage = 0; analogOutVoltage <= 5.0; analogOutVoltage += 0.5)
      contr(analogOutVoltage);
    for (analogOutVoltage = 5.0; analogOutVoltage >= 0; analogOutVoltage -= 0.5)
      contr(analogOutVoltage);
  } else {
    analogWrite(CONTROLLINO_AO0, 0);
    analogWrite(CONTROLLINO_AO1, 0);
  }
}

void setup(void)
{
  Serial.begin(9600);
  Serial.println("Current_Time(s),Input Voltage (V),Output Voltage (V)");
 // pinMode(CONTROLLINO_D0, OUTPUT);
  //digitalWrite(CONTROLLINO_D0, LOW);

  pinMode(CONTROLLINO_AO0, OUTPUT);
  pinMode(CONTROLLINO_AO1, OUTPUT);
  pinMode(CONTROLLINO_AI12, INPUT);
  //pinMode(CONTROLLINO_AI13, INPUT);
  delay(5000);
}