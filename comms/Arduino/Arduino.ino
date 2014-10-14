#include "XBee.h"
#include "queue.h"
#include <SoftwareSerial.h>

#define DEVICE_READY 0
#define NAVI_READY 1
#define NAVI_END 2
#define OBSTACLE_DETECTED 3

// Other constants
#define RPI_ADDR 0
#define MAX_RPI_MSG_SIZE 5
#define PKG_INDEX 8

XBee xbee;
Queue RxQ;
SoftwareSerial sserial(12,13);
int flag;
void setup(void)
{
    sserial.begin(9600);
    Serial.begin(9600);
    Serial.println("xbee starts");
    flag = 0;
}

//void loop(void)
//{
//    delay(5);
//    int queueLen = 0;
//    int delPos = 0;
//   
//    while (sserial.available() > 0){
//        unsigned char in = (unsigned char)sserial.read();
//        Serial.println(in,HEX);
//        if (!RxQ.Enqueue(in)){
//            break;
//        }
//    }
//
//    queueLen = RxQ.Size();
//    for (int i=0;i<queueLen;i++){
//        if (RxQ.Peek(i) == 0x7E){
//            unsigned char checkBuff[Q_SIZE];
//            unsigned char msgBuff[Q_SIZE];
//            int checkLen = 0;
//            int msgLen = 0;
//
//            checkLen = RxQ.Copy(checkBuff, i);
//            msgLen = xbee.Receive(checkBuff, checkLen, msgBuff);
//            if (msgLen > 0){
//                unsigned char outMsg[MAX_RPI_MSG_SIZE];
//                unsigned char outFrame[Q_SIZE];
//                int frameLen = 0;
//                int packageID = (char)msgBuff[PKG_INDEX] - '0';
//
//                int ack_len = 0;
//                
//                switch(packageID){
//                  case DEVICE_READY:
//                    memcpy(outMsg,"ACK",3);
//                    ack_len = 3;
//                    break;
//                  case NAVI_READY:
//                    memcpy(outMsg,"ACK",3);
//                    ack_len = 3;
//                    break;
//                  case NAVI_END:
//                    memcpy(outMsg,"ACK",3);
//                    ack_len = 3;
//                    break;
//                  case OBSTACLE_DETECTED:
//                    memcpy(outMsg,"ACK",3);
//                    // activate servos
//                    // dir = msgBuff[9];
//                    // str = msgBuff[10];
//                    Serial.print("dir: ");
//                    Serial.print((char)msgBuff[9]);
//                    Serial.print(" str: ");
//                    Serial.println((char)msgBuff[10]);
//                    ack_len = 3;
//                    break;
//                  default:
//                    // raise error ?
//                    break;
//                }
//                frameLen = xbee.Send(outMsg, ack_len, outFrame, RPI_ADDR);
//                sserial.write(outFrame, frameLen);
//                i += msgLen;
//                delPos = i;    
//            }else{
//                if (i>0){
//                    delPos = i-1;
//                }
//            }
//        }
//    }
//
//    RxQ.Clear(delPos);
//}


void loop(void){
    if(!flag)
    {
      int frameLen = 0;
      unsigned char outFrame[Q_SIZE];
      unsigned char outMsg[2];
      int handstatus = 0;
      memcpy(outMsg,"4",1);
      if(handstatus == 1)
        memcpy(&outMsg[1],"1",1);
      else
        memcpy(&outMsg[1],"0",1);
      frameLen = xbee.Send(outMsg, 2, outFrame, RPI_ADDR);
      sserial.write(outFrame, frameLen);
      flag = 1;
      Serial.println("Done");
    }
}
