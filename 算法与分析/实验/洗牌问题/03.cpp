#include <iostream>
#include <vector>
#include <random>
#include <ctime>
using namespace std;

// 随机数生成器类
class RandomNumber {
public:
    RandomNumber(unsigned long s = std::random_device{}()) {
        rng.seed(s);
    }

    unsigned short Random(unsigned long n) {
        uniform_int_distribution<unsigned short> dist(0, n - 1);
        return dist(rng);
    }

private:
    mt19937 rng;
};

class Queen {
    friend bool nQueen(int); // 声明友元函数

private:
    int n;
    vector<int> x, y;

    Queen(int n) : n(n), x(n + 1), y(n + 1) {}

    // 检查在第 k 列放置皇后是否合法
    bool Place(int k) {
        for (int j = 1; j < k; ++j) {
            if (abs(k - j) == abs(x[k] - x[j]) || x[k] == x[j])
                return false;
        }
        return true;
    }

    // 回溯补全，从第 t 列开始
    bool Backtrack(int t) {
        if (t > n) {
            PrintSolution();
            return true;
        }
        for (int i = 1; i <= n; ++i) {
            x[t] = i;
            if (Place(t) && Backtrack(t + 1))
                return true;
        }
        return false;
    }

    // 拉斯维加斯阶段：随机放置前 stopVegas 列
    bool QueensLV(int stopVegas) {
        RandomNumber rnd;
        int k = 1;
        int count = 1;

        // 只做 stopVegas 列的随机放置
        while ((k <= stopVegas) && (count > 0)) {
            count = 0;
            for (int i = 1; i <= n; ++i) {
                x[k] = i;
                if (Place(k))
                    y[count++] = i;
            }
            if (count > 0)
                x[k++] = y[rnd.Random(count)];
        }

        // 如果前 stopVegas 列成功放置，则用回溯补全剩余列
        if (count > 0)
            return Backtrack(k);
        return false;
    }

    // 打印棋盘解
    void PrintSolution() {
        cout << "One solution:\n";
        for (int i = 1; i <= n; ++i) {
            for (int j = 1; j <= n; ++j) {
                cout << (x[j] == i ? "Q " : "- ");
            }
            cout << endl;
        }
        cout << endl;
    }
};

// n 皇后主函数：尝试一次 Las Vegas+回溯，失败时返回 false
bool nQueen(int n) {
    Queen Q(n);
    int stop = (n > 15) ? n - 15 : 8;
    return Q.QueensLV(stop);
}

int main() {
    int n = 8;
    bool found = false;

    // 一直循环，直到找出解
    while (!found) {
        found = nQueen(n);
    }

    cout << "Press Enter to exit...";
    cin.get(); // 等待用户按下 Enter
    return 0;
}

