//
// RobotControl.cpp
// RobotControl
//
// Guanghan Pan
//

#include <iostream>
#include "LoadPath_client.h"

extern "C" int Client() {
  return client();
}

extern "C" int SendCommand(char *script) {
  return sendCommand(script);
}

extern "C" int GotoView(int num){
  return gotoView(num);
}

extern "C" int LoadPath(char *pathName){
  return loadPath(std::string(pathName));
}

extern "C" int ExecutePath(){
  return executePath();
}

extern "C" int SetVelocity(float v){
  return setVelocity(v);
}

