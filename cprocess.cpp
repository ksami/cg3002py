#include <iostream>

using namespace std;

int main(void){
	char kill = '1';
	int ikill = 1;

	cout << "cprocess started" << endl;

	while(ikill > 0){
		cin >> kill;
		ikill = kill - '0';
		cout << "hello " << ikill << endl;
	}
}