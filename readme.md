在tcp通信中似乎少见跨字节位域拼接的传输方式，故本工具最小计量单位为Byte


所以使用struct.pack unpack即可完成协议解析，但转换出来的数据仍需要手动赋值到指定类型的变量才能正常查看，
所以还是希望以json为协议格式的载体，自动化接收数据并完成协议的解析

后续希望在字符串处理的层面上加点东西，使得能识别出来各种类型的数组