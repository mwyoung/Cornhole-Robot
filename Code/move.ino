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

#define led 13

Servo servo1;
Servo servo2;
boolean elecMagnetState = LOW;
int beanBag = 2;
int bagButtonStatus = 0;
int limit = 0;
int pos;

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
	servoMoveTo(0);
    delay(800);
    servo1.detach();
	servo2.detach(); //stop from moving
    beanBag = 2;
}

void loadBeanBag(){
    if (beanBag == 2) {
        limit = 120; //most of the way there
    } 
    else {
        limit = 180; //full limit
    }

    servo1.attach(s1p);
    servo2.attach(s2p);
    delay(1); 
    Serial.print("limit ");
    Serial.println(limit);
    // This for loop helps to load the bean bag
    for (pos = 0; pos <= limit; pos += 1) {
        //pos_other = 180 - pos; 
        servoMoveTo(pos);
        delay(20);	
    }
    
    delay(500); 

    Serial.println("reverse"); 
    resetServos(); //go to original position
        
    Serial.write("ld");
    if (beanBag == 2){ //print current bean bag
        Serial.write("2\n");
    }
    else if (beanBag == 1){
        Serial.write("1\n");
    }
    else {
        Serial.write("?\n");
    }
    
    beanBag--;
    if (beanBag == 0){
        beanBag = 2; //reset bean bag
    }
}

void motor(boolean input1, boolean input2){
	digitalWrite(mtrEn, input1); //output to motor, enable
	digitalWrite(mtrDr, input2); //direction
}

void electroMagnet(boolean input1, boolean input2){
    //Serial.write("em\n");
	digitalWrite(eMgEn, input1); //enable emagnet
	//digitalWrite(eMgDr, input2);
}

void unlockMagnet(){
    Serial.write("ul\n");
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
        Serial.write("lk\n");
    }
    else {
        unlockMagnet(); //switch not pressed
    }
}

void tighten(uint16_t time){
	//increase strength
    Serial.write("wf\n");
	motor(HIGH, LOW);
	analogWrite(mtrPWM, 255);
    
    for (uint16_t i=0; i<time; i++){
        if (digitalRead(mtrBtn) == LOW){ //if button is not pressed
            //stop
            i = time;
            Serial.write("bk\n");
        } 
        else {
            delay(1); //delay 1 ms, motor keeps turning
        }
    }	
		
	motor(LOW, LOW); //turn off
	analogWrite(mtrPWM, 0);
}
	
void loosen(uint16_t time){
    //initial rotation direction
    Serial.write("wb\n");
    motor(HIGH, HIGH);
    analogWrite(mtrPWM, 255);
    delay(time); //winds back
    
    motor(LOW, LOW); //turn off
	analogWrite(mtrPWM, 0);
}
			
void launchBeanBag(){
   //activate electromagnet
   lockMagnet();
    if (elecMagnetState == LOW){
        return; //not locked
    }
    
    tighten(3500);

    unlockMagnet(); //unlock the magnet

    delay(1000);

    loosen(3500);
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
    Serial.write("Ready\n");    

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
            Serial.write("rcv\n");
            launchBeanBag();
            Serial.write("ln\n"); //done
            break;
        case 'o':
            Serial.write("rcv\n"); //command received
            loadBeanBag();
            break;
        case 'r':
            resetServos();
            Serial.write("rl\n"); //reset to original state
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
            loosen(250); //turn for 250 ms 
            break;
        case 'f':
            tighten(250); //turn for 250 ms
            break;
        default:
            inputStr.concat("?\n"); //unknown command
            Serial.print(inputStr);
            break;
    }
	digitalWrite(led,LOW);
}
