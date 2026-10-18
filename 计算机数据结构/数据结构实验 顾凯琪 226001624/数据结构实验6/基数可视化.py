import random
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation

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
    return arr

def radix_sort(arr):
    maxnum = max(arr)
    exp = 1
    while maxnum // exp > 0:
        arr = counting_sort(arr, exp)
        yield arr
        exp *= 10

# 初始化图表
fig, ax = plt.subplots()
ax.set_title('Radix Sort Visualization')

# 生成初始随机列表
num_elements = 20
random_numbers = [random.randint(0, 100) for _ in range(num_elements)]
bar_rects = ax.bar(range(len(random_numbers)), random_numbers, align='edge')

# 更新函数，用于动画
def update_fig(data):
    for rect, val in zip(bar_rects, data):
        rect.set_height(val)

# 创建动画
def radix_sort_animation():
    yield random_numbers
    yield from radix_sort(random_numbers)

anim = animation.FuncAnimation(fig, func=update_fig, frames=radix_sort_animation, repeat=False)

# 显示动画
plt.show()
