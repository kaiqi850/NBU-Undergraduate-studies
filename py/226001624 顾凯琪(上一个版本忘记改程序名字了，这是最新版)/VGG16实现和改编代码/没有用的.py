import math
import pandas as pd
import sys

# input1 = pd.read_excel("")
# print("hello world")  ###注释符号

PI = 3.14159
PI = PI * 2
# print(PI)  # 常量不变，提醒作用
# # print(input())
# print(1 // 2)
# print(type(int(input())))


# m,n = input().split()
# print(m,n)


# list1 = [1, 2, 5, 9, 78, 15]
# list2 = [8, 9, 4, 7]
# list3 = [[1, 2], 3]
# print(list1 + list2)
# print(list1*2)
# print(list1[0:2])
# print(list1[0:6:2])
# print(2 in list1)

# str1 = 'hijio'
# print(str1[1])
# str2 = "helpl"
# print(str2[4])
# print(str2[-2])
#
# print([1, 2] in list1)
# print([1,2] in list3)

# print('hello\\nworld')
# str1 = "dawdawf"
# str1[0] = 'f'

# str1 = 'da'
# str2 = 'aw'
# print(str1+str2)
# print(str2.join(str1))
#
# print('djawufb {1} daw {0}'.format('nafwj',15))

# print(list1[1:5])

# del list1[0]
# print(list1)
#
# list1.insert(1, 48)
# print(list1)
#
# print(list1[-5:-1])
#
# print(len(list1))
#
# tup1 = (1, 2, 3, 4, 5)
# # tup1[1] = 1
# print(type(tup1[0]))
#
# shot_id = [1, 2, 3]
# shot_zone_area = ['Right Side(R)', 'Left Side(L)', 'Left Side Center(LC)']
# match_dict = {}
# for key, value in zip(shot_id, shot_zone_area):
#     match_dict[key] = value
# print(match_dict)
#
# print(match_dict.get(1))
#
# student = {'Tom', 'Jim', 'Mary', 'Tom', 'Jack', 'Rose'}
# print(student)
# print(type(student))
#
# set1 = ["a", "b", "c", "d", "a"]
# for i,j in enumerate(set1):
#     print(i,j)

import sys


#
# s = input()
# strs = s[:s.find('#')]  # "以符号#结尾"
# for k in set([i for i in strs if i.isalnum() == False and i != '_']):
#     strs = strs.replace(k, ' ')  # 其它字符均认为是单词分隔符
# strs = strs.rstrip(' ').lower().split()  # 全部变小写
# print(type(strs))
# print(strs)
# counts = {}
# for i in strs:
#     k = i[:15]
#     if k not in counts:
#         counts[k] = 1
#     else:
#         counts[k] += 1
# # 词频递减的顺序，若有并列，则按递增字典序
# ans = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
# print(len(counts))
# print(type(ans))
# print(ans)
# for i in range(0, int(0.1 * len(counts))):
#     print(str(ans[i][1]) + ':' + ans[i][0])

def su(list1):
    list = (2, 3, 4)
    list1 = list1 + list
    return list1


list2 = (1, 2, 3)
list2 = su(list2)


# print(list2)


# def su(x,**b):
#     print(b)
#
# x1 = 1
# x2 = 2
# x3 = 3
# su(1,x1=1,x2=2,x3=3)

# def fibs(n):
#     result = [0, 1]
#     for i in range(n - 2):
#         result.append(result[-2] + result[-1])
#     return result
#
#
# print(fibs(5))
#
# a = [1,2,3]
# b= [2,3,4]
# c = [ 4,5,6,7]
#
# print(list(zip(a,b,c)))

# d={'blue':500,'red':100,'white':300}
# d1 = dict(zip(d.values(),d.keys()))
# print(d1)
# print(sys.path)

# list5 = [1,2,3,4]
# # print(dir(list5))

class su():
    im = 1
    name = 'aw'
    def __init__(self,age,name):
        self.__age = age
        su.name = name   # 区别self.name = name

    def __detect(self):
        sfa = 1
        print('dawda')

    def getName(self):
        return su.name


a = su(12,'daw')
print(a.name)
# print(a._su__age)
# a._su__detect()
# print(su(16,'faw').im)
# print(a.im)
# print(su.im)
b = su(15,'faw')
print(a.getName())
print(b.getName())
su.name = 'gr'    #  ????
print(a.getName())
print(b.getName())
a.name = 'faw'
print('awd'+a.name)
print(a.getName())
print(b.getName())


# class Father(object):
#     def __init__(self, name):
#         self.name = name
#         print("name: %s" % (self.name))
#
#     def getName(self):
#         return 'Father ' + self.name
#
#
# class Son(Father):
#     def __init__(self, name):
#         super(Son, self).__init__(name)  # 两种形式都可以
#         # Father.__init__(self, name)
#         print("hi")
#
#
#     def getName(self):
#         return 'Son ' + self.name
#
#
# if __name__ == '__main__':
#     son = Son('runoob')
#     print(son.getName())
