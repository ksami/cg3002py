#include <avr/io.h>
#include <FreeRTOS.h>
#include <task.h>
#include <Arduino.h>
#include <queue.h>
#include "Servo.h"
#include "Ultrasonic.h"
#include "delay.h"
#include "microsmooth.h"
#include "XBee.h"
#include "que.h"

#define STACK_DEPTH 256

// Mapping for flex sensor
int flexpin = A0;

//counter for flex sensor
unsigned int counterForFlex[2];

// Mapping of corresponding sonar trigger and echo pins
int trigpin_1 = 2;
int echopin_1 = 3;

int trigpin_2 = 4;
int echopin_2 = 5;

int sonarpin_1 = 7;
int sonarpin_2 = 8; 

// Creating objects for sonar and servo
Ultrasonic ultrasonic_1(trigpin_1, echopin_1);
Ultrasonic ultrasonic_2(trigpin_2, echopin_2);

// Sonar variables
long microsec_1 = 0;
long microsec_2 = 0;
float distance_1 = 0;
float distance_2 = 0;

// Comm stuff
#define DEVICE_READY 0
#define NAVI_READY 1
#define NAVI_END 2
#define OBSTACLE_DETECTED 3
#define RPI_ADDR 0
#define MAX_RPI_MSG_SIZE 5
#define PKG_INDEX 8

XBee xbee;
Que RxQ;

// Following are flags in our program
#define open false
#define close true
#define not_ack false
#define ack true 

bool handStatus = open;		// hand open/close => false/true
bool deviceRdy = not_ack;	// to check if arduino is connected to rpi
bool naviRdy = false;		// to check if rpi has sent the 'green' light for navi to start

// Writing to actuator(servo) whenever ard/pi detects obstacle
void writeToActuator(float left, float right) { //should change to constant val of 0-2 depending on distance
	
	if (naviRdy && deviceRdy && handStatus) { 
		
		//Sonar Left
		//Serial.print("L: ");
		//Serial.print((int) left, DEC);

		if ((left > 1) && (left <= 60)) {
			digitalWrite(sonarpin_1, HIGH);
			delayInMilliSeconds(500);
			digitalWrite(sonarpin_1, LOW);
			//delayInMilliSeconds(500);
		}
		
		//Serial.print("     R: ");
		//Serial.println((int) right, DEC);

		// Sonar right	
		if ((right > 1) && (right <= 60)) {
			digitalWrite(sonarpin_2, HIGH);
			delayInMilliSeconds(500);
			digitalWrite(sonarpin_2, LOW);
			//delayInMilliSeconds(500);
		}
	}
}

// Sonar and Servo Tasks
void ssTask(void* p)
{	
	Serial.println("IN SONAR TASK");
	while (1) {
		
		if (deviceRdy && handStatus == close) { 

			//Left Sonar
			//Obtains time of travel for sound.
			microsec_1 = ultrasonic_1.timing();
			//Updates distance in cm.
			distance_1 = ultrasonic_1.CalcDistance(microsec_1, Ultrasonic::CM);
			
			//Right Sonar
			//Obtains time of travel for sound.
			microsec_2 = ultrasonic_2.timing();
			//Updates distance in cm.
			distance_2 = ultrasonic_2.CalcDistance(microsec_2, Ultrasonic::CM);
			
			writeToActuator(distance_1, distance_2);
		}
		vTaskDelay(200);
	}
}

// Flex sensor task
void flexTask(void* p) {
	Serial.println("IN FLEX TASK");
	while (1) {
		
		if (deviceRdy) {
			int readRaw = analogRead(flexpin);
			//Serial.println(readRaw);
			int frameLen = 0;
			unsigned char outFrame[Q_SIZE];
			unsigned char outMsg[2];
			memcpy(outMsg, "4", 1);
		
			if (readRaw < 490 && handStatus == open) {
				if (counterForFlex[0] >= 5) {
					// send data to rpi to inform that hand has been closed for 2 cycles
					handStatus = close;
					memcpy(&outMsg[1], "1", 1);
					frameLen = xbee.Send(outMsg, 2, outFrame, RPI_ADDR);
					Serial1.write(outFrame, frameLen);
					Serial.println("ON");
					counterForFlex[0] = 0; //reset counter	
				}
				else {
					counterForFlex[0]++;	//increment counter
					counterForFlex[1] = 0;
				}
				
			} else if (readRaw >= 500 && handStatus == close) {
				if (counterForFlex[1] >= 5) {
					// send data to rpi to inform that hand has been opened for 2 cycles;
					handStatus = open;
					memcpy(&outMsg[1], "0", 1);
					frameLen = xbee.Send(outMsg, 2, outFrame, RPI_ADDR);
					Serial1.write(outFrame, frameLen);
					Serial.println("OFF");
					counterForFlex[1] = 0; //reset counter	
				}
				else {
					counterForFlex[1]++;	//reset counters
					counterForFlex[0] = 0;
				}
			}
			else {
				counterForFlex[0] = 0;
				counterForFlex[1] = 0;
			}
		}
		vTaskDelay(200);
	}
}

