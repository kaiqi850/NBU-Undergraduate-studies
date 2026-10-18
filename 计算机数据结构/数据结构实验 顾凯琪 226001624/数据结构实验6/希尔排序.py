import random
import time
import datetime

# 生成10000个随机数
random_numbers = [random.randint(0, 2 ** 31 - 1) for _ in range(10000)]
var_list = [1, 3, 7, 15, 31, 63, 127, 255, 511, 1023, 2047, 4095]
var_list.reverse()


def insert_sort(arr, start, gap):
    for i in range(start + gap, len(arr), gap):
        position = i
        while position >= gap and arr[position] < arr[position - gap]:
            arr[position], arr[position - gap] = arr[position - gap], arr[position]
            position -= gap


def shell_sort():
    for var in var_list:
        for i in range(var):
            insert_sort(random_numbers, i, var)


total_time = 0
for i in range(10):
    random_numbers = [random.randint(0, 2 ** 31 - 1) for _ in range(10000)]
    start_time = time.time()
    shell_sort()
    total_time += time.time() - start_time

print("希尔排序十次平均时间：", total_time / 10)
