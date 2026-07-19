#ifndef PC_REC_H
#define PC_REC_H

#include <Arduino.h>
 

#define CONST_STARTBYTE1 0xAAu
#define CONST_STARTBYTE2 0x55u
const uint16_t BUFFER_SIZE = 90;
const uint16_t DATA_SIZE = 20; //Effective data should not exceed DATA_SIZE (有效数据不应该超过 DATA_SIZE)

//Frame function code enumeration (帧功能号枚举)
enum PACKET_FUNCTION {
  FUNC_SET_ANGLE = 0x01,
  FUNC_SET_XYZ = 0x03,
  FUNC_SET_PWMSERVO = 0x05,
  FUNC_SET_SUCTIONNOZZLE = 0x07,
  FUNC_READ_ANGLE = 0x11,
  FUNC_READ_XYZ = 0x13
};


//Parser state machine state enumeration (解析器状态机状态枚举)
enum PacketControllerState {
    STATE_STARTBYTE1, /**< Searching for start byte 1 (正在寻找帧头标记1) */
    STATE_STARTBYTE2, /**< Searching for start byte 2 (正在寻找帧头标记2) */
    STATE_FUNCTION, /**< Processing frame function code (正在处理帧功能号) */
    STATE_LENGTH, /**< Processing frame length (正在处理帧长度) */
    STATE_DATA, /**< Processing frame data (正在处理帧数据) */
    STATE_CHECKSUM, /** Processing data checksum (正在处理数据校验) */
};

#pragma pack(1)

//Command content parameters (命令内容参数)
typedef
struct PacketRawFrame {
    uint8_t start_byte1;
    uint8_t start_byte2;
    uint8_t function;   //Function code (功能号)
    uint8_t data_length;
    uint8_t data[DATA_SIZE];  //Data (数据)
    uint8_t checksum;
}packet_st;

//Set Angle (设置Angle)
typedef
struct ANGLE_CTL_DATA{
  uint16_t pul[3];
  uint16_t time;
}Angle_Ctl_Data;

//Set XYZ (设置xyz)
typedef
struct XYZ_CTL_DATA{
  int16_t pos[3];
  uint16_t time;
}XYZ_Ctl_Data;

//Set PWM Servo (设置PWM舵机)
typedef
struct PWM_CTL_DATA{
  uint16_t pul;
  uint16_t time;
}PWM_Ctl_Data;

// Set Suction Nozzle (设置吸嘴)
typedef
struct SN_CTL_DATA{
  uint8_t cmd;
}SN_Ctl_Data;

//Read Angle (读Angle)
typedef
struct READ_ANGLE_DATA{
  uint16_t pos[3];
}read_Angle_Data;

//Read XYZ (读xyz)
typedef
struct READ_XYZ_DATA{
  int16_t x;
  int16_t y;
  int16_t z;
}read_XYZ_Data;

#pragma pack(0)


/**
 * @brief Protocol parser (协议解析器)
 * @details Stores the parser's working state, state machine state, buffer storage, etc. （协议解析器, 存储了解析器的工作状态、状态机状态、缓冲存储区等）
 */
struct PacketController {
    //Variables related to protocol parsing (解析协议的相关变量)
    enum PacketControllerState state;        //Current state of the parser state machine (解析器状态机当前状态)
    struct PacketRawFrame frame;             //Frame currently being processed by the parser (解析器正在处理的帧)
    int data_index;   //Data index used during parsing (解析时需要用到的数据下标)

    //Buffer related variables (缓冲区相关变量)
    uint8_t len;
    uint8_t index_head;
    uint8_t index_tail;
    uint8_t data[BUFFER_SIZE];
};



class PC_REC{
  public:
    PC_REC(void);

    void begin(uint16_t bount);
    void rec_data(void);

    void deal_command(struct PacketRawFrame* ctl_com);

  private:
    // Flag indicating successful read (读取成功标志位)
    bool read_succeed;
    // Receiving and parsing controller (接收解析控制器)  
    struct PacketController pk_ctl;
    // Variable storing parsing result (解析结果储存变量)
    // packet_st pk_result;
};

#endif //PC_REC_H
