#include<iostream>
using namespace std;
// 递归函数 Count
// 功能：计算 n 个元素的错位排列（Derangement）的数量
// 错位排列：排列中没有任何一个元素出现在其原始位置
// 参数：n 表示元素的数量
// 返回值：n 个元素的错位排列的数量
int Count(int n) {
    // 递归终止条件
    if (n == 1 || n == 2)  // 当 n = 1或2 时，错位排列的数量为 n-1（因为唯一一个元素只能在其原始位置）
        return n-1;

    else 
        // 递归公式：D(n) = (n-1) * (D(n-1) + D(n-2))
        // D(n-1) 表示第 n 个元素与前面某个元素交换位置后的错位排列数
        // D(n-2) 表示第 n 个元素与前面某个元素交换位置后，另一个元素也交换位置的错位排列数
        return (n - 1) * (Count(n - 1) + Count(n - 2));
}
int main() {
    int n;
    // 循环读取输入的 n
    while (cin >> n) {
        // 调用 Count 函数计算错位排列的数量并输出
        cout << Count(n) << endl;
    }
    return 0;
}
