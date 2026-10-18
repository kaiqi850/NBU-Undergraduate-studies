#include <iostream>
#include <algorithm>
using namespace std;

int dp[1001][11] = {};  

int main() {
    int n, loc, t, val, max_time = 0;
    cin >> n;

    while (n--) {
        cin >> loc >> t >> val;
        dp[t][loc] = val;
        max_time = max(max_time, t);
    }

    for (int i = max_time - 1; i >= 0; --i) {
        for (int j = 0; j <= 10; ++j) {
            int best_next = dp[i + 1][j];  // 不动
            if (j > 0) best_next = max(best_next, dp[i + 1][j - 1]);  // 左走
            if (j < 10) best_next = max(best_next, dp[i + 1][j + 1]); // 右走
            dp[i][j] += best_next;  
        }
    }

    cout << dp[0][5] << endl; 
    return 0;
}

