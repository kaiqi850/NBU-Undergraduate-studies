class Hamming():
    def __init__(self,data):
        self.data = data



    def hammingEncode(self):
        self.dataLen = len(self.data)
        self.r = 0
        while pow(2,self.r) - self.r < self.dataLen + 1:
            self.r += 1
        self.HammingLen = self.r + self.dataLen #求出插入校验码后的总长
        self.HammingData = [0] * self.HammingLen
        for i in range(self.r):
            self.HammingData[pow(2,i)-1] = 1#先默认校验位都设置为1
        dataIndex = 0
        for i in range(self.HammingLen):#插入数据
            if self.HammingData[i] == 0:
                self.HammingData[i] = self.data[dataIndex]
                dataIndex += 1
        #print(self.HammingData)
        for pn in range(1,self.r+1):#逐个计算校验位
            #pn所在位置
            pos = pow(2,(pn-1)) - 1
            temp = 0
            for pr in range(pos,self.HammingLen+1,pow(2,pn)):
                for i in range(pr,min(pr+pow(2,(pn-1)),self.HammingLen)):#疯狂异或
                    temp ^= self.HammingData[i]
            if temp == 1:
                self.HammingData[pos] = 0
        #print(self.HammingData)
        return self.HammingData