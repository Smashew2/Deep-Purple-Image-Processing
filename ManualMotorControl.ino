#include <AccelStepper.h>

#define STEP_PIN_STEP 6 //Ensure this is digital pin with ~ 
#define DIR_PIN_STEP 2
#define STEP_PIN_STAGE 9 //Ensure this is digital pin with ~ 
#define DIR_PIN_STAGE 8

AccelStepper stepperStage(AccelStepper::DRIVER, STEP_PIN_STAGE, DIR_PIN_STAGE);
AccelStepper stepperStep(AccelStepper::DRIVER, STEP_PIN_STEP, DIR_PIN_STEP);



void setup() {
  Serial.begin(9600);  // Initialize serial communication
  
  delay(1000);
  stepperStage.setMaxSpeed(3000);       // Max speed (steps per second)
  stepperStage.setAcceleration(1000);    // Acceleration (steps per second^2)
  delay(1000);
  stepperStep.setMaxSpeed(1000);       // Max speed (steps per second)
  stepperStep.setAcceleration(1000);    // Acceleration (steps per second^2)
  delay(1000);

  


}

void loop(){
  
  stepperStage.move(-300); //pos is counter clock wise
  while(stepperStage.distanceToGo() != 0) {
    stepperStage.run();
  }
  delay(1000);
  
  /*
  //Adjust vertical
  stepperStep.move(); //pos is down
  while(stepperStep.distanceToGo() != 0) {
    stepperStep.run();
  }
  */
  while (true) {
    delay(100000);
  }
  
}
