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


void setup() {
  // put your setup code here, to run once:

  




}

void loop() {
  // put your main code here, to run repeatedly:

}
