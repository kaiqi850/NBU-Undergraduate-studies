#include<iostream>
#include <iomanip> // 包含 setw 和 setfill 操纵符
using namespace std;

int a[1000][100] = {0}; // 定义一个二维数组a，用于存储数列的每一位，每列存储5位数字

// 函数fun用于计算数列的第n项
void fun(int n) {
    int i, q, j;
    a[0][99] = 1; // 第0项的最低位是1
    a[1][99] = 3; // 第1项的最低位是3

    // 从第2项开始计算
    for (i = 2; i < n; i++) {
        // 计算当前项的最低位
        j = a[i - 1][99] + 2 * a[i - 2][99];
        a[i][99] = j % 100000; // 取后5位存储到a[i][99]

        // 从倒数第二列开始，逐列计算高位
        for (q = 98; q >= 0; q--) {
            // 计算当前列的值，并加上来自低位的进位
            j = a[i - 1][q] + 2 * a[i - 2][q] + j / 100000;
            a[i][q] = j % 100000; // 取后5位存储到a[i][q]
        }
    }
}

int main() {
    int n;
    cin >> n; // 输入n，表示要计算数列的第n项

    int j, s = 0;
    fun(n); // 调用fun函数计算数列的第n项

    // 循环输出数列的第n-1项
    for (int j = 0; j < 100; j++) {
        if (a[n - 1][j] != 0 && s == 0) {
            // 第一个非零数字，不补零
            cout << a[n - 1][j];
            s = 1; // 标记已经输出了第一个非零数字
        } else if (s == 1) {
            // 后续数字，固定输出5位，不足5位的前面补零
            cout << setw(5) << setfill('0') << a[n - 1][j];
        }
    }
    cout << endl; // 输出换行
    return 0;
}
