import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random

# 创建一个随机列表
num_bars = 20
data = random.sample(range(1, 100), num_bars)

# 冒泡排序算法
def bubble_sort(data):
    n = len(data)
    for i in range(n):
        for j in range(0, n-i-1):
            if data[j] > data[j+1]:
                data[j], data[j+1] = data[j+1], data[j]
                yield data

# 初始化图表
fig, ax = plt.subplots()
ax.set_title('Bubble Sort Visualization')
bar_rects = ax.bar(range(len(data)), data, align='edge')
text = ax.text(0.02, 0.95, "", transform=ax.transAxes)

# 更新函数，用于动画
def update_fig(data, rects, iteration):
    for rect, val in zip(rects, data):
        rect.set_height(val)
    iteration_str = f'Iteration: {iteration+1}'
    text.set_text(iteration_str)

# 创建动画
anim = animation.FuncAnimation(fig, func=update_fig, fargs=(bar_rects, 0), frames=bubble_sort(data), repeat=False)

# 显示动画
plt.show()
