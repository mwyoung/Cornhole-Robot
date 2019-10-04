/*
   Blink
   Turns on an LED on for one second, then off for one second, repeatedly.

   This example code is in the public domain.
 */

// Pin 13 has an LED connected on most Arduino boards.
// give it a name:
int led = 13;
String inputStr;
char input;
bool badInput = false;

// the setup routine runs once when you press reset:
void setup() {                
    // initialize the digital pin as an output.
    pinMode(led, OUTPUT);     
    Serial.begin(9600);
    Serial.write("Ready\n");
}

// the loop routine runs over and over again forever:
void loop() {
    digitalWrite(led, HIGH);
    if (badInput == false) {
        delay(500);
    }
    else {
        delay(2000);
    }
    digitalWrite(led, LOW);
    delay(1000);
}

// serial interrupts - single char
void serialEvent() { 
    inputStr = ""; 
    while (Serial.available()){
        input = (char)Serial.read();
        inputStr += input;
    }
    
    //if (inputStr[0] == 'A' || inputStr[0] == 'a') {
    //    Serial.write("tx a/A"); 
    //    badInput = false;
    //}
    if (inputStr[0] == 'l'){
        Serial.write("launch\n");
        badInput = false;
    }
    else if (inputStr[0] == 'o'){
        Serial.write("load\n");
        badInput = false;
    }
    else {
        Serial.write("tx ?\n"); 
        badInput = true;
    }
    Serial.flush();
}
