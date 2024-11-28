import math
import logging
import serial
import struct

logging.basicConfig(filename='CyberGear.log', filemode='w', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class ControlModeMsg():

    def __init__(self, can_id=1, torque=0.0, position=0.0, velocity=0.0, Kp=0.0, Kd=0.0):
        self.can_id   = can_id
        self.torque   = min(max(torque, -12.0), 12.0)
        self.position = min(max(position, -4*math.pi), 4*math.pi)
        self.velocity = min(max(velocity, -30.0), 30.0)
        self.Kp       = min(max(Kp, 0.0), 500.0)
        self.Kd       = min(max(Kd, 0.0), 5.0)

    def encode(self):
        type     = 0x01
        torque   = int((self. torque + 12.0)/24 * 0xffff)
        can_id   = self.can_id << 3 | 0x04
        length   = 0x08
        position = int((self.position + 4*math.pi)/(8*math.pi) * 0xffff)
        velocity = int((self.velocity + 30.0)/60 * 0xffff)
        Kp       = int(self.Kp / 500 * 0xffff)
        Kd       = int(self.Kd / 5 * 0xffff)

        data = [type << 3 | torque >> 13, torque >> 5 & 0xff, torque << 3 & 0xff | can_id >> 8, can_id & 0xff,
                length, position >> 8, position & 0xff, velocity >> 8, velocity & 0xff, Kp >> 8, Kp & 0xff, Kd >> 8, Kd & 0xff]
        msg = "41 54 " + ' '.join(f'{byte:02x}' for byte in data) + " 0d 0a"
        logging.info("controlModeMsg: " + msg)
        return msg


class FeedbackMsg():

    def __init__(self, msg=None):
        self.msg = msg

    def decode(self):
        if len(self.msg) != 17:
            logging.warning("Invalid message length.")
            return False

        if self.msg[0] != 0x41 or self.msg[1] != 0x54 or self.msg[15] != 0x0d or self.msg[16] != 0x0a:
            logging.warning("Invalid header and tail.")
            return False

        if self.msg[2] >> 3 != 0x02:
            logging.warning("Invalid type.")
            return False

        state = self.msg[2] >> 1 & 0x03
        if state == 0:
            self.state = "Reset"
        elif state == 1:
            self.state = "Cali"
        elif state == 2:
            self.state = "Run"
        else:
            logging.warning("Invalid state.")
            return False

        error = (self.msg[2] & 0x01) << 5 | self.msg[3] >> 3
        self.error = error != 0

        can_id = (self.msg[3] & 0x07) << 5 | self.msg[4] >> 3
        self.can_id = can_id

        host_id = (self.msg[4] & 0x07) << 5 | self.msg[5] >> 3
        self.host_id = host_id

        if self.msg[5] & 0x07 != 0x04:
            logging.warning("Invalid can id.")
            return False

        if self.msg[6] != 0x08:
            logging.warning("Invalid data length.")
            return False

        position = self.msg[7] << 8 | self.msg[8]
        self.position = (position / 0xffff * 8*math.pi) - 4*math.pi

        velocity = self.msg[9] << 8 | self.msg[10]
        self.velocity = (velocity / 0xffff * 60) - 30

        torque = self.msg[11] << 8 | self.msg[12]
        self.torque = (torque / 0xffff * 24) - 12

        temp = self.msg[13] << 8 | self.msg[14]
        self.temp = temp / 10.0

        return True


class MotorController():

    def __init__(self, port='/dev/ttyUSB0', baudrate=921600, timeout=1):
        self.serial = serial.Serial(port, baudrate, timeout=timeout)

        while True:
            self.serial.write(bytes.fromhex('41 54 2b 41 54 0d 0a'))
            ok_msg = self.serial.read(4)
            if ok_msg == b'OK\r\n':
                break

    def controlMode(self, send_msg):
        try:
            self.serial.write(bytes.fromhex(send_msg.encode()))
        except:
            logging.error("Failed to send controlModeMsg.")
            return None
        recv_msg = FeedbackMsg(self.serial.read(17))
        if recv_msg.decode():
            return recv_msg