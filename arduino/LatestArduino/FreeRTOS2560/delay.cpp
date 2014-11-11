#include "delay.h"

void printInteger(int num) {
        printInt(num);
        Serial.print('\n');
}

void printInt(int num) {
	int last_digit = num % 10;
	if(num > 10)
	printInt(num/10);
	Serial.print(last_digit, DEC);
}

void delayInMilliSeconds(int milliseconds) {
	long start = millis();
	while (millis() - start < milliseconds);
}

void delayInMicroSeconds(int microseconds) {
	long start = micros();
	while (micros() - start < microseconds);
}