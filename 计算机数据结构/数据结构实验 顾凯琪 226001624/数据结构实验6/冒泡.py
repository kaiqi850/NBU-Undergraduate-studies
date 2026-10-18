import random
import time


def swap(arr, i, j):
    temp = arr[i]
    arr[i] = arr[j]
    arr[j] = temp


def bubble_sort():
    for i in range(len(random_numbers1)):
        for j in range(len(random_numbers1) - i - 1):
            if random_numbers1[j] > random_numbers1[j + 1]:
                swap(random_numbers1, j, j + 1)



total_time = 0
for i in range(10):
    random_numbers1 = [random.randint(0, 2 ** 31 - 1) for _ in range(10000)]
    start_time = time.time()
    bubble_sort()
    total_time += time.time() - start_time

print("冒泡排序十次平均时间：", total_time / 10)
