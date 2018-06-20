import serial
import random
from time import sleep, time

class NB_TRUE:
    def __init__(self, debug):
        self.debug = debug
        self.previous_time = time()
        self.port = ""
        self.ver = 1
        self.type = 0
        self.ver_type_tokenlen = 0
        self.code = [None] * 2
        self.messageid = [None] * 4
        self.token = [None] * 8
        self.option_1_name_path = [None] * 8
        self.option_2_length = [None] * 2
        self.option_2_ver = [None] * 4
        self.option_3_dev_token_len = [None] * 2
        self.option_3_dev_token_ext_len = [None] * 2
        self.option_3_dev_token = [None] * 20
        self.option_4_len_telemetry_word = [None] * 2
        self.option_4_telemetry_word = [None] * 18
        self.option_4_endmask = [None] * 2
        self.buffer = [None] * 1024


    def setupDevice(self, serverPort):
        self.port = serverPort
        print("############ NB-IOT TRUE #############")
        self.reset()
        if self.debug :
            self.IMEI = self.getIMEI()
            print("IMEI : " + self.IMEI)
            self.firmwareVersion = self.getFirmwareVersion()
            print("Firmware Version : " + self.firmwareVersion)
            self.IMSI = self.getIMSI()
            print("IMSI SIM : " + self.IMSI)
        self.attachNB(serverPort)
        print("end")

    
    def reset(self):
        self.rebootModule()
        print("Set Phone Function")
        self.setPhoneFunction()
        print("Set Phone Function Complete")

    def rebootModule(self):
        print("Test AT")
        ser.write(b'AT\r\n')
        while(self.waitReady() != True):
            print('.',end='')
            sleep(0.2)
        print("OK")
        
        #reboot module
        print("Reboot Module")
        ser.write(b"AT+NRB\r\n")
        while(self.waitReady() != True):
            ser.write(b'AT\r\n')
            print(".", end='')
            sleep(.5)
        ser.flush()
        print("Reboot Module Complete")
        sleep(5)

    def waitReady(self):
        msg = ser.readline().decode('utf-8', 'ignore').strip()
        if msg == 'OK':
            return True
        else :
            return False

    def setPhoneFunction(self):
        ser.write(b'AT+CFUN=1\r\n')
        while self.waitReady() != True:
            print(".", end='')
            sleep(.2)

    def getIMEI(self):
        ser.write(b"AT+CGSN=1\r\n")
        msg = ""
        msg = ser.read(64).decode('utf-8').strip()
        return msg[msg.find("+CGSN")+6:msg.find("+CGSN")+21]

    def getFirmwareVersion(self):
        ser.write(b'AT+CGMR\r\n')
        msg = ""
        out = ""
        while msg != 'OK':
            msg = ser.readline().decode('utf-8').strip()
            out += msg
        return out[:-2]

    def getIMSI(self):
        ser.write(b'AT+CIMI\r\n')
        msg = ""
        msg = ser.read(30).decode('utf-8').strip().replace("\n", '')
        return msg

    def attachNB(self, serverPort):
        ret = False
        if not self.getNBConnect():
            print("Connecting NB IOT Network")
            i = 1
            while i < 60:
                self.setPhoneFunction()
                self.setAutoConnectOn()
                self.cgatt(1)
                sleep(3)
                if self.getNBConnect():
                    ret = True
                    break
                print('.', end='')
                i += 1
        else :
            return True
        if ret :
            print("> Connected")
            self.createUDPSocket(serverPort)
        else :
            print("> Disconnect")
        print("##################################")
        return ret

    
    def getNBConnect(self):
        ser.write(b'AT+CGATT?\r\n')
        msg = ""
        while msg[-2:] != 'OK':
            msg += ser.readline().decode('utf-8').strip()
        if msg[:-2] == '+CGATT:1':
            return True
        else :
            return False

    def setAutoConnectOn(self):
        ser.write(b'AT+NCONFIG=AUTOCONNECT,TRUE\r\n')
        msg = ""
        while msg[-2:] != 'OK':
            msg = ser.readline().decode('utf-8').strip()

    def cgatt(self, mode):
        txt = "AT+CGATT=" + str(mode) + "\r\n"
        ser.write(txt.encode())
        msg = ""
        while msg != 'OK':
            msg = ser.readline().decode('utf-8').strip() 

    def createUDPSocket(self, port):
        txt = "AT+NSOCR=DGRAM,17," + str(port) + ",1\r\n"
        ser.write(txt.encode())
        msg = ""
        while msg[-2:] != 'OK':
            msg = ser.readline().decode('utf-8').strip()
    
    def pingIP(self, IP):
        txt = "AT+NPING=" + IP + "\r\n"
        ser.write(txt.encode())
        msg = ""
        while True:
            msg += ser.readline().decode('utf-8').strip()
            if msg.find("+NPING") == 2:
                break
        index1 = msg.find(',')
        index2 = msg.find(',', index1+1)
        ttl = msg[index1+1:index2]
        rtt = msg[index2+1:len(msg)]
        print("Ping To IP: " + IP + " ttl = " +ttl + " rtt = " + rtt)

    def sendUDPmsg(self, address, port, data):
        data = data.encode('utf-8').hex()
        length = str(len(data)/2)
        txt = "AT+NSOST=0,"+address+"," + str(port) + "," +length[:-2]+ "," + data + "\r\n"
        ser.write(txt.encode())
        msg = ""
        while msg != 'OK':
            msg = ser.readline().decode('utf-8').strip()

    def response(self):
        pre_time = time()
        cur_time = time()
        ser.write(b"AT+NSORF=0,100\r\n")
        msg = ""
        getData = False
        data = ""
        while True:
            msg = ser.readline().decode('utf-8').strip()
            if msg.find(str(self.port)) != -1:  
                data = msg 
                getData = True
                break
            # time out
            cur_time = time()
            if cur_time - pre_time >= 0.25:
                pre_time = cur_time
                break

        if getData:
            index1 = msg.find(',')
            index2 = msg.find(',', index1+1)
            index3 = msg.find(',', index2+1)
            index4 = msg.find(',', index3+1)
            index5 = msg.find(',', index4+1)

            serv_ip = msg[index1+1:index2]
            serv_port = msg[index2+1:index3]
            length = msg[index3+1:index4]
            data = bytearray.fromhex(msg[index4+1:index5]).decode()
            

            if self.debug :
                print("Respone data From IP:" + serv_ip + " Port:" + serv_port + " Length:" + length + " Data:" + data)
            return data
    def postRequest(self,token,payload):
        token_len = len(token)
        payload_len = len(payload)
        header_token_len = 0x04
        self.ver_type_tokenlen = self.ver << 6 | (self.type & 0x03) << 4 | (header_token_len & 0x0F)
        self.code[0] = 0x30
        self.code[1] = 2 | 0x30
        for i in range(0,4):
            self.messageid[i] = random.randint(0, 9) | 0x30
        
        for i in range(0,8):
            self.token[i] = random.randint(0, 9) | 0x30
        self.option_1_name_path[0] = 0x42;
        self.option_1_name_path[1] = 0x33;
        self.option_1_name_path[2] = 0x36;
        self.option_1_name_path[3] = 0x31;
        self.option_1_name_path[4] = 0x37;
        self.option_1_name_path[5] = 0x30;
        self.option_1_name_path[6] = 0x36;
        self.option_1_name_path[7] = 0x39;
        self.option_2_length[0] = 0x30;
        self.option_2_length[1] = 0x32;
        self.option_2_ver[0] = 0x37;
        self.option_2_ver[1] = 0x36;
        self.option_2_ver[2] = 0x33;
        self.option_2_ver[3] = 0x31;
        self.option_3_dev_token_len[0] = 0x30;
        self.option_3_dev_token_len[1] = 0x44;
        self.option_3_dev_token_ext_len[0] = 0x30;
        self.option_3_dev_token_ext_len[1] = 0x37;

        for i in range(0 , token_len):
            self.option_3_dev_token[i] = token[i]

        self.option_4_len_telemetry_word[0] = 0x30;
        self.option_4_len_telemetry_word[1] = 0x39;
        self.option_4_telemetry_word[0] = 0x37;
        self.option_4_telemetry_word[1] = 0x34;
        self.option_4_telemetry_word[2] = 0x36;
        self.option_4_telemetry_word[3] = 0x35;
        self.option_4_telemetry_word[4] = 0x36;
        self.option_4_telemetry_word[5] = 0x43;
        self.option_4_telemetry_word[6] = 0x36;
        self.option_4_telemetry_word[7] = 0x35;
        self.option_4_telemetry_word[8] = 0x36;
        self.option_4_telemetry_word[9] = 0x44;
        self.option_4_telemetry_word[10] = 0x36;
        self.option_4_telemetry_word[11] = 0x35;
        self.option_4_telemetry_word[12] = 0x37;
        self.option_4_telemetry_word[13] = 0x34;
        self.option_4_telemetry_word[14] = 0x37;
        self.option_4_telemetry_word[15] = 0x32;
        self.option_4_telemetry_word[16] = 0x37;
        self.option_4_telemetry_word[17] = 0x39;
        self.option_4_endmask[0] = 0x46;
        self.option_4_endmask[1] = 0x46;

        for i in range(0 , payload_len):
            self.buffer[i] = payload[i]

    def sendUDPPacket2(self,remoteIP,remotePort,json_len):
        lens = 96
        lens = (lens + json_len*2)/2
        buff = "0,"+remoteIP+","+str(remotePort)+","+str(lens)
        ser.write(b'AT+NSOST=\r\n')
        ser.write(buff)
        ser.write( self.ver_type_tokenlen);
        ser.write( self.code);
        ser.write( self.messageid);
        ser.write( self.token);
        ser.write( self.option_1_name_path );
        ser.write( self.option_2_length);
        ser.write( self.option_2_ver);
        ser.write( self.option_3_dev_token_len);
        ser.write( self.option_3_dev_token_ext_len);

        for i in range(0,20):
            ser.write(self.option_3_dev_token[i])

        ser.write(self.option_4_len_telemetry_word)
        ser.write(self.option_4_telemetry_word)
        ser.write(self.option_4_endmask)

        for i in range(0,json_len):
            ser.write(self.buffer[i])
        
        ser.write("\r\n")



IP = '104.196.24.70'
port = 5683
iotToken = "mY6nQMft4YJLhG2UYHsL"
jsonData = "{\"temperature\": 48, \"humidity\": 50 }\0"

ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

# debug True or False
trueiot = NB_TRUE(True)
trueiot.setupDevice(port)
print("Test Ping")
trueiot.pingIP('8.8.8.8')
while True:
    sleep(1)
    
    jsonData_len = len(jsonData)
    print(jsonData)
    trueiot.postRequest(iotToken,jsonData)
    trueiot.sendUDPPacket2(IP,port,jsonData_len)

    # current_time = time()
    # if current_time - previous_time >= interval:
    #     cnt += 1
    #     trueiot.sendUDPmsg(IP,port,'Test'+str(cnt))
    #     previous_time = current_time
    #     print("send")
        
    trueiot.response()
