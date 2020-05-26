import json
import os
import socket

class IotProtocolTester:
    # 结果存在一个4元组的数组的list（可以看做是一个数组）
    # 格式为：
    # 0号：项目名称 String
    # 1号：bit长度 int
    # 2号：数据类型 String int为整型数 float为单精度浮点 double为双精度浮点 str为字符串
    # 3号: 解析出来的数据 String
    pItems = list()
    
    bitCnt = 0 # 这是一个统计各项所占位数的计数器，若bitCnt大于pLen*8, 则说明协议制定的有问题
    pLen = 0 # 这是从json读出得协议长度（以字节计数）

    def __init__(self, path):
        self.getJsonData(path)
        self.getProtocolInfoFromJson()
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
            bits,type = (str((self.jsonData[i])).split("+"))
            bits = int(bits)
            if  type == "int":
                self.pItems.append((item,bits,type,int(0)))
            elif type == "float":
                self.pItems.append((item,bits,type,float("inf")))    
            elif type == "double": # 一般Python中的Float就是双精度的
                self.pItems.append((item,bits,type,float("inf")))
            elif type == "str":
                self.pItems.append((item,bits,type,str("NULL")))
            else:
                self.pItems.append((item,bits,"TYPE ERROR",str("TYPE ERROR")))
                
    def isProtocolLenValid(self):
        """
        判断协议总长度是否大于各个分项长度和
        """
        # 统计每个项目的bit长度和
        for item in self.pItems:
            self.bitCnt = self.bitCnt + item[1] #int(item[1])
        # 若bitCnt*8大于pLen, 则说明协议制定的有问题
        return (self.bitCnt > self.pLen * 8)
        # if (self.bitCnt > self.pLen * 8):
        #     return False
        # else: 
        #     return True

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

iot = IotProtocolTester("p.json")
for i in iot.pItems:
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