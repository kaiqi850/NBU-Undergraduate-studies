import time
import random


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

    for i in range((n-2) // 4, -1, -1):
        heapify(arr, n, i)

    for i in range(n - 1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i]
        heapify(arr, i, 0)


total_time = 0
for i in range(10):
    random_numbers = [random.randint(0, 2 ** 31 - 1) for _ in range(10000)]
    # random_numbers = [random.randint(0, 2 ** 8 - 1) for _ in range(20)]
    start_time = time.time()
    heap_sort(random_numbers)
    total_time += time.time() - start_time

print("堆排十次平均时间:", total_time / 10)
