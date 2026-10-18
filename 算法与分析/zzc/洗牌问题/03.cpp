#include <iostream>
#include <vector>
#include <random>
#include <ctime>
using namespace std;

// 定义一个生成随机数的类
class RandomNumber {
public:
    // 构造函数，如果不指定种子，就使用当前时间作为种子
    RandomNumber(unsigned long s = std::random_device{}()) {
        rng.seed(s);
    }

    // 生成范围在[0, n-1]之间的随机整数
    unsigned short Random(unsigned long n) {
        uniform_int_distribution<unsigned short> dist(0, n - 1);
        return dist(rng);
    }

private:
    mt19937 rng; // Mersenne Twister随机数生成器
};

// 定义一个皇后类
class Queen {
    friend bool nQueen(int); // 声明友元函数用于解决N皇后问题

private:
    bool Place(int k);      // 检查在第k列放置皇后是否会导致冲突
    bool Backtrack(int t);  // 使用回溯算法解决从第t列开始的N皇后问题
    bool QueensLV(int stopVegas); // 使用拉斯维加斯算法解决N皇后问题
    int n;                  // 皇后数量
    vector<int> x, y;       // x[i]表示放置在第i列的皇后所位于的行号

    // 私有构造函数，初始化皇后数量和x, y向量
    Queen(int n) : n(n), x(n + 1), y(n + 1) {}
};


// 检查在第 k 列放置皇后是否会导致冲突
bool Queen::Place(int k) {
    for (int j = 1; j < k; ++j) { // 遍历前面已经放置的皇后
        // 判断是否在同一对角线上或同一行有皇后，如果有返回false
        if (abs(k - j) == abs(x[j] - x[k]) || x[j] == x[k])
            return false;
    }
    return true; // 没有冲突，返回true
}


bool Queen::Backtrack(int t) {
    if (t > n) { // 如果已经放置了所有的皇后
        cout << "Solution found:" << endl; // 输出找到解决方案的消息
        for (int i = 1; i <= n; ++i) { // 遍历每一列
            for (int j = 1; j <= n; ++j) { // 遍历每一行
                cout << ((x[j] == i) ? "Q " : "- "); // 如果该位置有皇后则输出 "Q"，否则输出 "-"
            }
            cout << endl; // 换行
        }
        return true; // 返回找到解决方案
    }
    for (int i = 1; i <= n; ++i) { // 遍历当前列的每一行
        x[t] = i; // 尝试将皇后放置在当前列的第 i 行
        if (Place(t) && Backtrack(t + 1)) // 如果放置合法且成功解决剩余的皇后问题
            return true; // 返回找到解决方案
    }
    return false; // 没有找到解决方案
}


bool Queen::QueensLV(int stopVegas) {
    RandomNumber rnd;   // 创建一个随机数生成器对象
    int k = 1;          // 当前要放置的列号
    int count = 1;      // 有效的放置计数器

    // 迭代直到放置到stopVegas列或者没有有效放置
    while ((k <= stopVegas) && (count > 0)) {
        count = 0;

        // 尝试将皇后放置在第k列的每一行
        for (int i = 1; i <= n; ++i) {
            x[k] = i;
            // 如果不冲突，记录有效放置的位置
            if (Place(k))
                y[count++] = i;
        }

        // 如果有有效放置位置，从中随机选择一个放置皇后
        if (count > 0)
            x[k++] = y[rnd.Random(count)];
    }

    // 如果找到了有效的放置方案，调用回溯算法继续搜索剩余的皇后位置
    if (count > 0) {
        Backtrack(stopVegas + 1);
        return true;
    }

    // 如果没有找到有效的放置方案，返回false
    return false;
}


bool nQueen(int n) {
    Queen X(n); // 创建一个Queen对象，传入皇后数量

    int stop = (n > 15) ? n - 15 : 8; // 根据皇后数量确定拉斯维加斯算法停止的列数

    if (X.QueensLV(stop)) { // 使用拉斯维加斯算法放置皇后
        for (int i = 1; i <= n; ++i)
            cout << X.x[i] << " "; // 输出皇后的列数
        cout << endl;
        return true; // 返回找到解决方案
    }
    return false; // 没有找到解决方案
}


int main() {
    nQueen(8);
    cout << "Press Enter to exit...";
    cin.get();
    return 0;
}

