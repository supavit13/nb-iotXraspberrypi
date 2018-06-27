import serial
import urllib.request, json
import sys
import logging
from time import sleep, time

class NB_TRUE:
    def __init__(self, debug):
        self.debug = debug
        self.previous_time = time()
        self.port = ""
        


    def setupDevice(self, serverPort):
        self.port = serverPort
        logging.info("############ NB-IOT TRUE #############")
        self.reset()
        if self.debug :
            self.IMEI = self.getIMEI()
            logging.info("IMEI : " + self.IMEI)
            self.firmwareVersion = self.getFirmwareVersion()
            logging.info("Firmware Version : " + self.firmwareVersion)
            self.IMSI = self.getIMSI()
            logging.info("IMSI SIM : " + self.IMSI)
        self.attachNB(serverPort)
        logging.info("end")

    
    def reset(self):
        self.rebootModule()
        logging.info("Set Phone Function")
        self.setPhoneFunction()
        logging.info("Set Phone Function Complete")

    def rebootModule(self):
        logging.info("Test AT")
        ser.write(b'AT\r\n')
        while(self.waitReady() != True):
            logging.info('.',end='')
            sleep(0.2)
        logging.info("OK")
        
        #reboot module
        logging.info("Reboot Module")
        ser.write(b"AT+NRB\r\n")
        while(self.waitReady() != True):
            ser.write(b'AT\r\n')
            logging.info(".", end='')
            sleep(.5)
        ser.flush()
        logging.info("Reboot Module Complete")
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
            logging.info(".", end='')
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
            logging.info("> Connected")
            self.createUDPSocket(serverPort)
        else :
            logging.info("> Disconnect")
        logging.info("##################################")
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
        logging.info("Ping To IP: " + IP + " ttl = " +ttl + " rtt = " + rtt)

    def sendUDPmsg(self, address, port, data):
        data = data.encode('utf-8').hex()
        length = str(len(data)/2)
        txt = "AT+NSOST=0,"+address+"," + str(port) + "," +length[:-2]+ "," + data + "\r\n"
        ser.write(txt.encode())
##        print("write to serial")
        msg = ""
        # while msg != 'OK':
##            print("wait OK")
            # msg = ser.readline().decode('utf-8').strip()

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
                logging.info("Respone data From IP:" + serv_ip + " Port:" + serv_port + " Length:" + length + " Data:" + data)
            return data



IP = sys.argv[1]
port = int(sys.argv[2])
logging.info(IP)
logging.info(port)
jsonData = "{\"temperature\": 48, \"humidity\": 50 }"
logging.basicConfig(filename='logging.log',level=logging.DEBUG)

ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

# debug True or False
trueiot = NB_TRUE(True)
trueiot.setupDevice(port)
logging.info("Test Ping")
trueiot.pingIP('8.8.8.8')
previous_time = time()
interval = 1
cnt = 0
while True:
    current_time = time()
    # if current_time - previous_time >= interval:
    cnt += 1
    data = {}
    with urllib.request.urlopen("http://127.0.0.1:8080/data/aircraft.json") as url:
        data = json.loads(url.read().decode())
        logging.info("read json aircraft..")
        for aircraft in data['aircraft']:
            aircraft['unixtime'] = data['now']
            aircraft['node_number'] = int(sys.argv[3])
            if all(x in aircraft for x in ("lat","lon","flight","altitude")):
                trueiot.sendUDPmsg(IP,port,json.JSONEncoder().encode(aircraft))
                logging.info("send udp")
    previous_time = current_time
    logging.info("send"+str(cnt))
    if cnt == 11:
        cnt = 0
        
    # trueiot.response()
