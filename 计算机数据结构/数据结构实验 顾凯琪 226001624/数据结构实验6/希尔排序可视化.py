import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random

# 生成20个随机数
num_bars = 20
data = random.sample(range(1, 100), num_bars)

# 希尔排序算法
def shell_sort(data):
    gap = len(data) // 2
    while gap > 0:
        for i in range(gap, len(data)):
            temp = data[i]
            j = i
            while j >= gap and data[j - gap] > temp:
                data[j] = data[j - gap]
                j -= gap
            data[j] = temp
            yield data
        gap //= 2

# 初始化图表
fig, ax = plt.subplots()
ax.set_title('Shell Sort Visualization')
bar_rects = ax.bar(range(len(data)), data, align='edge')
text = ax.text(0.02, 0.95, "", transform=ax.transAxes)

# 更新函数，用于动画
def update_fig(data, rects):
    for rect, val in zip(rects, data):
        rect.set_height(val)

# 创建动画
anim = animation.FuncAnimation(fig, func=update_fig, fargs=(bar_rects,), frames=shell_sort(data), repeat=False)

# 显示动画
plt.show()