// Task to receive data from RPi
void xbeeTask(void* p) {
	Serial.println("IN XBEE TASK");
	while (1) {

		int queueLen = 0;
		int delPos = 0;
		
		while (Serial1.available() > 0) {
			unsigned char in = (unsigned char)Serial1.read();
			Serial.println(in, HEX);
			if (!RxQ.Enqueue(in)) {
				break;
			}
		}

		queueLen = RxQ.Size();
		for (int i=0;i<queueLen;i++) {
			if (RxQ.Peek(i) == 0x7E) {
				unsigned char checkBuff[Q_SIZE];
				unsigned char msgBuff[Q_SIZE];
				int checkLen = 0;
				int msgLen = 0;
				checkLen = RxQ.Copy(checkBuff, i);
				msgLen = xbee.Receive(checkBuff, checkLen, msgBuff);
			
				if (msgLen > 0) {
					unsigned char outMsg[MAX_RPI_MSG_SIZE];
					unsigned char outFrame[Q_SIZE];
					int frameLen = 0;
					int packageID = (char)msgBuff[PKG_INDEX] - '0';

					int ack_len = 0;
					
					switch(packageID) {
						case DEVICE_READY:
							memcpy(outMsg, "ACK", 3);
							deviceRdy = ack;
							ack_len = 3;
							break;
						case NAVI_READY:
							memcpy(outMsg, "ACK", 3);
							naviRdy = true;
							ack_len = 3;
							break;
						case NAVI_END:
							memcpy(outMsg, "ACK", 3);
							naviRdy = false;
							deviceRdy = not_ack;
							ack_len = 3;
							break;
						case OBSTACLE_DETECTED:
							memcpy(outMsg, "ACK", 3);
							// activate servos
							if(msgBuff[9] == 'L')
								Serial.println("left");
							else
								Serial.println("right");
							// str = msgBuff[10];
							//writeToActuator(left,right);
							ack_len = 3;
							break;
						default:
							// raise error ?
							break;
					}
					
					
					frameLen = xbee.Send(outMsg, ack_len, outFrame, RPI_ADDR);
					
					Serial1.write(outFrame, frameLen);
					i += msgLen;
					delPos = i;
				}
				
				else {
					if (i > 0) {
						delPos = i-1;
					}
				}
			}
		}

		RxQ.Clear(delPos);
		vTaskDelay(200);
	}
}

// Task for testing purpose
void testTask(void* p) {
	while (1) {
		////Serial.println("hello muneer");
		vTaskDelay(1000);
	}
}

void vApplicationIdleHook()
{
	// 	Do 	nothing.
}

int main()
{
	init();
	//deviceRdy = 1; // for debugging w/o rpi
	//naviRdy = 1; // for debugging w/o rpi
	Serial1.begin(9600);
	Serial.begin(9600);
	Serial.println("START");
	
	pinMode(7, OUTPUT);
	pinMode(8, OUTPUT);
	
	TaskHandle_t taskSS, taskFlex, taskXBee;
	xTaskCreate(ssTask, "ssTask", STACK_DEPTH, NULL, 5, &taskSS);
	xTaskCreate(flexTask, "Flex", STACK_DEPTH, NULL, 5, &taskFlex);
	xTaskCreate(xbeeTask,"xbeeTask", STACK_DEPTH*2, NULL, 5, &taskXBee);
	//xTaskCreate(task2, "test", STACK_DEPTH, NULL, 5, NULL);

	vTaskStartScheduler();
}