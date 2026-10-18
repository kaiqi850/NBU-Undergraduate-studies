/*
整数N（课程数<100）和整数M（天数<100）；
后面是i=1..N行数据，每行j=1..M个数据；
第i行数据表示第i门课，花费j天的时间获得的预期成绩。
一个整数，表示最大预期总成绩。
*/

#include <iostream>
#include <cstring>
#include<algorithm>
using namespace std;


int main() {
    int N, M;
    int dp[105];
    int score[105][105];

    while (cin >> N >> M && N != 0 && M != 0) {
        memset(dp, 0, sizeof(dp));

        for (int i = 1; i <= N; i++) { // 课程数
            for (int j = 1; j <= M; j++) { // 天数
                cin >> score[i][j];
            }
        }

        for (int i = 1; i <= N; i++) { // 遍历每门课程
            for (int j = M; j >= 1; j--) { // 背包容量，即剩余天数
                for (int k = 1; k <= j; k++) { // 当前课程花费的天数
                    dp[j] = max(dp[j], dp[j - k] + score[i][k]);
                }
            }
        }

        cout << dp[M] << endl;
    }

    return 0;
}
