#include <Servo.h>

//Electro magnet
#define en1 9
#define dr1 13
#define pwm1 11
#define eMgEn en1
#define eMgDr dr1
#define eMgPWM pwm1
#define eMagPin 7 

//Motor
#define en2 8
#define dr2 12
#define pwm2 10
#define mtrBtn 14 //A0
#define mtrEn en2
#define mtrDr dr2 
#define mtrPWM pwm2
#define mPWM pwm2
#define motorLimit en2 

#define s1p 5 
#define s2p 6
#define bbStart 5 

#define led 13

Servo servo1;
Servo servo2;
boolean elecMagnetState = LOW;
int8_t beanBag = 2;
int8_t bagButtonStatus = 0;
uint16_t limit = 0;
uint16_t pos;

String inputStr;
char input;

void servoMoveTo(int pos){
    servo1.write(pos); //move to a servo position for both
    servo2.write(pos);
}

void resetServos(){
	servo1.attach(s1p); //get current status
	servo2.attach(s2p);
	// Start servos on top
	servoMoveTo(bbStart);
    delay(800);
    servo1.detach();
	servo2.detach(); //stop from moving
    beanBag = 2;
}

void beanBagMove(uint16_t start, uint16_t limit, int8_t change){
    for (pos = start; pos <= limit; pos += change) {
        servoMoveTo(pos);
        delay(25);	
    }
}

void loadBeanBag(){
    if (beanBag == 2) {
        limit = 115; //most of the way there
    } 
    else {
        limit = 175; //full limit
    }

    servo1.attach(s1p);
    servo2.attach(s2p);
    delay(1); 
    Serial.print("lmt ");
    Serial.print(limit);
    // This for loop helps to load the bean bag
    beanBagMove(bbStart, limit, 1);   
 
    delay(500); 
    beanBagMove(limit, limit+5, -1);  
    delay(500); 
    beanBagMove(limit+5, limit, 1);   
    
    Serial.print("rvs\n"); 
   
    beanBagMove(limit, bbStart, -1); 

    servoMoveTo(bbStart); //just in case
    delay(30);
    
    servo1.detach();
	servo2.detach(); //stop from moving
        
    Serial.print("ld");
    if (beanBag == 2){ //print current bean bag
        Serial.print("2\n");
    }
    else if (beanBag == 1){
        Serial.print("1\n");
    }
    else {
        Serial.print("?\n");
    }
    
    beanBag -= 1;
    if (beanBag == 0){
        beanBag = 2; //reset bean bag
    }
}

void motor(boolean input1, boolean input2){
	digitalWrite(mtrEn, input1); //output to motor, enable
	digitalWrite(mtrDr, input2); //direction
}

void electroMagnet(boolean input1, boolean input2){
    //Serial.print("em\n");
	digitalWrite(eMgEn, input1); //enable emagnet
	digitalWrite(eMgDr, input2);
}

void unlockMagnet(){
    Serial.print("ul\n");
    elecMagnetState = LOW;
	//electromagnet release
	electroMagnet(LOW, LOW);
}

void lockMagnet(){
	if (digitalRead(eMagPin) == LOW){ //if switch is pressed
        //electromagnet on
	    electroMagnet(HIGH, HIGH); //turn on
        analogWrite(eMgPWM, 250); //almost full strength
        elecMagnetState = HIGH;
        Serial.print("lk\n");
    }
    else {
        unlockMagnet(); //switch not pressed
    }
}

void tighten(uint16_t time, bool stop){
	//increase strength
    Serial.print("wf\n");
	motor(LOW, LOW); //default to have button be true
	analogWrite(mtrPWM, 255);
    
    for (uint16_t i=0; i<time; i++){
        //if stopping and button not pressed
        if (stop == true && digitalRead(mtrBtn) == LOW){ 
            motor(LOW, LOW); //turn off
            i = time; //stop for loop
            Serial.print("bk\n");
        } 
        else {
            delay(1); //delay 1 ms, motor keeps turning
        }
    }	
		
	motor(LOW, LOW); //turn off
	analogWrite(mtrPWM, 0);
}
	
void loosen(uint16_t time, bool stop){
    //initial rotation direction
    Serial.print("wb\n");
    motor(HIGH, HIGH);
    analogWrite(mtrPWM, 255);
    
    for (uint16_t i=0; i<time; i++){
        //if stopping and button is pressed 
        if (stop == true && digitalRead(eMagPin) == LOW){ 
            motor(LOW, LOW); //turn off
            i = time; //stop for loop
            Serial.print("bk\n");
        } 
        else {
            delay(1); //delay 1 ms, motor keeps turning
        }
    }
    
    motor(LOW, LOW); //turn off
	analogWrite(mtrPWM, 0);
}
			
void launchBeanBag(){
   //activate electromagnet
   lockMagnet();
    if (elecMagnetState == LOW){
        return; //not locked
    }
    
    tighten(3600, true);

    unlockMagnet(); //unlock the magnet

    delay(1000);

    loosen(3400, true);
    //slight adjust
}

//setup overall structure
void setup(){
	pinMode(eMgEn, OUTPUT); //setup pins
	pinMode(eMgPWM, OUTPUT);
	pinMode(eMgDr, OUTPUT);
	pinMode(mtrEn, OUTPUT);
	pinMode(mtrDr, OUTPUT);
	pinMode(mtrPWM, OUTPUT);
    pinMode(mtrBtn, INPUT);
	pinMode(led, OUTPUT);
	
	pinMode(eMagPin, INPUT_PULLUP); //input
	digitalWrite(led,HIGH);

	Serial.begin(9600);

    resetServos();
    Serial.print("Ready\n");    

    beanBag = 2;    
	digitalWrite(led,LOW);
}

void loop(){
    delay(1); //infinite loop, always check for serial event
}

void serialEvent(){
    inputStr = ""; //clear string
    while (Serial.available()) {
        input = (char)Serial.read(); //read input
        inputStr += input;
    }

	digitalWrite(led,HIGH); //led high, doing command
    Serial.flush(); //clear serial

    switch(inputStr[0]){
        case 'l':
            Serial.print("rcv\n");
            launchBeanBag();
            Serial.print("ln\n"); //done
            break;
        case 'o':
            Serial.print("rcv\n"); //command received
            loadBeanBag();
            break;
        case 'r':
            resetServos();
            Serial.print("rl\n"); //reset to original state
            break;
        case 'c':
            if (elecMagnetState == LOW){ //toggle button
                lockMagnet();    
            }
            else {
                unlockMagnet(); 
            }
            break;
        case 'b': 
            loosen(250, false); //turn for 250 ms, no stopping
            break;
        case 'f':
            tighten(250, false); //turn for 250 ms, no stopping
            break;
        default:
            inputStr.concat("?\n"); //unknown command
            Serial.print(inputStr);
            break;
    }
	digitalWrite(led,LOW);
}
