import random
import time


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


total_time = 0
for i in range(10):
    random_numbers = [random.randint(0, 2 ** 31 - 1) for _ in range(10000)]
    start_time = time.time()
    merge_sort(random_numbers, 0, len(random_numbers) - 1)
    total_time += time.time() - start_time

print("四分归并排序十次平均时间：", total_time / 10)
