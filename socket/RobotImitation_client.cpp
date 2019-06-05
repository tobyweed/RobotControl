//
// RobotImitation_client.cpp
// 2019 Middlebury College Summer Research
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

int main(int argc, char const *argv[]){
  char command[1024];
  char quit[] = "q";
  while (true){
    int client_sock = client(),valread = 0;
    if(client_sock<1){
      break;
    }
    char buffer[1024] = {0};
    cout << "Enter your command:";
    cin >> command;
    send(client_sock, command,strlen(command),0);
    valread = read(client_sock, buffer, 1024);
    cout << buffer << "\n";
    close(client_sock);
    if(strcmp(command,quit)==0)
      break;
    usleep(1000000);
  }
  return 0;
}
