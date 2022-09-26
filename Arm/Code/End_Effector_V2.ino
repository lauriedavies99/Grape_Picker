#include <DynamixelShield.h>

#if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_MEGA2560)
  #include <SoftwareSerial.h>
  SoftwareSerial soft_serial(7, 8); // DYNAMIXELShield UART RX/TX
  #define DEBUG_SERIAL soft_serial
#elif defined(ARDUINO_SAM_DUE) || defined(ARDUINO_SAM_ZERO)
  #define DEBUG_SERIAL SerialUSB    
#else
  #define DEBUG_SERIAL Serial
#endif

const uint8_t DXL_CUTTER = 1;
const uint8_t DXL_GRIPPER = 2;
const float DXL_PROTOCOL_VERSION = 2.0;

int GripperClosed  = 0;
int GripperOpen = 30;
int CutterClosed = 120;
int CutterOpen = 0;
int BS;

DynamixelShield dxl;

using namespace ControlTableItem;

void setup() {
  pinMode(8, INPUT_PULLUP);  // Pin 8 reads 1 if not connected to GND
  pinMode(LED_BUILTIN, OUTPUT); // We can now use the built in LED
  DEBUG_SERIAL.begin(115200);

  // Set Port baudrate to 57600bps. This has to match with DYNAMIXEL baudrate.
  dxl.begin(57600);
  // Set Port Protocol Version. This has to match with DYNAMIXEL protocol version.
  dxl.setPortProtocolVersion(DXL_PROTOCOL_VERSION);
  // Get DYNAMIXEL information
  dxl.ping(DXL_CUTTER);
  dxl.ping(DXL_GRIPPER);

  // Turn off torque when configuring items in EEPROM area
  dxl.torqueOff(DXL_CUTTER);
  dxl.setOperatingMode(DXL_CUTTER, OP_POSITION);
  dxl.torqueOn(DXL_CUTTER);
  dxl.torqueOff(DXL_GRIPPER);
  dxl.setOperatingMode(DXL_GRIPPER, OP_POSITION);
  dxl.torqueOn(DXL_GRIPPER);

  //Angle Conversion
  GripperClosed = (GripperClosed + 80) * 11.377;
  GripperOpen = (GripperOpen + 80) * 11.377;
  CutterClosed = (CutterClosed) * 11.377;
  CutterOpen = (CutterOpen+20) * 11.377; 
  
}
void loop() {
  BS = digitalRead(8);
  digitalWrite(LED_BUILTIN, BS);
  if (BS == 0) {
    dxl.writeControlTableItem(PROFILE_VELOCITY, DXL_GRIPPER, 75);
    dxl.writeControlTableItem(PROFILE_VELOCITY, DXL_CUTTER, 500);
    dxl.setGoalPosition(DXL_GRIPPER,GripperClosed);
    delay(2000);
    dxl.setGoalPosition(DXL_CUTTER, CutterClosed);
    delay(2000);
    dxl.writeControlTableItem(PROFILE_VELOCITY, DXL_CUTTER, 75);
    dxl.setGoalPosition(DXL_CUTTER, CutterOpen);
    delay(2000);
    dxl.setGoalPosition(DXL_GRIPPER,GripperOpen);
  }
  
  // we echo the status of the pin 8 input on the built in LED
  
}
