import random
import time
import datetime


def swap(arr, i, j):
    temp = arr[i]
    arr[i] = arr[j]
    arr[j] = temp


def quick_sort(arr):
    if len(arr) == 0 or len(arr) == 1:
        return arr
    random_numbers2 = arr
    piovt_index = 0
    piovt = random_numbers2[piovt_index]
    i = 1
    j = len(arr) - 1
    while (i <= j):
        while i <= j and (random_numbers2[i] <= piovt):
            i += 1
        while i <= j and (random_numbers2[j] >= piovt):
            j -= 1
        if i <= j:
            swap(random_numbers2, i, j)

    swap(random_numbers2, piovt_index, j)
    return quick_sort(random_numbers2[:j]) + [piovt] + quick_sort(random_numbers2[j + 1:])


total_time = 0
for i in range(10):
    random_numbers = [random.randint(0, 2 ** 31 - 1) for _ in range(10000)]
    start_time = time.time()
    quick_sort(random_numbers)
    total_time += time.time() - start_time

print("快速排序十次平均时间：", total_time / 10)
