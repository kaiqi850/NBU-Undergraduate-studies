#include <iostream>
#include <fstream>
using namespace std;

// 递归计算半数集的大小
int countSet(int n, int last) {
    int count = 1; // 计算自身
    for (int i = 1; i <= last / 2; ++i) {
        count += countSet(i * 10 + n, i); // 递归添加数字
    }
    return count;
}

int main() {
    
    int n;
    cin >> n; // 读取输入
    
    int result = countSet(n, n);
    cout << result << endl; // 写入输出
    
    return 0;
}

