#include "FreeRTOS.h"
#include "task.h"

int trigpin_1 = 2;//appoint trigger pin
int echopin_1 = 3;//appoint echo pin

int trigpin_2 = 6;
int echopin_2 = 5;

float cmdivisor = 13;

void SonarTask(void* p)
{

	float cmdistance_1; //left
	float cmdistance_2; //right
	long microsec = ultrasonic.timing(); //MODIFIED DELAY FUNCTION
	long microsec_2 = ultrasonic_2.timing();
	
	    digitalWrite(trigpin_1, LOW);
		digitalWrite(trigpin_2, LOW);
	    vTaskDelay(2);
	    digitalWrite(trigpin_1, HIGH);
		digitalWrite(trigpin_2, HIGH);
	    vTaskDelay(10);
	    digitalWrite(trigpin_1, LOW);
		digitalWrite(trigpin_2, LOW);
	    long microsec_1 = pulseIn(echopin_1, HIGH);
		long microsec_2 = pulseIn(echopin_2, HIGH);
	    cmdistance_1 = microsec_1 / cmdivisor / 2.0;
		cmdistance_2 = microsec_2 / cmdivisor / 2.0;
		
	    int distance_left = (int) cmdistance_1;
		int distance_right = (int) cmdistance_2;
		
		if(cmdistance>40 && cmdistance<60) {

		}
		else if (cmdistance<40)	{

		}
		else { }

		if(cmdistance>40 && cmdistance<60) {

		}
		else if (cmdistance<40)	{

		}
		else { }
}

//send data on the queue