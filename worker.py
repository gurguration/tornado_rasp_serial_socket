import serial
import time
import multiprocessing


## Change this to match your local settings
PORT = '/dev/ttyUSB0'
BAUDRATE = 9600
PARITY=serial.PARITY_EVEN
STOPBITS=serial.STOPBITS_ONE
BYTESIZE=serial.SEVENBITS

    #voltageCommand = chr(0x2F) + chr(0x3F) + chr(0x21) + chr(0x01) + chr(0x52) + chr(0x31) + chr(0x02) + chr(0x56) + chr(0x4F)+chr(0x4C)+chr(0x54)+ chr(0x41)+chr(0x28)+ chr(0x29)+chr(0x03)+chr(0x5F)
    # currentCommand = chr(0x2F) + chr(0x3F) + chr(0x21) + chr(0x01) + chr(0x52) + chr(0x31) + chr(0x02) + chr(0x43) + chr(0x55)+ chr(0x52)+ chr(0x52)+chr(0x45)+chr(0x28)+chr(0x29)+chr(0x03)+chr(0x5A)
    # powerCoefCommand = chr(0x2F) + chr(0x3F) + chr(0x21) + chr(0x01) + chr(0x52) + chr(0x31) + chr(0x02) + chr(0x43) + chr(0x4f)+ chr(0x53)+ chr(0x5f)+chr(0x66)+chr(0x28)+chr(0x29)+chr(0x03)+chr(0x83)
    # powerCommand = chr(0x2F) + chr(0x3F) + chr(0x21) + chr(0x01) + chr(0x52) + chr(0x31) + chr(0x02) + chr(0x50) + chr(0x4F)+ chr(0x57) + chr(0x50) + chr(0x50) + chr(0x28) + chr(0x29) + chr(0x03) + chr(0x6F)
    # totalCosumedPowerCommand = chr(0x2F) + chr(0x3F) + chr(0x21) + chr(0x01) + chr(0x52) + chr(0x31) + chr(0x02) + chr(0x50) + chr(0x4f)+ chr(0x57)+ chr(0x45)+chr(0x50)+chr(0x28)+chr(0x29)+chr(0x03)+chr(0x64)
    # numeratorPowerCommand = chr(0x2F) + chr(0x3F) + chr(0x21) + chr(0x01) + chr(0x52) + chr(0x31) + chr(0x02) + chr(0x45) + chr(0x54)+ chr(0x30)+ chr(0x50)+chr(0x45)+chr(0x28)+chr(0x29)+chr(0x03)+chr(0x37)
#message_command =chr(0x2F) + chr(0x3F) + chr(0x21) + chr(0x01) + chr(0x52) + chr(0x31) + chr(0x02) + chr(0x56) + chr(0x4F)+chr(0x4C)+chr(0x54)+ chr(0x41)+chr(0x28)+ chr(0x29)+chr(0x03)+chr(0x5F)
message_command_volt = chr(0x2F) + chr(0x3F) + chr(0x21) + chr(0x01) + chr(0x52) + chr(0x31) + chr(0x02) + chr(0x56) + chr(0x4F)+chr(0x4C)+chr(0x54)+ chr(0x41)+chr(0x28)+ chr(0x29)+chr(0x03)+chr(0x5F)
message_command_amp = chr(0x2F) + chr(0x3F) + chr(0x21) + chr(0x01) + chr(0x52) + chr(0x31) + chr(0x02) + chr(0x43) + chr(0x55)+ chr(0x52)+ chr(0x52)+chr(0x45)+chr(0x28)+chr(0x29)+chr(0x03)+chr(0x5A)

#print(message_command2)

class SerialProcess(multiprocessing.Process):
 
    def __init__(self, input_queue, output_queue, parity=PARITY, stopbits=STOPBITS, bytesize=BYTESIZE, baudrate=BAUDRATE, timeout=1):
        multiprocessing.Process.__init__(self, target=self.serial_con, args=(PORT, BAUDRATE, PARITY, STOPBITS, BYTESIZE, 1))
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.result = bytes()
        
        #self.sp = serial.Serial(PORT, parity=PARITY, stopbits=STOPBITS, bytesize=BYTESIZE, baudrate=BAUDRATE, timeout=1)
     
    def serial_con(self, PORT=PORT, baudrate=BAUDRATE, bytesize=BYTESIZE, parity=PARITY, stopbits=STOPBITS, timeout=1):
        self.ser = serial.Serial(PORT, baudrate, bytesize, parity, stopbits, timeout=1)
        self.save_ser(self.ser)
        
    def save_ser(self, obj=None):
        if obj:
            self.sp = obj
        else:
            return self.sp

    def close(self):
        self.sp.close()
 
    def writeSerial(self, data):
        #self.sp.open()
        if data == 'volt':
            #time.sleep(0.1)
            self.sp.write(message_command_volt.encode())
        elif data == 'amp':
            self.sp.write(message_command_amp.encode())
        elif data == 'none':
            pass
        else:
            sent_data = data.encode()
            print(self.sp)
            self.sp.write(sent_data)        
        
    def readSerial(self):
        #return self.sp.readline().replace("\n", "")
        print('reading')
        self.result = self.sp.read_until('+')
        #self.result = self.sp.read_all()
        print(len(self.result))
    
        #x = result.rstrip(b",.\/#-\\)-*&$!%^@+0123456789\\'\\(|{}\"")
        now = time.strftime("%Y/%m/%d %H:%M:%S")
        x = self.result[:-2]
        x += ('<br><br><b>received on:<b> '+now).encode()
        #result = self.sp.read(100)
        #print(x.decode())
        #print(result)
        return x
 
        
 
    def run(self):
        self.serial_con()
        self.sp = self.save_ser()
        #self.sp.flushInput()
        #print(dir(self.sp))
        while True:

            # look for incoming tornado request
            
            if not self.input_queue.empty():
                data = self.input_queue.get()
                #print('data incoming')
                # send it to the serial device
                #print(type(data.encode('ascii')))
                #self.sp.write(data.encode())
                self.writeSerial(data)
                print("writing to serial: ", data)
                #x = self.sp.readline().decode()
                #self.output_queue.put(x)
            # look for incoming serial data
            #print(self.sp.readline())
            #print(self.output_queue.get())
            #self.output_queue.put('response from console')
            #self.output_queue.put('response')
            #self.sp.open()
            if (self.sp.in_waiting > 0):
                response = self.readSerial()
                # send it back to tornado
                self.output_queue.put(response.decode())
                #print(self.output_queue)
            time.sleep(0.09)


#voltage commands for ec2
#chr(0x2F) + chr(0x3F) + chr(0x21) + chr(0x01) + chr(0x52) + chr(0x31) + chr(0x02) + chr(0x56) + chr(0x4F)+chr(0x4C)+chr(0x54)+ chr(0x41)+chr(0x28)+ chr(0x29)+chr(0x03)+chr(0x5F)
