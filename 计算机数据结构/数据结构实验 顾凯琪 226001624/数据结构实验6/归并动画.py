import random
import time
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random


# 四分归并排序算法
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


# 归并函数
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


# 初始化图表
fig, ax = plt.subplots()

# 生成初始随机列表
num_elements = 20
random_numbers = [random.randint(0, 100) for _ in range(num_elements)]

# 绘制初始状态
bar_rects = ax.bar(range(len(random_numbers)), random_numbers, align='edge')
ax.set_title('Four-way Merge Sort Visualization')


# 更新函数，用于动画
def update_fig(arr, rects):
    for rect, val in zip(rects, arr):
        rect.set_height(val)


# 创建动画
def merge_sort_animation():
    for first in range(len(random_numbers)):
        yield random_numbers
    merge_sort(random_numbers, 0, len(random_numbers) - 1)
    yield random_numbers


anim = animation.FuncAnimation(fig, func=update_fig, fargs=(bar_rects,), frames=merge_sort_animation, repeat=False)

# 显示动画
plt.show()
