// 10 July 2024 CMS code for ISUS DI water pump ARGO
// Program controlls 1 Lee pump witted with check balves to pump DIW through a flowcell fitted with a 40 psi
// backpressure regulator. Program is intended to be uploaded to the Arduino and run automatically and continuously
// when power is applied
// Arduino 1.0 version

// SELECT FLOW RATES FOR FILL & DISPENSE BY UNCOMMENTING FLOWRATE BELOW //

  // 4 possible flow rates in mL/min.  The high pulse rate delay = 500 usec for all 
const int Fill_LowPulse = 725;       // low pulse delay for 6 mL/min
// const int Fill_LowPulse = 2000;   // low pulse delay for 3 mL/min
// const int Fill_LowPulse = 3250;   // low pulse delay for 2 mL/min
// const int Fill_LowPulse = 7000;   // low pulse delay for 1 mL/min

  // 4 possible dispense rates in mL/min.  The high pulse rate delay = 500 usec for all
// const int Dispense_LowPulse = 725;    // low pulse delay for 6 mL/min
const int Dispense_LowPulse = 2000;      // low pulse delay for 3 mL/min
// const int Dispense_LowPulse = 3250;   // low pulse delay for 2 mL/min
// const int Dispense_LowPulse = 7000;   // low pulse delay for 1 mL/min

  // Pump Pins
int pump_pulse = 2;             // pin used to pulse the pump with EZINCH controller
int pump_direction = 3;         // pin used to change Lee pump direction with EZINCH controller
  // int position_sensor = 1;     // pin pused for position sensor out pin for the pump (A1)

  // Lee pump characteristics
const int Pump_Volume = 2750;             // 3000 uL pump but used 2750 in case it gets powered off at full fill
const int Pump_Steps = 8 * Pump_Volume;   // eight step resolution - both EZ inch dip switches must be in off position

//--------------------------------------------------------------------------------
// function creation

void Home_Pump() {
  // Sets pump to all the way down so that it can pump a standardized amount for other pumps

  int sensorValue;
  digitalWrite(pump_direction, LOW);   //fill pump direction in
  Serial.println("Filling Pump a little bit");
  for(int k = 1; k<2000; k++)    // 250ul
  {
    //Serial.println("Filling pump a little bit");
    digitalWrite(pump_pulse, HIGH);
    delayMicroseconds(500);
    digitalWrite(pump_pulse, LOW);
    delayMicroseconds(7000);
  }

  digitalWrite(pump_direction, HIGH);  //out direction
  Serial.println("going to pump out");
  sensorValue = analogRead(A1);        // read position sensor
  Serial.println("START");
  Serial.println(sensorValue);
  do {
    digitalWrite(pump_pulse, HIGH);
    delayMicroseconds(500);
    digitalWrite(pump_pulse, LOW);
    delayMicroseconds(7000);
    sensorValue = analogRead(A1);        // read position sensor
    Serial.println(sensorValue);
  } while (sensorValue > 100);
  delay(1000);
  Serial.println("Pump is home");

}

//--

void Fill_And_Dispense_Pump(){
  // Repeated code to fill and dispense the set amount of water at set fill and pump rates

  // fill part of program
  for (int m=1; m<= Pump_Steps; m++)
  {
    digitalWrite(pump_direction, LOW);   //fill pump direction (in)
    digitalWrite(pump_pulse, HIGH);
    delayMicroseconds(500);
    digitalWrite(pump_pulse, LOW);
    delayMicroseconds(Fill_LowPulse);

  }
  delay(1000);
  //dispense part of program
  int sensorValue;
  digitalWrite(pump_direction, HIGH);      // out direction
  sensorValue = analogRead(A1);            // read position sensor
  do{
    digitalWrite(pump_pulse, HIGH);
    delayMicroseconds(500);
    digitalWrite(pump_pulse, LOW);
    delayMicroseconds(Dispense_LowPulse);
    sensorValue = analogRead(A1);            // read position sensor
    Serial.println(sensorValue);
  } while (sensorValue > 100);
  delay (1000);

}

void setup() {
  // put your setup code here, to run once:

  Serial.begin(9600);

  pinMode(pump_pulse, OUTPUT);        // declare Pump_pulse as output
  pinMode(pump_direction, OUTPUT);    // declare Pump_direction as output

  Home_Pump();

}

void loop() {
  // put your main code here, to run repeatedly:
  Fill_And_Dispense_Pump();

}

