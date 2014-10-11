#include <avr/io.h>
#include <FreeRTOS.h>
#include <task.h>
#include <Arduino.h>
#include <queue.h>
#include "Ultrasonic.h"

#define STACK_DEPTH 512

TaskHandle_t t1, t2, t3, t4;

QueueHandle_t qh = 0;

int _trigPin = 2;//appoint trigger pin
int _EchoPin = 3;//appoint echo pin
//float _cmDivison = 27.6233;
float _cmDivison = 13;

void printInt(int num) {
	int last_digit = num % 10;
	if(num > 10)
	printInt(num/10);
	Serial.print(last_digit, DEC);
}


void testTask(void* p)
{
	
	//Serial.print("a");
	while (1) {

		Serial.print("b");
		
		float cmdistance; //left
		
		digitalWrite(_trigPin, LOW);
		vTaskDelay(2);
		digitalWrite(_trigPin, HIGH);
		vTaskDelay(10);
		digitalWrite(_trigPin, LOW);
		long microsec = pulseIn(_EchoPin, HIGH);
		cmdistance = microsec / _cmDivison / 2.0;
		int test = (int) cmdistance;
		
		if (test >= 100) {
			digitalWrite(10, HIGH);
		}
		else {
			digitalWrite(10, LOW);
		}
		
		printInt(test);
		Serial.print('\n');

		digitalWrite(12, HIGH);
	}
}

void task_tx(void* p)
{
	int myInt = 0;
	while(1)
	{
		myInt++;
		vTaskDelay(3000);
		if(!xQueueSend(qh, &myInt, 500)) {
			//puts("Failed to send item to queue within 500ms");
		}
		else {
			digitalWrite(12, HIGH);
			vTaskDelay(250);
			digitalWrite(12, LOW);
		}
		vTaskDelay(1000);
	}
}

void task_rx(void* p)
{
	int myInt = 0;
	while(1)
	{
		if(!xQueueReceive(qh, &myInt, 1000)) {
			//puts("Failed to receive item within 1000 ms");
		}
		else {
			digitalWrite(11, HIGH);
			vTaskDelay(250);
			digitalWrite(11, LOW);
			//printf("Received: %u\n", myInt);
		}
	}
}

void task1(void* p)
{
	while (1) {
		digitalWrite(12, HIGH);
		vTaskDelay(1000000);
		digitalWrite(12, LOW);
		vTaskDelay(1000000);
	}
}

void task2(void* p)
{
	while (1) {
		digitalWrite(11, HIGH);
		vTaskDelay(1000000);
		digitalWrite(11, LOW);
		vTaskDelay(1000000);
	}
}

void Servotask(void *p)
{
	while (1) {
		
		digitalWrite(6, HIGH);
		vTaskDelay(15);
		digitalWrite(6, LOW);
		vTaskDelay(185);
		
		vTaskDelay(1000);
		
		digitalWrite(6, HIGH);
		vTaskDelay(25);
		digitalWrite(6, LOW);
		vTaskDelay(175);
		
	}
}

int main()
{
	
	Serial.begin(9600);
	Serial.print("s");
	
	pinMode(_trigPin, OUTPUT);
	pinMode(_EchoPin, INPUT);
	
	pinMode(10, OUTPUT);
	pinMode(11, OUTPUT);
	pinMode(12, OUTPUT);
	
	pinMode(6, OUTPUT);
	
	//pinMode(13, OUTPUT);

	//qh = xQueueCreate(1, sizeof(int));
	
	//xTaskCreate(task_tx, "t1", STACK_DEPTH, NULL, 5, &t1);
	//xTaskCreate(task_rx, "t2", STACK_DEPTH, NULL, 5, &t2);
	
	xTaskCreate(testTask, "test", STACK_DEPTH, NULL, 6, &t1);
	xTaskCreate(Servotask, "servo", STACK_DEPTH, NULL, 6, &t3);
	
	//xTaskCreate(task1, "t1", STACK_DEPTH, NULL, 6, &t1);
	xTaskCreate(task2, "t2", STACK_DEPTH, NULL, 6, &t2);
	
	//xTaskCreate(ssTask, "SonarServo", STACK_DEPTH, NULL, 5, &t3);
	
	vTaskStartScheduler();
}


void vApplicationIdleHook()
{
	// 	Do 	nothing.
}