#include "Que.h"
#include <string.h>

Que::Que() {
  m_Head = 0;
  m_Tail = 0;
  m_Size = 0;
  memset(m_Data, 0, Q_SIZE);
}

Que::~Que(){
  memset(m_Data, 0, Q_SIZE);
}

bool Que::Enqueue(unsigned char d) 
{
    if (!Full()){
        m_Data[m_Tail++] = d;
        m_Tail %= Q_SIZE;
        m_Size++;
        return true;
    }else{
        return false;
    }
}

unsigned char Que::Dequeue(){
    unsigned char t=0;

    if (!Empty()) {
        t = m_Data[m_Head];
        m_Data[m_Head++] = 0;
        m_Head %= Q_SIZE;
        m_Size--;
    }
    return t;
}

int Que::QueueString(unsigned char * s, int len){
    int sendlen = 0;

    for (int i=0; i<len; i++){
        if (Enqueue(*s)){
            s++;
            sendlen++;
        }else{ 
            break;
        }
    }

    return sendlen;
}

unsigned char Que::Peek(unsigned int pos){
    unsigned char c = 0;

    pos += m_Head;
    pos %= Q_SIZE;

    if ((pos >= m_Head) || (pos < m_Tail)){
        c = m_Data[pos];
    }

    return c;
}

int Que::Copy(unsigned char *outbuf, int start){
    int i = 0;
    int pos = 0; 

    if (start >= m_Size)
        return false;

    pos = (m_Head + start) % Q_SIZE;
    while(i < m_Size){
        outbuf[i++] = m_Data[pos++];
        pos %= Q_SIZE;
    }
	return i;
}


int Que::Clear(unsigned int pos){
    int deleted = 0;
    pos += m_Head;
    pos %= Q_SIZE;

    if (pos >= m_Tail){ 
        // delete entire thing
        for (unsigned int i=0; i<Q_SIZE; i++) {
            m_Data[i] = 0;
        }

        m_Head = 0;
        m_Tail = 0;
        m_Size = 0;
        return Q_SIZE;
    }

    while(m_Head != pos){
        m_Data[m_Head++] = 0;
        m_Head %= Q_SIZE;
        m_Size--;
        deleted++;
    }

    return deleted;
}
