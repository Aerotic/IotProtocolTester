import json
import os
import socket
import struct

class IotProtocolTester:

    # 结果存在一个3元组的数组的list（list可以看做是一个数组）
    # 格式为：
    # 0号：项目名称 String
    # 1号：bit长度 int
    # 2号: 起始地址
    # 3号：数据类型 String int为整型数 float为单精度浮点 double为双精度浮点 str为字符串
    #       uint8_t     <->       B     标准长度1
    #       int8_t      <->       b     标准长度1
    #       char[1]     <->       c     标准长度1  实际就是长度为1的字符串
    #       uint16_t    <->       H     标准长度2
    #       int16_t     <->       h     标准长度2
    #       uint32_t    <->       I     标准长度4
    #       int32_t     <->       i     标准长度4
    #       uint64_t    <->       Q     标准长度8
    #       int64_t     <->       q     标准长度8
    #       float       <->       f     标准长度4
    #       double      <->       d     标准长度8
    #       char[]      <->       s     标准长度
    #       uint8_t     <->       B     标准长度
    pItems = list()

    #
    pItemsData = list()

    # struct.pack unpack所需的格式解析字符串
    pFmtStr = '!'

    # 格式为：
    # 0号：项目名称 String
    # 1号：bit起始
    # 2号：bit终止
    pItemBitFields = list()
    

    
    byteCnt = 0 # 这是一个统计各项所占字节数的计数器
    pLen = 0 # 这是从json读出得协议长度（以字节计数）

    def __init__(self, path,port):
        self.getJsonData(path)
        self.getProtocolInfoFromJson()
        # if self.isProtocolLenValid() == False:
        #     print("FATAL! Protocol Length is less than sum of item length")
        #     exit()
        # self.getItemBitFields()
        pass

    def getJsonData(self,path):
        # 打开json文件并读取所有内容到 jsonText
        jsonText = open(path).read()
        # 将Json项目名和值存入JsonData
        self.jsonData = json.loads(jsonText) 

    def getProtocolInfoFromJson(self):
        self.byteCnt = 0
        for i in self.jsonData:

            
            # 名称
            item = i 

            # 更新格式字符串
            self.pFmtStr = self.pFmtStr + str(self.jsonData[item]) 

            # 获取长度和起始地址，更新字节计数器
            if len(str(self.jsonData[item])) == 1:
                byte_len = 1;
                type = str(self.jsonData[item])[0]
            else:
                byte_len = int(str(self.jsonData[item])[0])
                type = str(self.jsonData[item])[1]
            
            #以格式串“b4sb” 数据(12,'0000',3)为例
            # 在struct.unpack后，“3”的位置在返回的元组得2号位置而非4号位置
            if type == 's':
                byte_len = 1

            startAddr = self.byteCnt
            self.byteCnt = self.byteCnt + byte_len

            # 获取类型
            typeStr = 'Not Initialized'
            #       uint8_t     <->       B     标准长度1
            #       int8_t      <->       b     标准长度1
            #       char[1]     <->       c     标准长度1  实际就是长度为1的字符串
            #       uint16_t    <->       H     标准长度2
            #       int16_t     <->       h     标准长度2
            #       uint32_t    <->       I     标准长度4
            #       int32_t     <->       i     标准长度4
            #       uint64_t    <->       Q     标准长度8
            #       int64_t     <->       q     标准长度8
            #       float       <->       f     标准长度4
            #       double      <->       d     标准长度8
            #       char[]      <->       s     标准长度
            if  type == "B":
                typeStr = 'uint8_t'
            elif type == "b":
                typeStr = 'int8_t'
            elif type == "c":
                typeStr = 'char[1]'
            elif type == "H":
                typeStr = 'uint16_t'
                 
            elif type == "h":
                typeStr = 'int16_t'
                 
            elif type == "I":
                typeStr = 'uint32_t'
                 
            elif type == "i":
                typeStr = 'int32_t'
                 
            elif type == "Q":
                typeStr = 'uint64_t'
                 
            elif type == "q":
                typeStr = 'int64_t'
                 
            elif type == "b":
                typeStr = 'int8_t'
                 
            elif type == "f":
                typeStr = 'float'
                 
            elif type == "d":
                typeStr = 'double'
                 
            elif type == "s":
                typeStr = 'char[]'
                 
            else:
                typeStr = "TYPE ERROR"
            # 更新项目名称，起始地址，长度，类型
            self.pItems.append((item,startAddr,byte_len,typeStr))
        
        # 更新协议长度
        self.pLen = self.byteCnt

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


    def unpack(self,dat):
        tup = tuple() # struct.unpack返回值为元组，故用一个元组中转一下
        tup = struct.unpack(self.pFmtStr,dat)
        for i in self.pItems:
            start = i[1]
            end = start + i[2]
            
            if i[3] == 'char[]':
                tmp = str(tup[start], encoding = "utf8") # 字符串无论多长都是按照元组的一个元素计算，故用起始位提取即可
                iData = tmp.rstrip('\x00') # 此步为了去除尾部占位的‘\x00’
                # 字符串尾部特意加‘\x00’的吔屎去
            elif i[2] == 1: # 处理非字符串，单个元素的情况
                iData = list(tup[start:end]).pop()
            else: # 处理非字符串，有多个元素的数组的情况
                iData = list(tup[start:end])
            self.pItemsData.append(i.__add__((iData,)))
        

    def funcname(self, parameter_list):
        pass
iot = IotProtocolTester("demo.json",10086)
print(iot.pFmtStr)
for i in iot.pItems:
    print(">>>",i)
    pass

# 名，类型，长度，起始地址


tri = tuple()
fmt = '!B2f4B5sB'
data = struct.pack(fmt, 5, 2.333,6.66,10, 35, 12, 13, bytes('12'.encode('utf-8')), 13)
# print(str(data))
# arr=(1,2,3,4)
tri = struct.unpack(fmt,data)
print(tri[8])
print("-------------------------")
iot.unpack(data)
for iD in iot.pItemsData:
    print(iD)
    print(type(iD[4]))
    pass
# print(tri)
# l = list(tri[1:])
# print(l)

# print(data[4])
# print(data[5])
# print(data[6])
# print(data[7])
# # data[7] = '\0'
# print(data[8])
# print(l)
# print(len('4B'))
# # print(str(l, encoding = "utf-8"))
# # for i in tri:
    
#     pass
# print(iot.pLen)

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