#include <stdio.h>
#include <stdlib.h>

#define MAX_SIZE 6

int n;
int board[MAX_SIZE][MAX_SIZE];
int visited[MAX_SIZE][MAX_SIZE];

// 定义四个方向：上、下、左、右
int directions[4][2] = {{-1, 0}, {1, 0}, {0, -1}, {0, 1}};

// 判断坐标是否在有效范围内
int is_valid(int x, int y) {
    return x >= 0 && x < MAX_SIZE && y >= 0 && y < MAX_SIZE;
}

// DFS 寻找连通的相同图案
void dfs(int x, int y, int val, int *count, int positions[MAX_SIZE * MAX_SIZE][2]) {
    // 标记当前节点已访问
    visited[x][y] = 1;
    // 记录该图案的位置
    positions[*count][0] = x;
    positions[*count][1] = y;
    (*count)++;

    // 向四个方向扩展
    for (int i = 0; i < 4; i++) {
        int new_x = x + directions[i][0];
        int new_y = y + directions[i][1];

        if (is_valid(new_x, new_y) && !visited[new_x][new_y] && board[new_x][new_y] == val) {
            dfs(new_x, new_y, val, count, positions);
        }
    }
}

// 消除符合条件的图案
int eliminate() {
    int eliminated = 0;
    
    // 重置访问标记
    for (int i = 0; i < MAX_SIZE; i++) {
        for (int j = 0; j < MAX_SIZE; j++) {
            visited[i][j] = 0;
        }
    }

    // 扫描整个矩阵
    for (int i = 0; i < MAX_SIZE; i++) {
        for (int j = 0; j < MAX_SIZE; j++) {
            if (board[i][j] != 0 && !visited[i][j]) {
                int positions[MAX_SIZE * MAX_SIZE][2];  // 记录当前连通图案的位置
                int count = 0;
                int val = board[i][j];
                
                // 从当前未访问节点开始 DFS
                dfs(i, j, val, &count, positions);

                // 如果找到的相同图案个数 >= n，则消除这些图案
                if (count >= n) {
                    for (int k = 0; k < count; k++) {
                        int x = positions[k][0];
                        int y = positions[k][1];
                        board[x][y] = 0;  // 将这些位置标记为消除
                    }
                    eliminated = 1;  // 标记发生了消除
                }
            }
        }
    }

    return eliminated;
}

// 打印当前矩阵状态
void print_board() {
    for (int i = 0; i < MAX_SIZE; i++) {
        for (int j = 0; j < MAX_SIZE; j++) {
            if (board[i][j] == 0) {
                printf("0");
            } else {
                printf("%d", board[i][j]);
            }
            // 在每行的最后一个元素后面不加空格
            if (j != MAX_SIZE - 1) {
                printf(" ");
            }
        }
        printf("\n");
    }
}

int main() {
    // 输入数据
    scanf("%d", &n);

    // 读取6x6矩阵
    for (int i = 0; i < MAX_SIZE; i++) {
        for (int j = 0; j < MAX_SIZE; j++) {
            char c;
            scanf(" %c", &c);
            if (c == '#') {
                board[i][j] = 0;  // 无图案用0表示
            } else {
                board[i][j] = c - '0';  // 图案是数字字符，转换为整数
            }
        }
    }

    // 进行消除操作，直到没有更多消除
    while (eliminate()) {
        // 每次消除后输出当前的状态
    }

    // 如果最后有任何图案未消除，输出“yes”
    int success = 1;
    for (int i = 0; i < MAX_SIZE; i++) {
        for (int j = 0; j < MAX_SIZE; j++) {
            if (board[i][j] != 0) {
                success = 0;  // 如果有任何图案未消除
                break;
            }
        }
    }

    if (success) {
        printf("yes\n");
    } else {
        print_board();
    }

    return 0;
}
