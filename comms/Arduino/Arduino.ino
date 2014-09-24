#include "XBee.h"
#include "queue.h"

XBee xbee;
Queue RxQ;
const int leftPin = 8;
const int rightPin = 7;
const int ackPin = 9;

void setup(void)
{
    Serial1.begin(9600);
    Serial.begin(9600);
    pinMode(leftPin, OUTPUT);
    pinMode(rightPin, OUTPUT);
    pinMode(ackPin, OUTPUT);
}

void loop(void)
{
    delay(5);
    int queueLen = 0;
    int delPos = 0;
    int counter = 0;
    while (Serial1.available() > 0){
        unsigned char in = (unsigned char)Serial1.read();
        Serial.println(String(in,HEX));
        if (!RxQ.Enqueue(in)){
          break;
        }
    }

    queueLen = RxQ.Size();
    for (int i=0;i<queueLen;i++){
        if (RxQ.Peek(i) == 0x7E){
            unsigned char checkBuff[Q_SIZE];
            unsigned char msgBuff[Q_SIZE];
            int checkLen = 0;
            int msgLen = 0;
            //Serial.print("Length: ");
            checkLen = RxQ.Copy(checkBuff, i);
//            Serial.println("checkBuff: ");
//            for(int j=0;j<checkLen;j++)
//              Serial.println(String(checkBuff[j],HEX));    
//            Serial.print("Len: ");
//            Serial.println(checkLen);
//            Serial.print("message length: ");
            msgLen = xbee.Receive(checkBuff, checkLen, msgBuff);
//            Serial.println(msgLen);
            if (msgLen > 0){
                unsigned char outMsg[Q_SIZE];
                unsigned char data[Q_SIZE];
                unsigned char outFrame[Q_SIZE];
                int frameLen = 0;
                int addr = ((int)msgBuff[4] << 8) + (int)msgBuff[5];
                
                // 10 is length of "you sent: "
                memcpy(outMsg, "you sent: ", 10);
                // len - (9 bytes of frame not in message content)
                
                int data_id = xbee.GetDataId(msgBuff);
                int data_len = xbee.GetData(msgBuff,msgLen,data);
                switch(data_id){
                  case 0:
                    // Ack is sent by XBee 
                    // Pi is device ready
                    digitalWrite(ackPin, HIGH);
                    break;
                  case 1:
                    // Pi detects obstacle
                    if(data[0] == 'L') { // left obstacle
                      Serial.print("left str: ");
                      Serial.println(char(data[1]));
                      digitalWrite(leftPin, HIGH);
                    } else if(data[0] == 'R') { //right obstacle
                      Serial.print("Right str: ");
                      Serial.println(char(data[1]));
                      digitalWrite(rightPin, HIGH);
                    } else
                      Serial.println("alamak which direction la ?");
                    break;
                  default:
                    // raise error ?
                    break;
                }
                memcpy(&outMsg[10], &msgBuff[8], msgLen-9);
                // 10 + (-9) = 1 more byte in new content than in previous message
//                memcpy(outMsg,"start",5);
//                frameLen = xbee.Send(outMsg, 5, outFrame, addr);
//                frameLen = xbee.Send(outMsg, msgLen+1, outFrame, addr);
//                Serial.println("out frame:");
//                for(int count = 0;count < frameLen; count++)
//                  Serial.println(String(outFrame[count],HEX));
                frameLen = xbee.Send(outMsg, msgLen+1, outFrame, addr);
                Serial1.write(outFrame, frameLen);
                i += msgLen;
                delPos = i;    
            }else{
                if (i>0){
                    delPos = i-1;
                }
            }
        }
    }

    RxQ.Clear(delPos);
}
