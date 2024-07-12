const int relayPins[] = {2, 3, 4, 5, 6, 7, 8};
const int numRelays = sizeof(relayPins) / sizeof(relayPins[0]); // Calculate the number of relays
String str;
char buf[16];

void allOff() {
  for (int i = 0; i < numRelays; i++) {
    digitalWrite(relayPins[i], HIGH);
  }
}

void setup() {
  for (int i = 0; i < numRelays; i++) {
    pinMode(relayPins[i], OUTPUT); // Initialize each relay pin as an output
    digitalWrite(relayPins[i], HIGH); // Initially, all relays are turned off (HIGH for low-level trigger)
  }
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    Serial.readStringUntil('\r').toCharArray(buf,sizeof(buf));
    if (strcmp(buf, "0") == 0 ) {
      allOff();
      digitalWrite(relayPins[0], LOW);
    } else if (strcmp(buf, "1") == 0) {
      allOff();
      digitalWrite(relayPins[1], LOW);
    } else if (strcmp(buf, "2") == 0) {
      allOff();
      digitalWrite(relayPins[2], LOW);
    } else if (strcmp(buf, "3") == 0) {
      allOff();
      digitalWrite(relayPins[3], LOW);
    } else if (strcmp(buf, "4") == 0) { 
      allOff(); 
      digitalWrite(relayPins[4], LOW);
    } else if (strcmp(buf, "5") == 0) {
      allOff();
      digitalWrite(relayPins[5], LOW);
    } else if (strcmp(buf, "6") == 0) {
      allOff();
      digitalWrite(relayPins[6], LOW);
    } else {
      allOff();
    }
  }
}
