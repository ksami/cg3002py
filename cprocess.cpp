#include <iostream>

using namespace std;

int main(void){
	int timer = 0;
	int i;

	cout << "cprocess started" << endl;

	for(i=0; i<100; i++){
		while(timer<=100000000){
			timer++;
		}
		timer = 0;
		cout << "hello " << i << endl;
	}
}