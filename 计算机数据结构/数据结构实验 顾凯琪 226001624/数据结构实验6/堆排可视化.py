import random
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation

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
        yield arr
        yield from heapify(arr, n, largest)

def heap_sort(arr):
    n = len(arr)

    for i in range((n-2) // 4, -1, -1):
        yield from heapify(arr, n, i)

    for i in range(n - 1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i]
        yield arr
        yield from heapify(arr, i, 0)

# 初始化图表
fig, ax = plt.subplots()
ax.set_title('Heap Sort Visualization')

# 生成初始随机列表
num_elements = 20
random_numbers = [random.randint(0, 100) for _ in range(num_elements)]
bar_rects = ax.bar(range(len(random_numbers)), random_numbers, align='edge')

# 更新函数，用于动画
def update_fig(arr, rects):
    for rect, val in zip(rects, arr):
        rect.set_height(val)

# 创建动画
def heap_sort_animation():
    yield random_numbers
    yield from heap_sort(random_numbers)

anim = animation.FuncAnimation(fig, func=update_fig, fargs=(bar_rects,), frames=heap_sort_animation, repeat=False)

# 显示动画
plt.show()
