// 
// LoadPath_client.cpp
// 2019 Middlebury College Summer Research with professor Scharstein
// Guanghan Pan
//

#include <unistd.h>
#include <stdio.h> 
#include <sys/socket.h> 
#include <arpa/inet.h> 
#include <unistd.h>  
#include <string.h>
#include <string>
#include <iostream>
#define PORT 50001
using namespace std;
   
int client() 
{ 
    int sock = 0; 
    struct sockaddr_in serv_addr; 
    char buffer[1024] = {0}; 
    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0) 
    { 
        printf("\n Socket creation error \n"); 
        return -1; 
    } 
   
    serv_addr.sin_family = AF_INET; 
    serv_addr.sin_port = htons(PORT); 
       
    // Convert IPv4 and IPv6 addresses from text to binary form 
    if(inet_pton(AF_INET, "127.0.0.1", &serv_addr.sin_addr)<=0)  
    { 
        printf("\nInvalid address/ Address not supported \n"); 
        return -1; 
    } 
   
    if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) 
    { 
        printf("\nConnection Failed \n"); 
        return -1; 
    } 
    return sock; 
} 

int sendCommand(char *script){
  int client_sock = client(), result;
  char buffer[1024] = {0};
  if(client_sock<1)
    return -1;
  send(client_sock, script,strlen(script),0);
  if (result<0){
    printf("\nSending Failed\n");
    return -1;
  }
  read(client_sock, buffer, 1024);
  cout << buffer << "\n";
  close(client_sock);
  usleep(1000000);
  return 0;
  
}

int gotoView(int num){
  string script = std::to_string(num);
  int n = script.length();
  char command[n+1];
  strcpy(command, script.c_str());
  if(sendCommand(command)<0)
    return -1;
  return 0;
}

int loadPath(string pathName){
  string script = "load " + pathName + ".obj";
  int n = script.length();
  char command[n+1];
  strcpy(command, script.c_str());
  if(sendCommand(command)<0)
    return -1;    
  return 0;
}

int executePath(){
  string script = "e";
  int n = script.length();
  char command[n+1];
  strcpy(command, script.c_str());
  if(sendCommand(command)<0)
    return -1;    
  return 0;
}

int setVelocity(float v){
  string script = "v " +  std::to_string(v);
  int n = script.length();
  char command[n+1];
  strcpy(command, script.c_str());
  if(sendCommand(command)<0)
    return -1;    
  return 0;
}


int main(int argc, char const *argv[]){
  loadPath("test");
  gotoView(1);
  setVelocity(0.3);
  gotoView(2);
  setVelocity(0.6);
  executePath();
  return 0;
}
