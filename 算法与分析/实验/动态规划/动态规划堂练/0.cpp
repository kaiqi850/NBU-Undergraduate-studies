


#include <bits/stdc++.h>
using namespace std;
int main() {
    int n;
    cin >> n;

    vector<int> p = {0, 1, 5, 8, 10, 13, 17, 18, 22, 25, 30};

    vector<int> dp(n + 1, 0);

    for (int i = 1; i <= n; ++i) {
        for (int j = 1; j <= i && j < p.size(); ++j) {
            dp[i] = max(dp[i], p[j] + dp[i - j]);
        }
    }

    cout << dp[n] << endl;
    return 0;
}

