import random
import time
import datetime
import copy


def swap(arr, i, j):
    temp = arr[i]
    arr[i] = arr[j]
    arr[j] = temp


def bubble_sort(random_numbers1):
    for i in range(len(random_numbers1)):
        for j in range(len(random_numbers1) - i - 1):
            if random_numbers1[j] > random_numbers1[j + 1]:
                swap(random_numbers1, j, j + 1)


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


def insert_sort(arr, start, gap):
    for i in range(start + gap, len(arr), gap):
        position = i
        while position >= gap and arr[position] < arr[position - gap]:
            arr[position], arr[position - gap] = arr[position - gap], arr[position]
            position -= gap


def shell_sort(random_numbers):
    for var in var_list:
        for i in range(var):
            insert_sort(random_numbers, i, var)


def merge_sort(arr, first, last):
    if first < last:
        mid1 = first + (last - first) // 4
        mid2 = first + 2 * (last - first) // 4
        mid3 = first + 3 * (last - first) // 4

        merge_sort(arr, first, mid1)
        merge_sort(arr, mid1 + 1, mid2)
        merge_sort(arr, mid2 + 1, mid3)
        merge_sort(arr, mid3 + 1, last)

        merge(arr, first, mid1, mid2, mid3, last)


def merge(arr, first, mid1, mid2, mid3, last):
    left_arr = arr[first:mid1 + 1]
    mid1_arr = arr[mid1 + 1:mid2 + 1]
    mid2_arr = arr[mid2 + 1:mid3 + 1]
    mid3_arr = arr[mid3 + 1:last + 1]

    left_arr.append(float('inf'))
    mid1_arr.append(float('inf'))
    mid2_arr.append(float('inf'))
    mid3_arr.append(float('inf'))

    i = j = k = l = 0

    for m in range(first, last + 1):
        if left_arr[i] <= mid1_arr[j] and left_arr[i] <= mid2_arr[k] and left_arr[i] <= mid3_arr[l]:
            arr[m] = left_arr[i]
            i += 1
        elif mid1_arr[j] <= left_arr[i] and mid1_arr[j] <= mid2_arr[k] and mid1_arr[j] <= mid3_arr[l]:
            arr[m] = mid1_arr[j]
            j += 1
        elif mid2_arr[k] <= left_arr[i] and mid2_arr[k] <= mid1_arr[j] and mid2_arr[k] <= mid3_arr[l]:
            arr[m] = mid2_arr[k]
            k += 1
        else:
            arr[m] = mid3_arr[l]
            l += 1


def heapify(arr, n, i):
    largest = i
    left = 4 * i + 1
    mid1 = 4 * i + 2
    mid2 = 4 * i + 3
    right = 4 * i + 4

    if left < n and arr[left] > arr[largest]:
        largest = left

    if mid1 < n and arr[mid1] > arr[largest]:
        largest = mid1

    if mid2 < n and arr[mid2] > arr[largest]:
        largest = mid2

    if right < n and arr[right] > arr[largest]:
        largest = right

    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]
        heapify(arr, n, largest)


def heap_sort(arr):
    n = len(arr)

    for i in range((n - 2) // 4, -1, -1):
        heapify(arr, n, i)

    for i in range(n - 1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i]
        heapify(arr, i, 0)


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


# var_list = [1, 3, 7, 15, 31, 63, 127, 255, 511, 1023, 2047, 4095]      #10000
# var_list= [1, 3, 7, 15, 31, 63, 127, 255, 511] #1000
var_list = [1, 3, 7, 15, 31, 63, 127, 255, 511, 1023, 2047, 4095, 8191]
var_list.reverse()

random_numbers = [random.randint(0, 2 ** 31 - 1) for _ in range(100000)]
# 冒泡排序
bubble_numbers = copy.copy(random_numbers)
start_time = time.time()
bubble_sort(bubble_numbers)
end_time = time.time() - start_time
print("冒泡排序十次平均时间：", end_time)

# 快速排序
quick_numbers = copy.copy(random_numbers)
start_time = time.time()
quick_sort(quick_numbers)
end_time = time.time() - start_time
print("快速排序十次平均时间：", end_time)

# 希尔排序
shell_numbers = copy.copy(random_numbers)
start_time = time.time()
shell_sort(shell_numbers)
end_time = time.time() - start_time
print("希尔排序十次平均时间：", end_time)

# 归并排序
merge_numbers = copy.copy(random_numbers)
start_time = time.time()
merge_sort(random_numbers, 0, len(random_numbers) - 1)
end_time = time.time() - start_time
print("归并排序十次平均时间：", end_time)

# 堆排序
heap_numbers = copy.copy(random_numbers)
start_time = time.time()
heap_sort(heap_numbers)
end_time = time.time() - start_time
print("堆排序 十次平均时间：", end_time)

# 基数排序
radix_numbers = copy.copy(random_numbers)
start_time = time.time()
radix_sort(radix_numbers)
end_time = time.time() - start_time
print("基数排序十次平均时间：", end_time)
