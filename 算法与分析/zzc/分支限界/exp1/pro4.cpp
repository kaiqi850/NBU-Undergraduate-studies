#include<iostream> 
#include <cstring> 
using namespace std; 

int b[4][4]; // 定义一个4x4的整数数组b，用于存储当前灯的状态（0表示关，1表示开）
int a[4][4]; // 定义一个4x4的整数数组a，用于存储初始灯的状态
int c[4][4]; // 定义一个4x4的整数数组c，用于表示按下的开关的位置 

// set函数用于模拟按下某个灯的开关，改变相应位置及其上下左右灯的状态
void set(int x, int y) {
    b[x][y] = b[x][y] ^ 1; // 将灯x,y的状态取反（0变1，1变0）
    if (x - 1 >= 0) b[x - 1][y] = b[x - 1][y] ^ 1; // 上方灯状态取反
    if (x + 1 < 4) b[x + 1][y] = b[x + 1][y] ^ 1; // 下方灯状态取反
    if (y - 1 >= 0) b[x][y - 1] = b[x][y - 1] ^ 1; // 左方灯状态取反
    if (y + 1 < 4) b[x][y + 1] = b[x][y + 1] ^ 1; // 右方灯状态取反
}

// generate函数用于根据二进制数n生成一个4位的模式，存储在数组c的第一行，表示按下第一行的哪个开关 
void generate(int n) {
    for (int i = 0; i < 4; i++) {
        c[0][i] = n % 2; // 将n的最低位赋值给c[0][i]
        n = n / 2; // 右移n，为下一次循环准备
    }
}

int main() {
    int temp, min = 100000; 	// temp用于临时存储步数，min用于存储最小步数
    bool flag = false; 			// 标志变量，用于判断是否找到可行解
    char cc; 					// 用于存储输入的单个字符
    int j; 						// 循环变量
    // 读取输入，将字符转换为灯的开关状态
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            cin >> cc;
            if (cc == 'b')
                a[i][j] = 0; // 如果输入是'b'，则灯是关的
            else
                a[i][j] = 1; // 否则，灯是开的
        }
    }

    // 有四列，则第一行开关的按下方式有16种模式
    for (int n = 0; n < 16; n++) {
        // 从初始状态开始，复制a到b
        for (int i = 0; i < 4; i++) {
            for (int j = 0; j < 4; j++) {
                b[i][j] = a[i][j];
                c[i][j] = 0; // 初始化c数组
            }
        }
        // 生成目标模式，表示各个情况下按下第一行哪个开关 
        generate(n);	
        temp = 0; // 重置步数计数器
        // 根据c的第一行设置第一行的灯状态
        for (j = 0; j < 4; j++) {
            if (c[0][j] == 1) {		//若按下该开关 
                set(0, j);			//则对应b数组中的灯光状况发生变化 
                temp++; 			// 增加步数
            }
        }
        // 根据c的模式设置剩余行的灯状态
        for (int i = 1; i < 4; i++) {
            for (int j = 0; j < 4; j++) {
                if (b[i - 1][j] == 1) { // 如果上一行对应的灯是开的
                    set(i, j);			//则需要按下下一行开关 
                    c[i][j] = 1; 		// 标记c[i][j]为1，表示开关按下 
                    temp++; 			// 增加步数
                }
            }
        }
        // 检查最后一行是否所有灯都关闭
        for (j = 0; j < 4; j++) {
            if (b[3][j] == 1) break; // 如果有灯是开的，则退出循环
        }
        if (j >= 4) { // 如果所有灯都关闭，说明找到了一种可行的模式
            min = (min < temp) ? min : temp; // 更新最小步数
            flag = true; // 设置标志变量
        }
    }
    // 输出结果
    if (flag)
        cout << min << endl; // 如果找到了可行解，输出最小步数
    else
        cout << "Impossible" << endl; // 如果没有找到可行解，输出"Impossible"
    return 0;
}
