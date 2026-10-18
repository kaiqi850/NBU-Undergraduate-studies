import random
import time


def counting_sort(arr, exp):
    n = len(arr)
    output = [0] * n
    count = [0] * 10

    for i in range(n):
        index = arr[i] // exp % 10
        count[index] += 1

    for i in range(1, 10):
        count[i] += count[i - 1]

    i = n - 1
    while i >= 0:
        index = arr[i] // exp % 10
        output[count[index] - 1] = arr[i]
        count[index] -= 1
        i -= 1

    for i in range(n):
        arr[i] = output[i]


def radix_sort(arr):
    maxnum = max(arr)
    exp = 1
    while maxnum // exp > 0:
        counting_sort(arr, exp)
        exp *= 10


total_time = 0
for i in range(10):
    random_numbers = [random.randint(0, 2 ** 31 - 1) for _ in range(10000)]
    start_time = time.time()
    radix_sort(random_numbers)
    total_time += time.time() - start_time

print("基数排序十次平均时间：", total_time / 10)
