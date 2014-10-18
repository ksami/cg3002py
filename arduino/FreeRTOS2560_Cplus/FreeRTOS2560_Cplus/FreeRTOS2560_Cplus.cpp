
#include <avr/io.h>
#include <FreeRTOS.h>
#include <task.h>
#include <Arduino.h>
#include <queue.h>
#include "Servo.h"
#include "Ultrasonic.h"
#include "delay.h"
#include "microsmooth.h"

#define STACK_DEPTH 256

//Mapping for flex sensor

int flexpin = A0;

//Mapping of corresponding sonar trigger and echo pins

int trigpin_1 = 2;
int echopin_1 = 3;

int trigpin_2 = 4;
int echopin_2 = 5;

//Creating objects for sonar and servo

Ultrasonic ultrasonic_1(trigpin_1, echopin_1);
Ultrasonic ultrasonic_2(trigpin_2, echopin_2);

//Attach corresponding servo pins

//Servo servo_1;
//Servo servo_2;

//Sonar variables

long microsec_1 = 0;
long microsec_2 = 0;
float distance_1 = 0;
float distance_2 = 0;

//Sonar Filtering variables
const int arraysize = 5;
int median;

int reading_1[arraysize];
int reading_2[arraysize];

int temp_1[arraysize];
int temp_2[arraysize];

int index_1;
int index_2;

uint16_t *history_1;
uint16_t *history_2;

bool start = false;

//QuickSort for Sonar Filtering

void quicksort(int x[], int first, int last){
	int pivot, j, temp, i;

	if(first<last){
		pivot=first;
		i=first;
		j=last;

		while(i<j){
			while(x[i] <= x[pivot] && i<last)
			i++;
			while(x[j] > x[pivot])
			j--;
			if(i<j){
				temp=x[i];
				x[i]=x[j];
				x[j]=temp;
			}
		}

		temp=x[pivot];
		x[pivot]=x[j];
		x[j]=temp;
		quicksort(x, first, j-1);
		quicksort(x, j+1, last);

	}
}

//Setup for Sonar and Servo

void ssSetup()
{
	history_1 = ms_init(SGA);
	history_2 = ms_init(SGA);
	
	//index_1 = 0;
	//index_2 = 0;
	//median = (arraysize/2) + 1;
	
	//sonar1_ready = false;
	//sonar2_ready = false;
	/*
	for(int i=0; i<arraysize; i++) {
	reading_1[i] = 0;
	reading_2[i] = 0;
	}
	*/
	//servo_1.attach(7);
	//servo_2.attach(8);
	
	//servo_1.write(0);
	//servo_2.write(0);
}

//Sonar and Servo Tasks

void ssTask(void* p)
{
	
	while (1) {
		
		if (start) {
			
			//Left Sonar
			//Obtains time of travel for sound.
			microsec_1 = ultrasonic_1.timing();
			//Updates distance in cm.
			distance_1 = ultrasonic_1.CalcDistance(microsec_1, Ultrasonic::CM);
			
			distance_1 = sma_filter(distance_1, history_1);
			
			//memcpy(temp_1, reading_1, sizeof(reading_1));
			//quicksort(temp_1, 0, arraysize-1);
			//distance_1 = temp_1[median];
			
			//Servo Left
			
			Serial.print("L: ");
			Serial.print((int) distance_1, DEC);
			
			if ((distance_1 > 0.1) && (distance_1 <= 60)) {
				digitalWrite(7, HIGH);
				delayInMilliSeconds(200);
				digitalWrite(7, LOW);
				delayInMilliSeconds(200);
				/*
				servo_1.write(10);
				delayInMilliSeconds(50);
				servo_1.write(0);
				delayInMilliSeconds(50);
				*/
			}
			

			//Right Sonar
			//Obtains time of travel for sound.
			microsec_2 = ultrasonic_2.timing();
			//Updates distance in cm.
			distance_2 = ultrasonic_2.CalcDistance(microsec_2, Ultrasonic::CM);
			
			distance_2 = sma_filter(distance_2, history_2);
			
			//memcpy(temp_2, reading_2, sizeof(reading_1));
			//quicksort(temp_2, 0, arraysize-1);
			//distance_2 = temp_2[median];
			
			//Servo Right

			Serial.print("     ");
			Serial.print("R: ");
			Serial.print((int) distance_2, DEC);
			Serial.println();
			
			if ((distance_2 > 0.1) && (distance_2 <= 60)) {
				digitalWrite(8, HIGH);
				delayInMilliSeconds(200);
				digitalWrite(8, LOW);
				delayInMilliSeconds(200);
				/*
				servo_2.write(10);
				delayInMilliSeconds(50);
				servo_2.write(0);
				delayInMilliSeconds(50);
				*/
			}
		}
		vTaskDelay(200);
	}
}



void flexTask(void* p) {
	while (1) {
		int readRaw = analogRead(flexpin);
		Serial.println(readRaw);
		
		//Readings are remapped from 0 to 10.
		int readMap = map(readRaw, 520, 600, 0, 10);
		Serial.println(readMap);
		
		if (readMap > 10) {
			//on
			start = true;
			Serial.println("ON");
		}
		
		else {
			start = false;
			Serial.println("OFF");
			//on
		}
		vTaskDelay(100);
	}
}

void testTask(void* p) {
	while (1) {
		Serial.println("hello muneer");
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
	
	Serial.begin(9600);
	Serial.println("START");
	
	ssSetup();
	
	pinMode(7, OUTPUT);
	pinMode(8, OUTPUT);
	
	TaskHandle_t taskSS;

	xTaskCreate(ssTask, "ssTask", STACK_DEPTH, NULL, 5, &taskSS);
	//xTaskCreate(task2, "test", STACK_DEPTH, NULL, 5, NULL);
	xTaskCreate(flexTask, "Flex", STACK_DEPTH, NULL, 5, NULL);

	vTaskStartScheduler();
}



/*
for (int i=0; i < arraysize; i++) {
temp_1[i] = reading_1[i];
}

quicksort(temp_1, 0, arraysize-1);

distance_1 = temp_1[median];
*/

/*
// left sensor readings
if(distance_1 <= 400 && distance_1 > 0)
reading_1[(index_1++)%arraysize] = distance_1;

// right sensor readings
//if(distance_2 <= 400 && distance_2 > 0)
//reading_2[(index_2++)%arraysize] = distance_2;

if((index_1 >= arraysize)) { initFlag = 1; }

//Servo Left
if(initFlag == 1) {
//Serial.println("left");
for(int i=0;i<10;i++)
//Serial.println((int)reading_1[i]);
distance_1 = 0;
for (int i=0; i < arraysize; i++) {
distance_1 += reading_1[i];
}
distance_1 /= arraysize;
//Serial.print("avg l: ");
//Serial.println((int)distance_1);

//distance_2 = 0;
//for (int i=0; i < arraysize; i++) {
//distance_2 += reading_2[i];
//}
//distance_2 /= arraysize;
*/