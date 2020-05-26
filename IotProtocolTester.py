import json
import os
import socket
import struct

class IotProtocolTester:

    # 结果存在一个3元组的数组的list（可以看做是一个数组）
    # 格式为：
    # 0号：项目名称 String
    # 1号：bit长度 int
    # 2号：数据类型 String int为整型数 float为单精度浮点 double为双精度浮点 str为字符串
    #       uint8_t     <->       B     标准长度1
    #       int8_t      <->       b     标准长度1
    #       char[1]     <->       c     标准长度1
    #       uint16_t    <->       H     标准长度2
    #       int16_t     <->       h     标准长度2
    #       uint8_t     <->       B
    #       uint8_t     <->       B
    #       uint8_t     <->       B
    #       uint8_t     <->       B
    #       uint8_t     <->       B
    #       uint8_t     <->       B

    pItems = list()
    
    # 格式为：
    # 0号：项目名称 String
    # 1号：bit起始
    # 2号：bit终止
    pItemBitFields = list()

    bitCnt = 0 # 这是一个统计各项所占位数的计数器，若bitCnt大于pLen*8, 则说明协议制定的有问题
    pLen = 0 # 这是从json读出得协议长度（以字节计数）

    def __init__(self, path,port):
        self.getJsonData(path)
        self.getProtocolInfoFromJson()
        if self.isProtocolLenValid() == False:
            print("FATAL! Protocol Length is less than sum of item length")
            exit()
        self.getItemBitFields()
        pass

    def getJsonData(self,path): 
        jsonText = open(path).read() # 打开json文件并读取所有内容到 jsonText
        self.jsonData = json.loads(jsonText) # 将Json项目名和值存入JsonData

    def getProtocolInfoFromJson(self):
        for i in self.jsonData:
            if i == "len_byte":
                self.pLen = self.jsonData[i]
                continue
            item = i
            bits,type = (str((self.jsonData[item])).split("+"))
            bits = int(bits)
            if  type == "int":
                self.pItems.append((item,bits,type,int(0)))
            elif type == "float":
                if bits != 32 :
                    self.pItems.append((item,bits,"TYPE LENGTH ERROR"))
                else:
                    self.pItems.append((item,bits,type))
            elif type == "double": # 一般Python中的Float就是双精度的
                if bits != 64 :
                    self.pItems.append((item,bits,"TYPE LENGTH ERROR"))
                else:
                    self.pItems.append((item,bits,type))
            elif type == "str":
                self.pItems.append((item,bits,type))
            else:
                self.pItems.append((item,bits,"TYPE ERROR"))
                
    def isProtocolLenValid(self):
        """
        判断协议总长度是否大于各个分项长度和
        """
        # 统计每个项目的bit长度和
        for item in self.pItems:
            self.bitCnt = self.bitCnt + item[1] #int(item[1])
        # 若bitCnt*8大于pLen, 则说明协议制定的有问题
        if (self.bitCnt > self.pLen * 8):
            return False
        else: 
            return True

    def getItemBitFields(self):
        bitPtr = 0
        for i in self.pItems:
            start = bitPtr
            bitPtr = bitPtr + i[1] # 加上项目长度
            self.pItemBitFields.append((i[0],start,bitPtr - 1))

    def updateHostIp(self):
        """
        查询本机ip地址
        :return: ip
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            self.hostIp = s.getsockname()[0]
        finally:
            s.close()
        return self.hostIp

iot = IotProtocolTester("demo.json",10086)

data = struct.pack('!Bf', 10, 35, 12, 13)



print(iot.pLen)
for i in iot.pItemBitFields:
    print(i)
    pass
    # # 打开json文件并读取所有内容到json_text
    # json_text= open("t.json").read()


    # data= json.loads(jsonText)
    # for i in data:
    #     print(i + " " + str(data[i]))
    #     pass
    # print (str((data["ID"])).split("+"))


    # def tr():
    #     return 7,8,9

    # a = list()
    # a.append((1,2,3))

    # a.append((4,5,6))
    # a.append(tr())
    # for i in a:
    #     print(i[0])
    #     pass