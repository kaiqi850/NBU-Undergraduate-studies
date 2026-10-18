#include <stdio.h>
#include <stdlib.h>

// 定义科学家结构体
typedef struct {
    int byear; // 出生年份
    int eyear; // 去世年份
} Scientist;

// 比较函数，用于排序
int compare(const void *a, const void *b) {
    Scientist *s1 = (Scientist *)a;
    Scientist *s2 = (Scientist *)b;
    return s1->byear - s2->byear;
}

int main() {
    int n; // 科学家数量
    scanf("%d", &n);

    Scientist scientists[n];

    // 输入科学家数据
    for (int i = 0; i < n; i++) {
        scanf("%d %d", &scientists[i].byear, &scientists[i].eyear);
    }

    // 按出生年份排序
    qsort(scientists, n, sizeof(Scientist), compare);

    // 初始化科学盛世的记录
    int maxCount = 0;     // 最大人数
    int startYear = 0;    // 科学盛世开始年
    int endYear = 0;      // 科学盛世结束年

    // 遍历科学家，计算每个时间段的重叠人数
    for (int i = 0; i < n; i++) {
        int count = 1; // 当前科学家自己
        int currentStart = scientists[i].byear;
        int currentEnd = scientists[i].eyear;

        for (int j = i + 1; j < n; j++) {
            if (scientists[j].byear <= currentEnd - 10) { // 存在交叉
                count++;
                if (scientists[j].eyear > currentEnd) {
                    currentEnd = scientists[j].eyear;
                }
            } else {
                break; // 超出范围，结束检查
            }
        }

        // 更新科学盛世信息
        if (count > maxCount) {
            maxCount = count;
            startYear = currentStart;
            endYear = currentEnd;
        }
    }

    // 输出科学盛世时间段
    printf("%d %d\n", startYear, endYear);

    return 0;
}
