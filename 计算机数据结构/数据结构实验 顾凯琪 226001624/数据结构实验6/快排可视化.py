import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random

# 创建一个随机列表
num_bars = 20
data = random.sample(range(1, 100), num_bars)

# 快速排序算法
def quick_sort(data, low, high):
    if low < high:
        pivot_index = partition(data, low, high)
        yield data
        yield from quick_sort(data, low, pivot_index)
        yield from quick_sort(data, pivot_index + 1, high)

def partition(data, low, high):
    pivot = data[(low + high) // 2]
    i = low - 1
    j = high + 1
    while True:
        i += 1
        while data[i] < pivot:
            i += 1
        j -= 1
        while data[j] > pivot:
            j -= 1
        if i >= j:
            return j
        data[i], data[j] = data[j], data[i]

# 初始化图表
fig, ax = plt.subplots()
ax.set_title('Quick Sort Visualization')
bar_rects = ax.bar(range(len(data)), data, align='edge')
text = ax.text(0.02, 0.95, "", transform=ax.transAxes)

# 更新函数，用于动画
def update_fig(data, rects, iteration):
    for rect, val in zip(rects, data):
        rect.set_height(val)
    iteration_str = f'Iteration: {iteration+1}'
    text.set_text(iteration_str)

# 创建动画
anim = animation.FuncAnimation(fig, func=update_fig, fargs=(bar_rects, 0), frames=quick_sort(data, 0, len(data)-1), repeat=False)

# 显示动画
plt.show()
