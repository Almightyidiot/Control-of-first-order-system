#include <Controllino.h>

#define DAC_0 CONTROLLINO_AO0  
#define ADC_0 CONTROLLINO_AI12 
#define fan CONTROLLINO_AO1
#define SAMPLING_TIME 100


// PID parameters
 float Kp = 0;
 float Ki = 0;
 float Kd = 0;
unsigned long lastUpdateTime = 0;
unsigned long startTime = 0;
// PID variables
 float setpoint = 0;    
 float error = 0, prev_error = 0;
 float integral = 0, derivative = 0;
 float control_output = 0;
bool pidReceived = false;

void setup() {
Serial.begin(9600);
Serial.println("Time (s), Setpoint (°C), Control Output (V), System Output (V)");
  pinMode(DAC_0, OUTPUT);
  pinMode(ADC_0, INPUT);
  startTime = millis();
  delay(1000);
}

void loop() {
   if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    if (command == "RESET") {
      resetParameters();
   
    }
    else {
      UpdateParameters(command);
    }
  }

  if (pidReceived && (millis() - lastUpdateTime >= SAMPLING_TIME)) {
    lastUpdateTime = millis();
    updateControl();
  }
}

void resetParameters() {
  Kp = Ki = Kd = setpoint = error = prev_error = integral = derivative = control_output = 0;
  analogWrite(DAC_0, 0);
  analogWrite(fan,10);
  pidReceived = false;
  startTime = millis();
}
void UpdateParameters(String data) {
    int numParams = 4;
    float values[numParams];
    int start = 0;
    int end = -1;
    for (int i = 0; i < numParams; i++) {
        end = data.indexOf(',', start);
        if (end == -1) end = data.length();  // Handle last value
        values[i] = data.substring(start, end).toFloat();
        start = end + 1;
    }
    if (!isnan(values[0]) && !isnan(values[1]) && !isnan(values[2]) && !isnan(values[3])) {

        setpoint = values[0] / 10.0 ;
        Kp = values[1];
        Ki = values[2];
        Kd = values[3];
        pidReceived = true; 
    } else {
        Serial.println(" failed to update: ");
    }
    error = prev_error = integral = derivative =control_output =  0;
}

void updateControl() {
  int adc_value = analogRead(ADC_0);
  float system_output = (adc_value / 1023.0) * 10.0;
  float system_temp = 10 * system_output;
  error = setpoint - system_output;
  derivative = (error - prev_error) / (SAMPLING_TIME / 1000.0);
  integral += error * (SAMPLING_TIME / 1000.0);
  integral = constrain(integral, -10.0, 10.0);
  control_output = (Kp * error) + (Ki * integral) + (Kd * derivative);
  control_output = constrain(control_output, 0, 10.0);
  int pwm_value = (int)((control_output / 10.0) * 255.0);
 
  if (error < 0) {
    analogWrite(DAC_0, pwm_value);
    int fan_value = (int)((1.0 / 10.0) * 255.0);
    analogWrite(fan,fan_value);
    }
    else{
  analogWrite(DAC_0, pwm_value);
  analogWrite(fan,0);
  }
  prev_error = error;

  unsigned long currentTime = millis() - startTime;
  Serial.print(currentTime / 1000.0, 2);
  Serial.print(",");
  Serial.print(setpoint * 10.0);
  Serial.print(",");
  Serial.print((pwm_value / 255.0) * 10.0);
  Serial.print(",");
  Serial.println(system_temp);
}
