#include "Servo.h"


int trigpin = 2;//appoint trigger pin
int echopin = 3;//appoint echo pin
int trigpin_2 = 6;
int echopin_2 = 5;


Servo myservo;  // create servo object to control a servo 
Servo myservo_2;  // create servo object to control a servo 
int pos = 0;    // variable to store the servo position 
int pos2=0;
Ultrasonic ultrasonic(trigpin,echopin);
Ultrasonic ultrasonic_2(trigpin_2,echopin_2);

void setup()
{
	Serial.begin(9600);//set Serial Baud rate
        myservo.attach(4);// attaches the servo on pin 4 to the servo object 
        myservo_2.attach(8);
        Serial.println("System is starting!!!\n");
        
}

void loop(void *p)
{      
            
            float cmdistance; //left
            float cmdistance_2; //right
            long microsec = ultrasonic.timing();
            long microsec_2 = ultrasonic_2.timing();
            cmdistance = ultrasonic.CalcDistance(microsec,Ultrasonic::CM);//this result unit is centimeter
            cmdistance_2 = ultrasonic_2.CalcDistance(microsec_2,Ultrasonic::CM);//this result unit is centimeter

          { 
            if(cmdistance>40 && cmdistance<60)
              {
                pos=180;
                myservo.write(pos);
                delay(300);
                pos=0;
                delay(300);
              }
              else
                if (cmdistance<40)
                 {
                    pos=180;             
                    myservo.write(pos);                  
                    delay(100);
                    pos=0;
                    myservo.write(pos);            
                    delay(100);
                 }
		  else
		    pos=0; 
		    myservo.write(pos);
          }

          {
            if(cmdistance_2>40 && cmdistance_2<60)
            {
              pos2=180;
             myservo_2.write(pos2);
             delay(300);
              pos2=0;
             myservo_2.write(pos2);
              delay(300);
             }
            else
              if (cmdistance_2<40)
                 {
                   pos2=180;
                    myservo_2.write(pos2);
                    pos2=0;
                    myservo_2.write(pos2);                    
                    delay(100);
                 }
		  else
		    pos2=0; 
	    myservo_2.write(pos2);
          }

}