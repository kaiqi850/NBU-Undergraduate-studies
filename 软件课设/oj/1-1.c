#include <stdio.h>

#define MAX_SIZE 120

void flip(int arr[], int k) {
    for (int i = 0; i < k / 2; i++) {
        int temp = arr[i];
        arr[i] = arr[k - i - 1];
        arr[k - i - 1] = temp;
    }
}

int main() {
    int n;
    scanf("%d", &n);
    
    int arr[MAX_SIZE];
    
    for (int i = 0; i < n; i++) {
        scanf("%d", &arr[i]);
    }
    
    // 检查是否已经排序好了
    for (int i = 1; i < n; i++) {
        if (arr[i] < arr[i - 1]) {
            break;
        }
        if (i == n - 1) {
            // 已经排序好
            for (int i = 0; i < n; i++) {
                if (i == n - 1) {
                    printf("%d", arr[i]);
                } else {
                    printf("%d ", arr[i]);
                }
            }
            return 0;
        }
    }

    // 模拟翻饼过程
    for (int i = n - 1; i >= 1; i--) {
        // 找到当前未排序部分中的最大值
        int max_index = 0;
        for (int j = 1; j <= i; j++) {
            if (arr[j] > arr[max_index]) {
                max_index = j;
            }
        }
        
        if (max_index != i) {
            // 如果最大值不是在当前的最后位置，先把它翻到最上面
            if (max_index != 0) {
                flip(arr, max_index + 1); // 翻转到最上面
            }
            // 然后翻到正确位置
            flip(arr, i + 1); // 翻转到最后
        }
    }

    // 输出排序后的结果
    for (int i = 0; i < n; i++) {
        if (i == n - 1) {
            printf("%d", arr[i]);  // 最后一项没有空格
        } else {
            printf("%d ", arr[i]);  // 其他项后面有空格
        }
    }
    printf("\n");

    return 0;
}

