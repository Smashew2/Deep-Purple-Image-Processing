/* 
Code for running motors with tolerance checking from R-Pi

Serial should recieve a name of exactly 5 characters: 
"A 12 34" (white space for clarity) 

A: Row letter (A-S)
12: Hole number in row (starting from 1 at center line)
34: Total holes in current row (lookup table in R-Pi)
*/

#include <AccelStepper.h>

#define STEPS_PER_REV_STEP 200  // 1.8° stepper motor (no microstepping on driver)
#define STEPS_PER_REV_STAGE 200*180  // 180 is the gear ratio (assuming no microstepping on driver)
#define STEP_PIN_STAGE 9 //Ensure this is digital pin with ~ 
#define DIR_PIN_STAGE 8
#define STEP_PIN_STEP 6 //Ensure this is digital pin with ~ 
#define DIR_PIN_STEP 2

AccelStepper stepperStage(AccelStepper::DRIVER, STEP_PIN_STAGE, DIR_PIN_STAGE);
AccelStepper stepperStep(AccelStepper::DRIVER, STEP_PIN_STEP, DIR_PIN_STEP);

const long stepPerRevStage = 200L*180L;
String curHole = "A0170";
char curRow = curHole[0]; 
int num = (curHole[3] - '0') * 10 + (curHole[4] - '0');  // Convert characters to an integer with charater vals
int curRotate = stepPerRevStage / num;  // Set rotation val for new row to curRotate
String oldHole = "";

void setup() {
  Serial.begin(9600);  // Initialize serial communication
  while(!Serial);

  delay(1000);
  stepperStage.setMaxSpeed(2000);       // Max speed (steps per second)
  stepperStage.setAcceleration(1000);    // Acceleration (steps per second^2) at least 1000
  delay(1000);
  stepperStep.setMaxSpeed(1000);       // Max speed (steps per second)
  stepperStep.setAcceleration(750);    // Acceleration (steps per second^2)
  delay(1000);

}

void loop() {

  oldHole = curHole;
  
  char buffer[6]; // +1 for null terminator if treating as a string

  for (int i = 0; i < 5; i++) {
    while (!Serial.available()); // Wait for data
    buffer[i] = Serial.read();
  }
  buffer[5] = '\0'; // Null-terminate if you want to use it as a string


  if ((buffer[0] == 'R') && (buffer[1] == 'R')) {
    // Consume the command from the buffer
    while (Serial.available() > 0) {
      Serial.read(); // discard byte
    }

    // Move motors to original position
    stepperStage.moveTo(0);
    while (stepperStage.distanceToGo() != 0) stepperStage.run();
    
    stepperStep.moveTo(0);
    while (stepperStep.distanceToGo() != 0) stepperStep.run();

    curHole = "A0170";
    curRow = 'A';

    Serial.println("Reset complete");
    delay(1000);
    return; // skip rest of loop
  }



  //Wait for tolerance flag
  //If bad fix
if (buffer[0] == 'T') {
    char fixBuf[6]; // Buffer for 5 chars + null terminator
    for (int i = 0; i < 5; i++) {
      while (!Serial.available());
      fixBuf[i] = buffer[i];
    }
    while (Serial.available() > 0) {
      Serial.read(); // discard byte
    }
    fixBuf[5] = '\0';

    // Convert last 3 characters to an integer
    int stepFix = atoi(&fixBuf[2]); // fixBuf[2], [3], [4] → step amount
  if(fixBuf[1] == 'N'){
    stepFix = -stepFix;
  }
    
    // Move by that number of steps
    stepperStage.move(stepFix);
    while (stepperStage.distanceToGo() != 0) stepperStage.run();

    Serial.println('1');
    delay(1000);
    return; // Skip the rest of the loop
}
   curHole = buffer;
  // Check if going to new row
  if (curHole[0] != curRow){

    //Move back to center line and move down one
    int holesFromZero = (oldHole[1] - '0') * 10 + (oldHole[2] - '0') - 1;  // Convert characters to an integer with charater vals
    
    //stepperStage.move(stepPerRevStage-curRotate); //in steps
    stepperStage.moveTo(0); //in steps
    while(stepperStage.distanceToGo() != 0) {
      stepperStage.run();
    }
    delay(1000);
    //Adjust vertical
    if(curRow == 'A') {
      stepperStep.move(1500); //in steps
      while(stepperStep.distanceToGo() != 0) {
        stepperStep.run();
      }
      delay(1000);
    }
    else {
      int rowDiff = curHole[0] - curRow;
      stepperStep.move(2000*rowDiff); //in steps
      while(stepperStep.distanceToGo() != 0) {
        stepperStep.run();
      }
      delay(1000);
    }

    //Update current rotation based on new row
    int num = (curHole[3] - '0') * 10 + (curHole[4] - '0') ;  // Convert characters to an integer with charater vals
    curRotate = stepPerRevStage / num;  // Set rotation val for new row to curRotate
    curRow = curHole[0];
    
    
  }
  else { 
    int num = (curHole[1] - '0') * 10 + (curHole[2] - '0');
    int oldNum = (oldHole[1] - '0') * 10 + (oldHole[2] - '0');
    int moveHoles = num - oldNum;
  

    if (num != oldNum) {
      //stepperStage.move(-curRotate*moveHoles);
      stepperStage.move(-curRotate*moveHoles);

      // Wait for the motor to finish moving
      while(stepperStage.distanceToGo() != 0) {
        stepperStage.run();
      }

  
      
    }
    delay(1000);

  }


  //Send update to say picture is ready
  Serial.println('1');
  delay(1000);

}
